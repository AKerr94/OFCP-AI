var suits = ["h", "d", "s", "c"];
var playButtonCounter = 0,
    cardsPlacedCount = 0,
    deckIndex = 0,
    round_number = 1;
var playLock = false,
    playerFirst = false;
var deck = [];
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


setupGame(); // initial set up stages


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
    createDeck(); // initialise deck
    playerLabels(0,false,false); // set player name fields
}

// play function called from pressing button
function play() {

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

        for (i = 1; i < 6; i++) {
            var img = document.getElementById('place' + i + 'card');
            var card = dealCard();
            img.src = card.src;
            img.name = card.name;
            img.style.display = "block"; // set visible 
            //img.src = "cards/d01.png"; //ace of diamonds		
        }
        playLock = true;

        document.getElementById('playButton').innerHTML = 'Next';
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
            AI_main(); // call AI to handle their turn
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
    deckIndex = 0; 
    AI_placement_counter = 0;
    deck = [];
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

function randomInt(min, max) {
    return Math.floor(Math.random() * (max - min + 1) + min);
}

function createDeck() {
    var cstring, cname;

    // add every card object to deck array
    for (i = 0; i < 4; i++) {

        for (j = 1; j < 14; j++) {
            var card = document.createElement("img");
            // build img and name strings
            if (j < 10) {
                // if single digit need padding for string (0 before num)
                cstring = "cards/" + suits[i] + "0" + j + ".png";
                cname = suits[i] + "0" + j;
            } else {
                cstring = "cards/" + suits[i] + j + ".png";
                cname = suits[i] + "" + j;
            }

            card.src = cstring;
            card.name = cname;

            deck.push(card);
        }
    }

    deck = shuffle(deck);
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

// Fisher-Yates Shuffle Algorithm
function shuffle(cards) {
    var count = cards.length;
    var temp, i;

    while (count > 0) {
        i = Math.floor(Math.random() * count); // random index
        count--;

        // swap positions
        temp = cards[count];
        cards[count] = cards[i];
        cards[i] = temp;
    }

    return cards;
}

// deal card from deck
function dealCard() {
    if (deckIndex < 52) {
        deckIndex++;
        return deck[deckIndex - 1];
    } else {
        return null;
    }
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
            temp2 = document.getElementById(AI_positions[i]).childNodes[0].name;         // get AI's card at pos i
        }
        catch(err) {
            temp2 = null;
        }
        tarray1.push(temp1); // player's cards array
        tarray2.push(temp2); // AI's cards array
    }   
    return [tarray1,tarray2];
}

// main function for handling the AI - pass here once the player is done
function AI_main() {

    AI_placement_counter++;

    // special case - first round
    if (playButtonCounter == 1 || (playButtonCounter == 2 && playerFirst == true)) {
        
        // deal first 5 cards out 
        var first_5_cards = [];
        for (i = 0; i < 5; i++) {
            var card = dealCard();
            var cardimg = document.createElement("img");
            cardimg.src = card.src;
            cardimg.name = card.name;
            cardimg.width = 109;
            cardimg.height = 150;
            cardimg.ondragstart = function() {return false;};
            first_5_cards.push(cardimg);
        }

        var t = populate_game_state_arrays();
        tarray1 = t[0];
        tarray2 = t[1];
        
        reqwest({'url': 'http://alastairkerr.co.uk/ofc/subpage/AI-calculate-first-5'
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
                                                    "card1": first_5_cards[0].name,
                                                    "card2": first_5_cards[1].name,
                                                    "card3": first_5_cards[2].name,
                                                    "card4": first_5_cards[3].name,
                                                    "card5": first_5_cards[4].name,
                                                }
                                            }
                                        }
                                    }
                    )
              }
        })
        .then(function (resp) {
            var recommended_moves = JSON.parse(resp); // parse response as list again 
            //alert(recommended_moves);
            for(k = 0; k < 5; k++) {
                if (recommended_moves[k] == 1) {
                    // place card in bottom row
                    document.getElementById(AI_pos_bottom[0]).appendChild(first_5_cards[k]);
                    AI_pos_bottom.shift(); // removes first element from array - keeps up to date with available positions
                }
                else if (recommended_moves[k] == 2) {
                    // place card in middle row 
                    document.getElementById(AI_pos_middle[0]).appendChild(first_5_cards[k]);
                    AI_pos_middle.shift();
                }
                else if (recommended_moves[k] == 3) {
                    // place card in top row
                    document.getElementById(AI_pos_top[0]).appendChild(first_5_cards[k]);
                    AI_pos_top.shift();
                }
                else {
                    alert("Invalid recommended row! Expected 1, 2 or 3. Actual: " + recommended_moves[k]);
                }
                //var astring = "Placing card " + first_5_cards[k].name + " in pos " + recommended_moves[k];
                //alert(astring);
            }
            //AI_cards.splice(i, 0, cardimg); // append card to appropriate position in array
        })
        .fail(function (err, msg) {
            alert("Error! AI place 5 Reqwest unsuccessful... check server connection and try again.");
        });   
    }

    // general case
    else {
        var card = dealCard();
        var cardimg = document.createElement("img");
        cardimg.src = card.src;
        cardimg.name = card.name;
        cardimg.width = 109;
        cardimg.height = 150;
        cardimg.ondragstart = function() {return false;};
        
        var t = populate_game_state_arrays();
        tarray1 = t[0];
        tarray2 = t[1];
        
        reqwest({'url': 'http://alastairkerr.co.uk/ofc/subpage/AI-calculate-one'
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
                                                    "card": cardimg.name,
                                                }
                                            }
                                        }
                                    }
                    )
              }
        })
        .then(function (resp) {
            var recommended_move = JSON.parse(resp); // parse response 
            //alert(recommended_move);
            if (recommended_move == 1) {
                // place card in bottom row
                document.getElementById(AI_pos_bottom[0]).appendChild(cardimg);
                AI_pos_bottom.shift(); // removes first element from array - keeps up to date with available positions
            }
            else if (recommended_move == 2) {
                // place card in middle row 
                document.getElementById(AI_pos_middle[0]).appendChild(cardimg);
                AI_pos_middle.shift();
            }
            else if (recommended_move == 3) {
                // place card in top row
                document.getElementById(AI_pos_top[0]).appendChild(cardimg);
                AI_pos_top.shift();
            }
            else {
                alert("Invalid recommended row! Expected 1, 2 or 3. Actual: " + recommended_move);
            }
            //var astring = "Placing card " + cardimg.name + " in pos " + recommended_move;
            //alert(astring);
            
            //alert("AI placement count: " + AI_placement_counter + ", Player first:" + playerFirst);
            if (AI_placement_counter >= 9 && playerFirst == true) {
                gamestage = "end";
                play();
            }
        })
        .fail(function (err, msg) {
            alert("Error! AI place one Reqwest unsuccessful... check server connection and try again.");
        });           
    }
}


// © 2015 Alastair Kerr. All rights reserved.
// formatted with http://jsbeautifier.org/