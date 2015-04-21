var suits = ["h", "d", "s", "c"];
var playButtonCounter = 0,
    cardsPlacedCount = 0,
    round_number = 1;
var playLock = false;
    playerFirst = true;
var AI_positions = ["p2_bottom1", "p2_bottom2", "p2_bottom3", "p2_bottom4", "p2_bottom5",
    "p2_middle1", "p2_middle2", "p2_middle3", "p2_middle4", "p2_middle5",
    "p2_top1", "p2_top2", "p2_top3"
];
var AI_pos_bottom = AI_positions.slice(0,5);
var AI_pos_middle = AI_positions.slice(5,10);
var AI_pos_top = AI_positions.slice(10);
var AI_placement_counter = 0;
var player_positions = ["p1_bottom1", "p1_bottom2", "p1_bottom3", "p1_bottom4", "p1_bottom5",
    "p1_middle1", "p1_middle2", "p1_middle3", "p1_middle4", "p1_middle5",
    "p1_top1", "p1_top2", "p1_top3"
];
var gamestage = "init";
var rowScoresArr = [0, 0, 0, 0, 0, 0]; // player 1 top, p1 middle, p1 bottom, p2 top, p2 middle, p2 bottom
var p1score = 0,
    p2score = 0;
var player1 = "Player 1",
    player2 = "Computer Opponent";


setupGame(); // Initial set up of game


function allowDrop(ev) {

    ev.preventDefault();
}

function drag(ev) {
    ev.dataTransfer.setData("text", ev.target.id);
}

function drop(ev) {
    ev.preventDefault();

    // if the container isnt empty (stops user from dragging multiple cards onto one box)
    if (ev.target.hasChildNodes()) {
        return;
    }

    if (ev.target.className == "cardl") {

        // drop card into container
        var data = ev.dataTransfer.getData("text");
        ev.target.appendChild(document.getElementById(data));


        // handle card count and unlocking of button
        if (playLock == true) {
            cardsPlacedCount++;
        }

        if (cardsPlacedCount == 5) {
            playLock = false;
        } else if (playButtonCounter > 1 && cardsPlacedCount == (playButtonCounter + 4)) {
            playLock = false;
        }

        // check if all cards are placed. If yes set gamestage
        if (cardsPlacedCount == 13) {
            if (playerFirst) {
                AI_main();
            }
            gamestage = "end";
            if (playerFirst == false) {
                play(); // automatically move on when last card is dropped
            }
        }
    }
}

function setupGame() {
    console.log('Welcome to OFCP-AI, an application by Alastair Kerr!');
    playerLabels(0,false,false); // set player name fields
    var button = document.getElementById('playButton');
    button.onclick = function() {
        button.innerHTML = "Next"; // change button text from 'Play' to 'Next'
        POST_reqwest(initial_5 ); // POST gamestate to backend and then calls initial_5 with response
    };
}

function initial_5(resp) {
    // displays player's first 5 cards to place
    cards = JSON.parse(resp); // parse response to get array of cards to be placed
    for (i = 1; i < 6; i++) {
        var img = document.getElementById('place'+i+'card');
        var card = cards[i-1];
        img.src = "../static/cards/" + card + ".png";
        img.name = card;
        img.style.display = "block"; // set visible
        //img.src = "cards/d01.png"; //ace of diamonds
    }
    playLock = true;

    var button = document.getElementById("playButton");
    button.onclick = function() {
        // TODO remake this playLock functionality to be less buggy - ATM can place one card in 5 places to unlock button - pressing button will crash game
        if (playLock == true) {
            alert("You must place all your cards first!")
            return;
        }
        button.style.display = "none"; // hide button while AI calculates moves

        var b_text = document.getElementById("buttonTextReplacer");
        b_text.innerHTML = "AI is calculating move..."

        POST_reqwest(handleAICards);
    };

}

function handleAICards(resp) {
    var gs = JSON.parse(resp); // parse game state from response
    var b_text = document.getElementById("buttonTextReplacer");
    b_text.style.display = "block";
    alert(gs['cardtoplace']);

    readAndPlace = function(min,max,row) { // read cards from backend response and updates frontend
        for (i = min; i < max+1; i++) {
            t = gs['properties2']['cards']['items']['position'+i] // get card info for appropriate position in game state
            if (t != null) {
                var cardimg = document.createElement("img");
                cardimg.src = "../static/cards/" + t + ".png";
                cardimg.name = t;
                cardimg.width = 109;
                cardimg.height = 150;
                cardimg.ondragstart = function() {return false;};

                j=i;
                // modify j to get correct row position
                if (row == 'middle'){
                    j -= 5;
                }else if (row == 'top') {
                    j -= 10;
                }

                console.log("AI Placed " + cardimg.name + " in row " + row + " (position" + i + ")");

                document.getElementById('p2_'+row+j).appendChild(cardimg); // append image for this card to position on game board

            }
        }
    }
    readAndPlace(1,5,'bottom');
    readAndPlace(6,10,'middle');
    readAndPlace(11,13,'top');

    var button = document.getElementById("playButton");
    button.style.display = "block";

    var b_text = document.getElementById("buttonTextReplacer");
    b_text.style.display = "none";
}

