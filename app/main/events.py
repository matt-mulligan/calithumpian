from collections import OrderedDict

from flask import request
from flask_socketio import emit

from .game import Calithumpian
from .. import socketio
from ..main import html_builder
from app import __version__

HTML_TAG_PARAGRAPH = "p"

GAME = Calithumpian()

PLAYERS = OrderedDict()


# --- INCOMING EVENTS --------------------
@socketio.on("connect")
def event_connect():
    client_address = f"{request.remote_addr}:{request.environ['REMOTE_PORT']}"
    print(f"client {request.sid} connected from {client_address}")
    emit("update_version", {"version": __version__.VERSION})


@socketio.on("join_game")
def event_join_game():
    message = html_builder.build_text_tag(HTML_TAG_PARAGRAPH, "SYSTEM: Please provide a player name")
    emit('identify', {"action": "identify_client", "message": message}, room=request.sid)


@socketio.on("reset_game")
def event_reset_game():
    print("INSIDE RESET!")
    for player in PLAYERS.keys():
        print(f"PLAYER IS {player}")
        del PLAYERS[player]
    emit("reset_all_assets", broadcast=True)

    # # stop current iteration of game
    print("Killing game loop")
    GAME.kill_game()

    # remove all players from player list
    update_players_list()

    update_action(["Welcome to calithumpian", "please click 'join game' button above"])


@socketio.on("disconnect")
def event_disconnect():
    print(f"Player {request.sid} left :(")
    player = get_player_name_from_sid(request.sid)
    message = html_builder.build_text_tag(HTML_TAG_PARAGRAPH, f"SYSTEM: player {player} has left the game :(")
    message_player_chat(message, all=True)
    del PLAYERS[player]
    update_players_list()


@socketio.on("client_identify")
def event_client_identify(data):
    sid = request.sid
    if data["player_name"] not in PLAYERS.keys():

        # Send Message to new Player
        message = html_builder.build_text_tag(HTML_TAG_PARAGRAPH, f"SYSTEM: Welcome to the game {data['player_name']}")
        emit("identify", {"action": "identify_accepted", "message": message})

        # Send Message to all players
        message = html_builder.build_text_tag(HTML_TAG_PARAGRAPH,
                                              f"SYSTEM: New Player {data['player_name']} has entered the game!")
        message_player_chat(message, all=True)

        # Register Player
        PLAYERS[data["player_name"]] = {"sid": sid}
        print(f"Player '{data['player_name']}' has joined the game!")

        # update all client score tables
        update_score_table(PLAYERS.keys())

        # Update Player List
        update_players_list()

    else:
        print("duplicate player name found! Requesting a new name")
        message = html_builder.build_text_tag(HTML_TAG_PARAGRAPH,
                                                      f"SYSTEM: The player name given is already in the game, please choose again")
        emit("identify", {"action": "identify_duplicate", "message": message})


@socketio.on("client_chat")
def event_client_chat(data):
    player = get_player_name_from_sid(request.sid)
    message = html_builder.build_text_tag(HTML_TAG_PARAGRAPH, f"{player}: {data['message']}")
    print(f"Player {request.sid} sent message {data['message']} to player chat.")
    message_player_chat(message, all=True)


@socketio.on("client_start_game")
def event_start_game(data):
    GAME.play(PLAYERS)


@socketio.on("bet_response")
def event_bet_response(data):
    player = get_player_name_from_sid(request.sid)
    try:
        bet = int(data['bet'])
        GAME.set_player_bet(player, {"bet": bet, "wins": 0})
    except ValueError:
        print(f"player has passed back bad bet value '{data['bet']}', sending new bet emit")
        message = "Bad bet value received :(  bet values should be integers, and if your smart, " \
                  "equal to or lower to the number of tricks in the round."
        emit("bet", {"message": message})


@socketio.on("play_card_response")
def event_played_card_response(data):
    player = get_player_name_from_sid(request.sid)
    if player == GAME.get_player_turn():
        if not GAME.check_legal_move(player, data["img_path"]):
            message = "ILLEGAL MOVE! if you have a card of the same suit as the lead suit you must play it. " \
                      "please pick again."
            emit("play_card", {"message": message}, room=request.sid)
        else:
            GAME.add_card_to_played_cards(player, data["img_path"])
            print(f"CARD ADDED TO PLAYED CARD FOR {player}")


# --- OUTGOING EVENTS --------------------
def update_player_cards(player_name, player_sid, card_imgs):
    """
    emits to a specific client what there card images should be
    :param player_name:
    :param player_sid:
    :param card_imgs:
    :return:
    """
    print(f"SENDING CARDS TO PLAYER {player_name} as sid {player_sid}")
    emit("update_player_cards", {"cards": card_imgs}, room=player_sid)


