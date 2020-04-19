/*********** SOCKET CONNECTION LOGIC ************/
// SOCKET - Setup socket object
var socket = io.connect('http://' + document.domain + ':' + location.port );




/*********** INCOMING EVENT LISTENERS ************/
// INCOMING EVENT - UPDATE_ELEMENT - handles updating html elements
socket.on('update_element', function(data) { update_element(data) });

// INCOMING EVENT - IDENTIFY - Used to identify the player and set their username
socket.on('identify', function(data) { identify_player(data) });

// INCOMING EVENT - update_score_table - updates a row of the score table
socket.on("update_score_table", function (data) { update_score_table(data) });

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

//INCOMING EVENT - RESET_ALL_ASSETS - cleans all the assets on the screen
socket.on("reset_all_assets", function () { reset_all_assets() });




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


// INCOMING EVENT FUNCTION - UPDATE_SCORE_TABLE - updates the entire score table
function update_score_table(data) {
    let old_table = document.getElementById("score_table");
    let new_table = document.createElement("table");

    new_table.classList.add("scores_table");
    new_table.id = "score_table";

    let headers = document.createElement("tr");
    for (let index=0; index < data.headers.length; index++) {
        console.log("HEADER VALUE IS " + data.headers[index])
        let header_data = document.createElement("th");
        header_data.innerText = data.headers[index];
        headers.appendChild(header_data);
    }
    new_table.appendChild(headers);

    for (let row_index=0; row_index < data.data.length; row_index++) {
        let data_row = document.createElement("tr")
        for (let item_index=0; item_index < data.data[row_index].length; item_index++) {
            let table_data = document.createElement("td");
            table_data.innerText = data.data[row_index][item_index];
            data_row.appendChild(table_data);
        }
        new_table.appendChild(data_row);
    }

    old_table.parentNode.replaceChild(new_table, old_table);

}


// INCOMING EVENT FUNCTION - BET_REPONSE - player needs to bet for the round
function bet_response(data) {
    // let bet_val = prompt(data.message);
    // socket.emit("bet_response", {"bet": bet_val})
    document.querySelector(".modal_bet_content_text").innerHTML = data.message
    toggle_modal_visable()



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

// INCOMING EVENT FUNCTION - RESET_ALL_ASSETS -
function reset_all_assets() {
    reset_score_table({"drop_players": true})
    update_bets_table([])
    update_played_cards([])
    update_player_cards({"cards": []})

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

// OUTGOING EVENT - JOIN GAME - player clicked the join game button
function event_join_game() {
    socket.emit("join_game")
}

// OUTGOING EVENT - RESET_GAME - resets the whole game, drops all players, cleans screen assets
function event_reset_game() {
    socket.emit("reset_game")
}


// OUTGOING EVENT - PLAY CARD RESPONSE - the client sending the card to the server to be played
function play_card_response(img_path) {
    console.log("INSIDE PLAY CARD RESPONSE WITH " + img_path);
    socket.emit("play_card_response", {"img_path": img_path});
}


// OUTGOING EVENT - MODAL SEND BET - sends the bet value from the modal_bet to server
function modal_send_bet() {
    let bet_val = document.getElementById("bet_input").value;
    socket.emit("bet_response", {"bet": bet_val})
    toggle_modal_visable()
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

//HELPERS - RESET_SCORE_TABLE - cleans the score table. will remove player columns if drop_table is true
function reset_score_table(data) {
    let old_scores = document.getElementById("score_table");
    let new_score = document.createElement("table");
    new_score.id = "score_table";
    new_score.classList.add("scores_table");

    let header_row = document.createElement("tr");
    let header_data = document.createElement("th");
    header_data.innerText = "Round";
    header_row.appendChild(header_data);
    new_score.appendChild(header_row);

    let rounds = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "10", "9", "8", "7", "6", "5", "4", "3", "2"]
    for (let round_num of rounds) {
        let row = document.createElement("tr");
        let data = document.createElement("td");
        data.innerText = round_num;
        row.appendChild(data);
        new_score.appendChild(row);
    }

    old_scores.parentNode.replaceChild(new_score, old_scores);
}

function toggle_modal_visable() {
    document.querySelector(".modal_bet").classList.toggle("modal_hidden")
}