// play function called from pressing button
function play() {

    alert("Play function called! waaaa");

    if (gamestage == "init") {
        gamestage = "game";
    } else if (gamestage == "end") {

        //work out scores for each row and display these
        handleRoundEnd();
        round_number += 1;

        // modify play button into play again
        var button = document.getElementById("playButton");
        button.innerHTML = "Play again!";

        button.onclick = function() {
            resetGame();
        }

        return;
    }


    // if cards from this round haven't been placed yet then button is disabled
    if (playLock == true) {
        if (gamestage == "game") {
            alert("You must place all your cards first!");
            return;
        } else {
            alert("Game state error");
            return;
        }
    }

    playButtonCounter++;

    // special case - first round
    if (playButtonCounter == 1) {

        if (!playerFirst) {
            AI_main();
        }
        alert("The play function is not dead code!");
        POST_reqwest(initial_5) // gets first 5 cards for player to place from backend
        //AI_main()
    }

    // general case
    else {

        if (!playerFirst) {
            AI_main();
        }

        if (playButtonCounter == 2) { // lock current cards in place
            for (i = 1; i < playButtonCounter + 4; i++) {
                var temp = document.getElementById('place' + i + 'card');
                temp.ondragstart = function() {return false;};

            }
        } else { // lock card from last round
            var temp = document.getElementById('place' + (playButtonCounter + 3) + 'card');
            temp.ondragstart = function() {return false;};
        }

        // generate next card
        var img = document.getElementById('place' + (playButtonCounter + 4) + 'card');
        img.style.display = "block"; // set visible
        var card = dealCard();
        img.src = card.src;
        img.name = card.name;

        playLock = true;

        if (playerFirst) {
            AI_main();
        }
    }
}

function resetGame() {
    // reset button
    var button = document.getElementById("playButton");
    button.innerHTML = "Play!";
    button.onclick = function() {
        play();
    }

    // reset global vars
    playButtonCounter = 0;
    cardsPlacedCount = 0;
    AI_placement_counter = 0;
    gamestage = "init";
    rowScoresArr = [0, 0, 0, 0, 0, 0];

    // recreate AI row temp arrays
    AI_pos_bottom = AI_positions.slice(0,5);
    AI_pos_middle = AI_positions.slice(5,10);
    AI_pos_top = AI_positions.slice(10);

    setupGame();

    // reset player cards
    for (i = 1; i <= 13; i++) {
        var temp = document.getElementById("place" + i + "card");
        temp.style.display = "none";
        temp.draggable = "true";
        temp.ondragstart = function(event) {
            drag(event);
        };
        temp.ondrop = function(event) {
            drop(event);
        };
        if (i <= 5) {
            document.getElementById("place" + i).appendChild(temp);
        } else {
            document.getElementById("place1").appendChild(temp);
        }
    }

    // remove AI cards
    var elements = document.getElementsByClassName("cardr");
    for (i = 0; i < elements.length; i++) {
        var temp = elements[i].firstChild;
        temp.parentElement.removeChild(temp);
    }

    // hide row scores from previous round
    var textString, temp;
    for (pID = 1; pID <= 2; pID++) {
        for (rowID = 1; rowID <= 3; rowID++) {
            textString = "p" + pID + "_text" + rowID;
            temp = document.getElementById(textString);
            temp.innerHTML = "";
        }
    }

    // handle whose turn it is first next round
    if (playerFirst) {
        playerFirst = false;
    } else {
        playerFirst = true;
    }

    play(); // automatically play next hand
    //window.location.reload();
}

