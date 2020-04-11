from collections import OrderedDict

from flask import request
from flask_socketio import emit

from .game import Calithumpian
from .. import socketio
from ..main import html_builder

HTML_TAG_PARAGRAPH = "p"

GAME = Calithumpian()

PLAYERS = OrderedDict()


# --- INCOMING EVENTS --------------------
@socketio.on("connect")
def event_connect():
    print(f"client {request.sid} connected!")
    message = html_builder.build_text_tag(HTML_TAG_PARAGRAPH, "SYSTEM: Please provide a player name")
    emit('identify', {"action": "identify_client", "message": message})


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

        # update score table with all current players
        for player in PLAYERS.keys():
            emit('add_player_to_score', {"player_name": player})

        # add new player to ALL players score tables
        print("BEFORE CALL")
        emit('add_player_to_score', {"player_name": data["player_name"]}, broadcast=True)
        print("AFTER CALL")

        # Register Player
        PLAYERS[data["player_name"]] = {"sid": sid}
        print(f"Player '{data['player_name']}' has joined the game!")

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


def play_card(player):
    """
    sends an event to a specific client to play a card
    :param player:
    :return:
    """

    player_sid = PLAYERS[player]["sid"]
    message = f"Player {player}, its your turn to play a card! please click a card from your hand to play it"
    emit("play_card", {"message": message}, room=player_sid)


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

    emit("update_element",
         {
             "target": "play_action_txt",
             "target_type": "list",
             "action": "overwrite",
             "message": [action_message]
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
