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

// INCOMING EVENT - add_player_to_score - adds a player to the score table
socket.on("add_player_to_score", function (data) {
    add_column_to_scores(data)
});

// INCOMING EVENT - update_score_row - updates a row of the score table
socket.on("update_score_row", function (data) {
    update_score_row(data)
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

// HELPER - ADD_COLUMN_TO_SCORES - adds a column to the table specified with the heading specified.
// all other values will be "-"
function add_column_to_scores(data) {

    let table = document.getElementById("score_table");
    let index = 0;

    for(let row of table.rows) {
        var cell = row.insertCell(-1);
        if (index === 0) {
            cell.innerText = data.player_name;
        } else {
            cell.innerText = "-";
        }
        index += 1;
    }
}

// HELPER - UPDATE_SCORE_ROW - updates the player values for the score table for a specific round
function update_score_row(data) {
    let table = document.getElementById("score_table");
    let row_index = data.row_index;
    let values = data.player_scores;

    let row = table.rows[row_index];
    for (let cell_index=1; cell_index <= values.length; cell_index++) {
        row.cells.item(cell_index).innerText = values[cell_index-1]
    }

}