function handleRoundEnd() {

    var temp1 = "", temp2 = "";
    var tarray1 = [], tarray2 = [];

    for (i = 0; i < 13; i++) {
        temp1 = document.getElementById(player_positions[i]).childNodes[0].name; // get player's card at pos i
        temp2 = document.getElementById(AI_positions[i]).childNodes[0].name;         // get AI's card at pos i
        tarray1.push(temp1); // player's cards array
        tarray2.push(temp2); // AI's cards array
    }

    reqwest({'url': 'http://alastairkerr.co.uk/ofc/subpage/calculate-scores/'
        , 'method': 'post'
        , 'data': {'game-state':JSON.stringify(
                                {
                                    "name1": "Player1",
                                    "properties1": {
                                        "cards": {
                                            "type": "array",
                                            "items": {
                                                "position1": tarray1[0],
                                                "position2": tarray1[1],
                                                "position3": tarray1[2],
                                                "position4": tarray1[3],
                                                "position5": tarray1[4],
                                                "position6": tarray1[5],
                                                "position7": tarray1[6],
                                                "position8": tarray1[7],
                                                "position9": tarray1[8],
                                                "position10": tarray1[9],
                                                "position11": tarray1[10],
                                                "position12": tarray1[11],
                                                "position13": tarray1[12],
                                            }
                                        }
                                    },
                                    "name2": "Player2",
                                    "properties2": {
                                        "cards": {
                                            "type": "array",
                                            "items": {
                                                "position1": tarray2[0],
                                                "position2": tarray2[1],
                                                "position3": tarray2[2],
                                                "position4": tarray2[3],
                                                "position5": tarray2[4],
                                                "position6": tarray2[5],
                                                "position7": tarray2[6],
                                                "position8": tarray2[7],
                                                "position9": tarray2[8],
                                                "position10": tarray2[9],
                                                "position11": tarray2[10],
                                                "position12": tarray2[11],
                                                "position13": tarray2[12],
                                            }
                                        }
                                    }
                                }
                )
          }
    })
  .then(function (resp) {
    scores_obj = JSON.parse(resp); // parse response as list again
    //  finalise scoring - update frontend to reflect scores

    p1_wins = 0;     // keep track of how many rows are won by each player
    p2_wins = 0;     // (if a player wins all 3 rows, they scoop for +3 points)
    p1foul = scores_obj[3][0];  // boolean - true if p1's hand fouled
    p2foul = scores_obj[3][1];  // boolean - true if p2's hand fouled

    if (scores_obj[0][0] == 1) {                            // Player 1 wins bottom row
        net = (scores_obj[0][1] - scores_obj[0][2]) + 1;    // Total = p1's royalty - p2's royalty, +1 for winning row
        rowScoresArr[0] = net;                              // p1's bottom score
        rowScoresArr[3] = -net;                             // p2's bottom score
        p1_wins += 1;
    } else if (scores_obj[0][0] == 2) {                     // Player 2 wins bottom row
        net = (scores_obj[0][2] - scores_obj[0][1]) + 1;    // Total = p1's royalty - p2's royalty
        rowScoresArr[0] = -net;                             // p1's bottom score
        rowScoresArr[3] = net;                              // p2's bottom score
        p2_wins += 1;
    }

    if (scores_obj[1][0] == 1) {                            // Player 1 wins middle row
        net = (scores_obj[1][1] - scores_obj[1][2]) + 1;    // Total = p1's royalty - p2's royalty
        rowScoresArr[1] = net;                              // p1's middle score
        rowScoresArr[4] = -net;                             // p2's middle score
        p1_wins += 1;
    } else if (scores_obj[1][0] == 2) {                     // Player 2 wins middle row
        net = (scores_obj[1][2] - scores_obj[1][1]) + 1;    // Total = p1's royalty - p2's royalty
        rowScoresArr[1] = -net;                             // p1's middle score
        rowScoresArr[4] = net;                              // p2's middle score
        p2_wins += 1;
    }

    if (scores_obj[2][0] == 1) {                            // Player 1 wins top row
        net = (scores_obj[2][1] - scores_obj[2][2]) + 1;    // Total = p1's royalty - p2's royalty
        rowScoresArr[2] = net;                              // p1's top score
        rowScoresArr[5] = -net;                             // p2's top score
        p1_wins += 1;
    } else if (scores_obj[2][0] == 2) {                     // Player 2 wins top row
        net = (scores_obj[2][2] - scores_obj[2][1])  + 1;   // Total = p1's royalty - p2's royalty
        rowScoresArr[2] = -net;                             // p1's top score
        rowScoresArr[5] = net;                              // p2's top score
        p2_wins += 1;
    }

    p1score += rowScoresArr[0] + rowScoresArr[1] + rowScoresArr[2]; // player's top middle bottom
    p2score += rowScoresArr[3] + rowScoresArr[4] + rowScoresArr[5]; // AI's top middle bottom

    scoop = 0;
    if (p1_wins == 3) {         // player 1 scoops for + 3 extra points
        p1score += 3;
        p2score -= 3;
        scoop = 1;
    }
    else if (p2_wins == 3) {    // player 2 scoops for + 3 extra points
        p1score -= 3;
        p2score += 3;
        scoop = 2;
    }

    // modify score fields to reflect row scores
    var temp, colourString, textString, count = 0;
    // iterate through every row and update score containers
    // Display positive scores in green and negative in red
    for (pID = 1; pID <= 2; pID++) {
        for (rowID = 3; rowID >= 1; rowID--) {
            textString = "p" + pID + "_text" + rowID;
            colourString = chooseScoreColour(rowScoresArr[count]);
            temp = document.getElementById(textString);
            temp.innerHTML = rowScoresArr[count];
            temp.style.color = colourString;
            count++;
        }
    }

    // change player labels to reflect their total scores
    playerLabels(scoop,p1foul,p2foul);
  })
  .fail(function (err, msg) {
     alert("Error! Scoring Reqwest unsuccessful... check server connection and try again.");
  });

}

