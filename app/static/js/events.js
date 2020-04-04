// SOCKET - Setup socket object
var socket = io.connect('http://' + document.domain + ':' + location.port );


// INCOMING EVENT - UPDATE_ELEMENT - handles updating html elements
socket.on('update_element', function(data) {

    if (data.target_type === "div") {
        $('#' + data.target).append(data.message);

    } else if (data.target_type === "list") {
        if (data.action === "overwrite") {
            $('#' + data.target).empty();
            $.each(data.message, function( key, value ) {
                $('#' + data.target).append('<li>' + value + '</li>');
            });
        }
    }
});


// INCOMING EVENT - IDENTIFY - Used to identify the player and set their username
socket.on('identify', function(data) {

    $('#player_chat').append(data.message);

    if (data.action === "identify_client") {
        var playerName = prompt("Please enter your name", "Derpy");
        socket.emit("client_identify", {"player_name": playerName})
    } else if (data.action === "identify_duplicate") {
        var playerName = prompt("Player name already in use, Please enter your name:", "Harry Potter");
        socket.emit("client_identify", {"player_name": playerName})
    }
});

// INCOMING EVENT - MOVE_TO_GAME - Used to identify the player and set their username
socket.on('move_to_game', function(data) {

    $('#player_chat').append(data.message);

    if (data.action === "identify_client") {
        var playerName = prompt("Please enter your name", "Harry Potter");
        socket.emit("client_identify", {"player_name": playerName})
    } else if (data.action === "identify_duplicate") {
        var playerName = prompt("Player name already in use, Please enter your name:", "Harry Potter");
        socket.emit("client_identify", {"player_name": playerName})
    }
});

// OUTGOING EVENT - PLAYER_CHAT_BUTTON_CLICK - used for players to post in the chat
function event_client_chat() {
    let msg_text = document.getElementById('send_chat').value;
    socket.emit("client_chat", {"message": msg_text});
}

// OUTGOING EVENT - START_GAME - a layer starting the game
function event_start_game() {
    socket.emit("client_start_game", {});
}