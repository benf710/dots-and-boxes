function getCookie(name) {
    var value = "; " + document.cookie;
    var parts = value.split("; " + name + "=");
    if (parts.length == 2) return parts.pop().split(";").shift();
    return null;
}

function setCookie(name, value) {
    document.cookie = name + "=" + value + ";" + ";path=/;" + "Secure";
}

function setPlayernameUI(player_name){
    player_name_item = document.getElementById("playername");
    player_name_item.innerText = player_name;
}

function initializeUser(){
    var player_name = getCookie("player_name");
    if (player_name == null){
        togglePlayerDiag();
        change_player();
    } else {
        setPlayernameUI(player_name);
    }
}

function togglePlayerDiag() {
    pn_diag = document.getElementById("playername-diag");
    content = document.getElementById("maincontentdiv");
    if (pn_diag.style.display === "none") {
        player_name = getCookie("player_name");
        if (player_name){
            document.getElementById("playernameinput").value = player_name;
        }
        content.style.display = "none";
        pn_diag.style.display = "block";
    } else {
        pn_diag.style.display = "none";
        content.style.display = "block";
    }
  }

function change_player(){
    document.getElementById("playername-error-message").style.display = "none"
    player_name = document.getElementById("playernameinput").value;
    name_rex = /^[a-zA-Z0-9]+$/
    if (name_rex.test(player_name)){
        setCookie("player_name", player_name);
        setPlayernameUI(player_name);
        togglePlayerDiag();
    } else {
        document.getElementById("playername-error-message").style.display = "block"
    }
}

function getAllGames(){
    error = false;
    request = new XMLHttpRequest();
    request.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            games_obj = JSON.parse(request.response);
            game_ids = Object.keys(games_obj);
            if (game_ids.length == 0){
                document.getElementById("games-list-message").innerHTML = '<p class="lead">No games available.</p>';
            } else {
                document.getElementById("games-list-message").innerHTML = '';
                list_builder = "";            
                game_ids.forEach (function(element) {
                    valid_id_rex = /^[0-9]+$/;
                    if (valid_id_rex.test(element)){
                        valid_value_rex = /^[a-zA-Z0-9\.: ]+$/;
                        game_object = games_obj[element];
                        status = game_object['status'];
                        if (valid_value_rex.test(status)){
                            list_builder += `<li><button class="btn btn-link" onclick="viewGame(${element});">${element} - ${status}</button>`
                            //list_builder += `<li><a href="/api/room/${element}/status">${element} - ${status}</a></li>`;
                        } else {
                            document.getElementById("games-list-message").innerHTML = '<p class="lead text-danger">Invalid response from server.</p>';
                            error = true;
                        }
                    } else {
                        document.getElementById("games-list-message").innerHTML = '<p class="lead text-danger">Invalid response from server.</p>';
                        error = true;
                    }
                })
                if (error == false){
                    document.getElementById("games-list").innerHTML = list_builder;
                }
            }
            toggleView("list-games-view");
        }
    }
    request.open("GET", "/api/all", true);
    request.send();
}

function toggleView(view) {
    pn_diag = document.getElementById("playername-diag");
    if (pn_diag.style.display === "block") {
        togglePlayerDiag();
    }
    index_view = document.getElementById("index-view");
    list_games_view = document.getElementById("list-games-view");
    in_game_view = document.getElementById("in-game-view");
    index_view.style.display = "none";
    in_game_view.style.display = "none";
    list_games_view.style.display = "none";
    document.getElementById(view).style.display = "block";
  }

function createGame(){
    request = new XMLHttpRequest();
    request.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            result = JSON.parse(request.response);
            if (result["status"] == "success"){
                viewGame(result["room"]);
            } else {
                document.getElementById("in-game-view-message-error").innerHTML = 'Invalid response from server.';
                toggleView("in-game-view");
            }
        }
    }
    request.open("GET", "/api/new?player_name=" + getCookie("player_name"), true);
    request.send();
}

var sleep = time => new Promise(resolve => setTimeout(resolve, time));
var poll = (promiseFn, time) => promiseFn().then(sleep(time).then(() => poll(promiseFn, time)))

function viewGame(game_id){ // Validate input

    function doUpdate(game_id){
        request = new XMLHttpRequest();
        request.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                document.getElementById("in-game-view-title").innerHTML = "Game: " + game_id;
                result = JSON.parse(request.response);
                if (result["status"] == "success"){
                    document.getElementById("in-game-view-message-status").innerHTML = result["result"]["status"];
                    if (result["result"]["status"] != "Waiting for another player to join."){
                        turn = result["result"]["turn"];
                        if (turn == getCookie("player_name")){
                            window.is_your_turn = true;
                        } else {
                            window.is_your_turn = false;
                        }
                        document.getElementById("in-game-view-message-turn").innerHTML = "Turn: " + turn;
                        scores = result["result"]["score"];
                        player_names = Object.keys(scores);
                        scores_text = player_names[0] + ': ' + scores[player_names[0]] + ', ' + player_names[1] + ': ' + scores[player_names[1]];
                        document.getElementById("in-game-view-message-score").innerHTML = scores_text;
                        updateBoard(result["result"]["board"]);
                    }
                }
            }
        }
        toggleView("in-game-view");
        request.open("GET", "/api/room/" + game_id + "/status", true)
        request.send();
    }
    poll(() => new Promise(() => doUpdate(game_id)), 5000);
}

function updateBoard(boardArray){
    xmax = 1;
    ymax = 1;
    boardArray.forEach(function(row){
        row.forEach(function(dot){
            if (dot['x'] < xmax){
                x_id = 'x' + dot['x'] + 'y' + dot['y'] + 'x';
                if (dot['x_vector']){
                    alreadySet(x_id);
                }
            }
            if (dot['y'] < ymax){
                y_id = 'x' + dot['x'] + 'y' + dot['y'] + 'y';
                if (dot['y_vector']){
                    alreadySet(y_id);
                }
            }
        })
    })
}

function alreadySet(buttonId){
    abutton = document.getElementById(buttonId);
    img = abutton.getElementsByClassName("poly")[0];
    img.classList.add("set");
    img.classList.remove("hover");
    img.classList.remove("not-set");
}

function setClicked(abutton){
    img = abutton.getElementsByClassName("poly")[0];
    if (!img.classList.contains("set") && window.is_your_turn){
        img.classList.add("set");
        img.classList.remove("hover");
        img.classList.remove("not-set");
    }
}

function setMouseOver(abutton){
    img = abutton.getElementsByClassName("poly")[0];
    if (!img.classList.contains("set") && window.is_your_turn){
        img.classList.add("hover");
        img.classList.remove("not-set");
    }
}

function setMouseOut(abutton){
    img = abutton.getElementsByClassName("poly")[0];
    if (!img.classList.contains("set") && window.is_your_turn){
        img.classList.remove("hover");
        img.classList.add("not-set");
    }
}