function chooseScoreColour(num) {
    if (num >= 0) {
        return "#00C303"; //green for positive
    } else {
        return "#FF0000"; //red for negative
    }
}

function playerLabels(scoop_id, p1_foul, p2_foul) {
    /* update player labels. Sccop id = 0 (no scoop)
       scoop id = 1 (player 1 scoops)
       scoop id = 2 (player 2 scoops) */

    p1_label_tail = "";
    p2_label_tail = "";

    p1_t_score = p1score;
    p2_t_score = p2score;

    if (scoop_id == 1) {             // if player 1 scoops
        p1_label_tail += " + Scoop (3)!"
        p1_t_score = p1_t_score - 3; // display modified score + bonus
    }
    else if (scoop_id == 2) {        // if player 2 scoops
        p2_label_tail += " + Scoop (3)!"
        p2_t_score = p2_t_score - 3; // display modified score + bonus
    }

    if (p1_foul == true) {
        p1_label_tail += " Fouled!"
    }
    if (p2_foul == true) {
        p2_label_tail += " Fouled!"
    }

    var temp1, temp2;
    temp1 = player1 + " (" + p1_t_score + ")" + p1_label_tail;
    temp2 = player2 + " (" + p2_t_score + ")" + p2_label_tail;

    var temp3 = document.getElementById("p1label");
    temp3.innerHTML = temp1;
    temp3 = document.getElementById("p2label");
    temp3.innerHTML = temp2;
}

function populate_game_state_arrays() {
    // populate temp arrays for game state. If no card placed in a position set appropriate index to null

    var temp1 = "", temp2 = "";
    var tarray1 = [], tarray2 = [];

    // populate temp arrays for game state. If no card placed in a position set appropriate index to null
    for (i = 0; i < 13; i++) {
        try {
            temp1 = document.getElementById(player_positions[i]).childNodes[0].name; // get player's card at pos i
        }
        catch(err) {
            temp1 = null;
        }

        try {
            temp2 = document.getElementById(AI_positions[i]).childNodes[0].name;     // get AI's card at pos i
        }
        catch(err) {
            temp2 = null;
        }
        tarray1.push(temp1); // player's cards array
        tarray2.push(temp2); // AI's cards array
    }
    return [tarray1,tarray2];
}

function POST_reqwest(thenFunction) {

    // get card info at each position on board (card name or null if empty)
    var t = populate_game_state_arrays();
    tarray1 = t[0];
    tarray2 = t[1];

    reqwest({'url': 'http://alastairkerr.co.uk/ofc/subpage/ofc-backend/'
        , 'method': 'post'
        , 'data': {"game-id":gameId,
            "game-state":JSON.stringify(
                                {
                                    "name1": "Player1",
                                    "properties1": {
                                        "cards": {
                                            "type": "array",
                                            "items": {
                                                "position1": tarray1[0],
                                                "position2": tarray1[1],
                                                "position3": tarray1[2],
                                                "position4": tarray1[3],
                                                "position5": tarray1[4],
                                                "position6": tarray1[5],
                                                "position7": tarray1[6],
                                                "position8": tarray1[7],
                                                "position9": tarray1[8],
                                                "position10": tarray1[9],
                                                "position11": tarray1[10],
                                                "position12": tarray1[11],
                                                "position13": tarray1[12],
                                            }
                                        }
                                    },
                                    "name2": "Player2",
                                    "properties2": {
                                        "cards": {
                                            "type": "array",
                                            "items": {
                                                "position1": tarray2[0],
                                                "position2": tarray2[1],
                                                "position3": tarray2[2],
                                                "position4": tarray2[3],
                                                "position5": tarray2[4],
                                                "position6": tarray2[5],
                                                "position7": tarray2[6],
                                                "position8": tarray2[7],
                                                "position9": tarray2[8],
                                                "position10": tarray2[9],
                                                "position11": tarray2[10],
                                                "position12": tarray2[11],
                                                "position13": tarray2[12],
                                            }
                                        }
                                    }
                                }
                )
          }
        })
       .then(thenFunction) // calls this function after a successful reqwest
       .fail(function (err, msg) {
            astring = "Error! POST 'Reqwest' unsuccessful... check server connection and try again.\n" + err.toString();
            alert(astring);
      });
     }

// © 2015 Alastair Kerr. All rights reserved.
// formatted with http://jsbeautifier.org/