def get_player_bet(player_sid, round, trump):
    """
    outgoing event for play to bet tricks
    :param player_sid:
    :param round:
    :param trump:
    :return:
    """
    message = f"Please enter the number of tricks you wish to bet this round. " \
              f"We are in Round {round} and the trump suit is {trump}"
    emit("bet", {"action": "place_bet", "message": message}, room=player_sid)


# -- HELPERS --------------------
def get_player_name_from_sid(sid):
    """
    Gets the player name from the SID given
    :param sid:
    :return:
    """

    for name, info in PLAYERS.items():
        if info["sid"] == sid:
            return name


def message_player_chat(message, all=True, client=None):
    """
    this helper message simplifies adding messages to the player_chat
    :param message:
    :param all:
    :return:
    """

    emit(
        "update_element",
        {
            "target": "player_chat",
            "target_type": "div",
            "action": "append",
            "message": message
        },
        broadcast=all
    )


def update_players_list():
    """
    this method will trigger an update of the players list
    :return:
    """

    emit("update_element",
         {
             "target": "player_list",
             "target_type": "list",
             "action": "overwrite",
             "message": list(PLAYERS.keys())
         },
         broadcast=True)


def update_action(action_message):
    """
    this method will trigger an update of the players list
    :return:
    """

    if not isinstance(action_message, list):
        action_message = [action_message]

    emit("update_element",
         {
             "target": "play_action_txt",
             "target_type": "list",
             "action": "overwrite",
             "message": action_message
         },
         broadcast=True)


def refresh_player_cards(players, hands):
    """
    Updates all of the players hands within the indivdual clients
    :param players: dictionary in format of key=name value=client_sid
    :param hands: List of card obejects within the players hand
    :return:
    """

    for player_name, player_info in players.items():
        card_imgs = []
        for card in hands[player_name]:
            card_imgs.append(card.img)
        update_player_cards(player_name, player_info["sid"], card_imgs)


def update_round(round_num):
    """
    updates the round_num element on players screens
    :param round_num: the round number
    :return:
    """

    emit(
        "update_element",
        {
            "target": "round_num",
            "target_type": "list",
            "action": "overwrite",
            "message": [f"Round Number: {round_num}"]
        },
        broadcast=all
    )


def update_trump(trump_suit):
    """
    Updates the trump suit displayed in game window
    :param trump_suit:
    :return:
    """

    emit(
        "update_element",
        {
            "target": "round_trump",
            "target_type": "list",
            "action": "overwrite",
            "message": [f"Round Trump Suit: {trump_suit}"]
        },
        broadcast=all
    )


def update_round_order(order):
    """
    updated the round order list itme
    :param order:
    :return:
    """

    emit(
        "update_element",
        {
            "target": "round_order",
            "target_type": "list",
            "action": "overwrite",
            "message": [f"Round Play Order: {order}"]
        },
        broadcast=all
    )


def update_bets_table(bets):
    """
    updates the bets table with new bets and wins
    :return:
    """
    bet_list = []

    for player, info in bets.items():
        bet_list.append({"player": player, "bet": info["bet"], "wins": info["wins"]})
    emit("update_bets_table", bet_list, broadcast=True)


def refresh_played_cards(played_cards):
    """
    method to update the played cards items in the clients views
    :param played_cards:
    :return:
    """

    card_list = []
    for player, card in played_cards.items():
        card_list.append({"player": player, "card_img": card.img})
    emit("update_played_cards", card_list, broadcast=True)


def update_score_table(players, scores=None):
    """
    updates the entire score table based on the values provided
    :param players: list of players in order
    :param scores: dictionary of scores for each round. if none then assumed no scores
    :return:
    """

    rounds = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 9, 8, 7, 6, 5, 4, 3, 2]
    headers = ["Round"]
    padded_scores = {}

    for player in players:
        headers.append(player)
        # pad the scores list of each player so that it has as many values as rounds
        if scores:
            padded_scores[player] = scores[player] + ["-"] * (len(rounds) - len(scores[player]))

    data = []
    for index, round_num in enumerate(rounds):
        data_row = [round_num]
        if scores:
            for player in players:
                data_row.append(padded_scores[player][index])
        else:
            data_row += ["-"] * ((len(players)+1) - len(data_row))
        data.append(data_row)

    data_row = ["TOTAL"]
    for player in players:
        if scores:
            data_row.append(sum(scores[player]))
        else:
            data_row.append(0)
    data.append(data_row)

    print(f"HEADERS = {headers}")
    print(f"DATA = {data}")
    emit("update_score_table", {"headers": headers, "data": data}, broadcast=True)
