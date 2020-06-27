
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
//"var request = new XMLHttpRequest()     request.open('GET', ";