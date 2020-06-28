
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
        content.style.display = "none";
        pn_diag.style.display = "block";
    } else {
        pn_diag.style.display = "none";
        content.style.display = "block";
    }
  }

function change_player(){
    //player_name = prompt("Enter your player name");
    player_name = document.getElementById("playernameinput").value;
    if (player_name != ""){
        setCookie("player_name", player_name);
        setPlayernameUI(player_name);
        togglePlayerDiag();
    } else {
        console.log("Enter a playername");
    }
}

function getAllGames(){
    error = false;
    request = new XMLHttpRequest();
    request.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            games_obj = JSON.parse(request.response);
            game_ids = Object.keys(games_obj);
            console.log("Request completed");
            if (game_ids.length == 0){
                document.getElementById("list-games-view").innerHTML = '<p class="lead">No games available.</p>';
            } else {
                list_builder = "";            
                game_ids.forEach (function(element) {
                    console.log(element);
                    valid_id_rex = /^[0-9]+$/;
                    if (valid_id_rex.test(element)){
                        console.log('id passed');
                        valid_value_rex = /^[a-zA-Z0-9\. ]+$/;
                        game_object = games_obj[element];
                        status = game_object['status'];
                        if (valid_value_rex.test(status)){
                            console.log('status passed');
                            list_builder += `<li><a href="/api/room/${element}/status">${element} - ${status}</a></li>`;
                        } else {
                            document.getElementById("list-games-view").innerHTML = '<p class="lead">Invalid response from server.</p>';
                            error = true;
                            console.log('error at valid_status');
                        }
                    } else {
                        document.getElementById("list-games-view").innerHTML = '<p class="lead">Invalid response from server.</p>';
                        error = true;
                        console.log('error at valid_id');
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
    if (pn_diag.style.display === "none") {
        index_view = document.getElementById("index-view");
        list_games_view = document.getElementById("list-games-view");
        in_game_view = document.getElementById("in-game-view");
        index_view.style.display = "none";
        in_game_view.style.display = "none";
        list_games_view.style.display = "none";
        document.getElementById(view).style.display = "block";
    }
  }

//"var request = new XMLHttpRequest()     request.open('GET', ";