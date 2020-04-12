/*********** SOCKET CONNECTION LOGIC ************/
// SOCKET - Setup socket object
var socket = io.connect('http://' + document.domain + ':' + location.port );




/*********** INCOMING EVENT LISTENERS ************/
// INCOMING EVENT - UPDATE_ELEMENT - handles updating html elements
socket.on('update_element', function(data) { update_element(data) });

// INCOMING EVENT - IDENTIFY - Used to identify the player and set their username
socket.on('identify', function(data) { identify_player(data) });

// INCOMING EVENT - add_player_to_score - adds a player to the score table
socket.on("add_player_to_score", function (data) { add_column_to_scores(data) });

// INCOMING EVENT - update_score_row - updates a row of the score table
socket.on("update_score_row", function (data) { update_score_row(data) });

// INCOMING EVENT - update_player_cards - updates the specific players held card
socket.on("update_player_cards", function (data) { update_player_cards(data) });

// INCOMING EVENT - BET - player is asked to bet tricks on this round
socket.on("bet", function (data) { bet_response(data) });

//INCOMING EVENT - UPDATE_BETS_TABLE - updates the bets table for the client
socket.on("update_bets_table", function (data) { update_bets_table(data) });

//INCOMING EVENT - PLAY_CARD - server telling player its there turn
socket.on("play_card", function (data) { play_card(data) });

//INCOMING EVENT: UPDATE PLAYED CARDS - updates the played card on the client views
socket.on("update_played_cards", function (data) { update_played_cards(data) });




/*********** INCOMING EVENT FUNCTIONS ************/

// INCOMING EVENT FUNCTION - IDENTIFY PLAYER - player sets thyer name and is registred for the game
function identify_player(data) {
    $('#player_chat').append(data.message);

    if (data.action === "identify_client") {
        let playerName = prompt("Please enter your name");
        socket.emit("client_identify", {"player_name": playerName})
    } else if (data.action === "identify_duplicate") {
        let playerName = prompt("Player name already in use, Please enter your name:");
        socket.emit("client_identify", {"player_name": playerName})
    }
}

// INCOMING EVENT FUNCTION - ADD_COLUMN_TO_SCORES - adds a column to the table specified with the heading specified.
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

// INCOMING EVENT FUNCTION - UPDATE_SCORE_ROW - updates the player values for the score table for a specific round
function update_score_row(data) {
    let table = document.getElementById("score_table");
    let row_index = data.row_index;
    let values = data.player_scores;

    let row = table.rows[row_index];
    for (let cell_index=1; cell_index <= values.length; cell_index++) {
        row.cells.item(cell_index).innerText = values[cell_index-1]
    }

}


// INCOMING EVENT FUNCTION - BET_REPONSE - player needs to be for the round
function bet_response(data) {
    let bet_val = prompt(data.message);
    socket.emit("bet_response", {"bet": bet_val})
}


// INCOMING EVENT FUNCTION - UPDATE_BETS_TABLE - drop the tbody tag from the table and replace it with a new one
// with new values
function update_bets_table(data) {
    let old_tbody = document.getElementById("bet_table_body");
    let new_tbody = document.createElement("tbody");
    new_tbody.id = "bet_table_body";

    for (let index=0; index < data.length; index++) {
        console.log(data[index]);
        let row = document.createElement("tr");
        let player_td = document.createElement("td");
        player_td.innerHTML = data[index].player;
        let bet_td = document.createElement("td");
        bet_td.innerHTML = data[index].bet;
        let wins_td = document.createElement("td");
        wins_td.innerHTML = data[index].wins;

        row.appendChild(player_td);
        row.appendChild(bet_td);
        row.appendChild(wins_td);

        new_tbody.appendChild(row);
    }

    old_tbody.parentNode.replaceChild(new_tbody, old_tbody);

}

// INCOME EVENT FUNCTION - PLAY CARD - user informed from server to play card
function play_card(data) { alert(data.message) }

// INCOMING EVENT FUNCTION - UPDATE PLAYED CARDS - cleans out then updates the played cards view object
function update_played_cards(data) {
    let old_cards = document.getElementById("played_card_obj");
    let new_cards = document.createElement("div");
    new_cards.id = "played_card_obj";

    let old_players = document.getElementById("played_cards_player");
    let new_players = document.createElement("div");
    new_players.id = "played_cards_player";

    let player = document.createElement("p");
    for (let index=0; index < data.length; index++) {
        player.innerText += "     " + data[index].player
        let card_img = data[index].card_img;

        let img_obj = document.createElement("img");
        img_obj.src = card_img;

        new_cards.appendChild(img_obj);
        new_players.appendChild(player)
    }

    old_cards.parentNode.replaceChild(new_cards, old_cards);
    old_players.parentNode.replaceChild(new_players, old_players);
}



/*********** OUTGOING EVENT FUNCTIONS************/

// OUTGOING EVENT - PLAYER_CHAT_BUTTON_CLICK - used for players to post in the chat
function event_client_chat() {
    let msg_text = document.getElementById('send_chat').value;
    socket.emit("client_chat", {"message": msg_text});
}

// OUTGOING EVENT - START_GAME - a player starting the game
function event_start_game() {
    socket.emit("client_start_game", {});
}

// OUTGOING EVENT - PLAY CARD RESPONSE - the client sending the card to the server to be played
function play_card_response(img_path) {
    console.log("INSIDE PLAY CARD RESPONSE WITH " + img_path);
    socket.emit("play_card_response", {"img_path": img_path});
}





/*********** HELPER FUNCTIONS ************/
// HELPERS - UPDATE ELEMENT - updates a visual element of the page
function update_element(data) {
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
}

// HELPER - UPDATE_PLAYER_CARDS - updates the images of the players held cards
function update_player_cards(data) {
    // clear the contents of the player cards fiv
    document.getElementById("player_card_objs").innerHTML = "";

    // for each card path passed in, create an image tag and insert into the dom element
    for (let index = 0; index < data.cards.length; index++) {
        let card_img = document.createElement("img");
        card_img.src = data.cards[index];
        card_img.addEventListener("click", function(){ play_card_response(data.cards[index]); });
        console.log("IMAGE PATH = " + card_img.src);
        document.getElementById("player_card_objs").appendChild(card_img)
    }
}