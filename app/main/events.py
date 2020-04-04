from collections import OrderedDict

from flask import request
from flask_socketio import emit

from .game import Calithumpian
from .. import socketio
from ..main import html_builder

HTML_TAG_PARAGRAPH = "p"

PLAYERS = OrderedDict()


# --- Events --------------------
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
    client = request.sid
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
        PLAYERS[data["player_name"]] = {"client": client}
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

    emit("update_score_row", {"row_index": 5, "player_scores": [1, 2, 3]}, broadcast=True)

    game = Calithumpian(PLAYERS.keys())
    game.play()


# -- HELPERS --------------------
def get_player_name_from_sid(sid):
    """
    Gets the player name from the SID given
    :param sid:
    :return:
    """

    for name, info in PLAYERS.items():
        if info["client"] == sid:
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


