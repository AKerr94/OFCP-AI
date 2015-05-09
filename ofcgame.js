// global vars
var suits = ["h", "d", "s", "c"];
var playButtonCounter = 0,
    cardsPlacedCount = 0,
    deckIndex = 0;
var playLock = false,
    playerFirst = false;
var deck = [];
var AI_positions = ["p2_bottom1", "p2_bottom2", "p2_bottom3", "p2_bottom4", "p2_bottom5",
    "p2_middle1", "p2_middle2", "p2_middle3", "p2_middle4", "p2_middle5",
    "p2_top1", "p2_top2", "p2_top3"
];
var AI_pos_c = AI_positions.slice();
var AI_cards = [];
var AI_placement_counter = 0;
var player_positions = ["p1_bottom1", "p1_bottom2", "p1_bottom3", "p1_bottom4", "p1_bottom5",
    "p1_middle1", "p1_middle2", "p1_middle3", "p1_middle4", "p1_middle5",
    "p1_top1", "p1_top2", "p1_top3"
];
var player_cards = [];
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
        }
    }
}

function setupGame() {
    createDeck(); // initialise deck
    playerLabels(); // set player name fields
}

// play function called from pressing button
function play() {

    if (gamestage == "init") {
        gamestage = "game";
    } else if (gamestage == "end") {

        //work out scores for each row and display these
        handleRoundEnd();

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
                temp.draggable = "false";
                temp.ondragstart = "return false;";
                temp.ondrop = "return false;";
            }
        } else { // lock card from last round
            var temp = document.getElementById('place' + (playButtonCounter + 3) + 'card');
            temp.draggable = "false";
            temp.ondragstart = "return false;";
            temp.ondrop = "return false;";
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
    playButtonCounter = 0, cardsPlacedCount = 0, deckIndex = 0, AI_placement_counter = 0;
    AI_cards = [], player_cards = [], deck = [];
    gamestage = "init";
    rowScoresArr = [0, 0, 0, 0, 0, 0];
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

    play(); // automatically start next round
    //window.location.reload();
}

function handleRoundEnd() {

    // work out scores for each row

    // calculate hand rank for player 1's bottom row 
    var p1bottomrow = [];
    for (i = 0; i < 5; i++) {
        var tcard = document.getElementById(player_positions[i]).childNodes[0]; // extract card from each div
        p1bottomrow.push(tcard);
    }
    var p1bottomrank = getHandRank(p1bottomrow);

    // calculate hand rank for player 1's middle row 
    var p1middlerow = [];
    for (i = 5; i < 10; i++) {
        var tcard = document.getElementById(player_positions[i]).childNodes[0]; // extract card from each div
        p1middlerow.push(tcard);
    }
    var p1middlerank = getHandRank(p1middlerow);

    // calculate hand rank for player 1's top row 
    var p1toprow = [];
    for (i = 10; i < 13; i++) {
        var tcard = document.getElementById(player_positions[i]).childNodes[0]; // extract card from each div
        p1toprow.push(tcard);
    }
    var p1toprank = getHandRank(p1toprow);

    /*
       var scoringAlertString = "ranks: 0 high card, 1 pair, 2 two pair, 3 trips, 4 straight, 5 flush, 6 full house, 7 four of a kind, 8 straight flush, 9 royal flush";
       scoringAlertString += "\n\n" + "Bottom Rank: " + p1bottomrank + ", Middle Rank: " + p1middlerank + ", Top Rank: " + p1toprank;
       alert(scoringAlertString);
       */

    // AI scores

    // calculate hand rank for player 2's bottom row 
    var p2bottomrow = [];
    for (i = 0; i < 5; i++) {
        var tcard = document.getElementById(AI_pos_c[i]).childNodes[0]; // extract card from each div
        p2bottomrow.push(tcard);
    }
    var p2bottomrank = getHandRank(p2bottomrow);

    // calculate hand rank for player 2's middle row 
    var p2middlerow = [];
    for (i = 5; i < 10; i++) {
        var tcard = document.getElementById(AI_pos_c[i]).childNodes[0]; // extract card from each div
        p2middlerow.push(tcard);
    }
    var p2middlerank = getHandRank(p2middlerow);

    // calculate hand rank for player 2's top row 
    var p2toprow = [];
    for (i = 10; i < 13; i++) {
        var tcard = document.getElementById(AI_pos_c[i]).childNodes[0]; // extract card from each div
        p2toprow.push(tcard);
    }
    var p2toprank = getHandRank(p2toprow);

    /*
	scoringAlertString = "[AI] Bottom Rank: " + p2bottomrank + ", Middle Rank: " + p2middlerank + ", Top Rank: " + p2toprank;	
	alert(scoringAlertString);
	*/

    // temporary simplified points system 
    // bottom
    if (p1toprank > p2toprank) {
        rowScoresArr[0] = p1toprank;
        rowScoresArr[3] = -p1toprank;
    } else {
        rowScoresArr[0] = -p2toprank;
        rowScoresArr[3] = p2toprank;
    }

    // middle
    if (p1middlerank > p2middlerank) {
        rowScoresArr[1] = p1middlerank;
        rowScoresArr[4] = -p1middlerank;
    } else {
        rowScoresArr[1] = -p2middlerank;
        rowScoresArr[4] = p2middlerank;
    }

    // top
    if (p1bottomrank > p2bottomrank) {
        rowScoresArr[2] = p1bottomrank;
        rowScoresArr[5] = -p1bottomrank;
    } else {
        rowScoresArr[2] = -p2bottomrank;
        rowScoresArr[5] = p2bottomrank;
    }


    p1score += rowScoresArr[0] + rowScoresArr[1] + rowScoresArr[2]; // player's top middle bottom
    p2score += rowScoresArr[3] + rowScoresArr[4] + rowScoresArr[5]; // AI's top middle bottom

    // modify score fields to reflect row scores
    var temp, colourString, textString, count = 0;
    // iterate through every row and update score containers
    // Display positive scores in green and negative in red
    for (pID = 1; pID <= 2; pID++) {
        for (rowID = 1; rowID <= 3; rowID++) {
            textString = "p" + pID + "_text" + rowID;
            colourString = chooseScoreColour(rowScoresArr[count]);
            temp = document.getElementById(textString);
            temp.innerHTML = rowScoresArr[count];
            temp.style.color = colourString;
            count++;
        }
    }

    // change player labels to reflect their total scores
    playerLabels();
}

function chooseScoreColour(num) {
    if (num >= 0) {
        return "#00c303"; //green for positive
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

function playerLabels() {
    var temp1, temp2;
    temp1 = player1 + " (" + p1score + ")";
    temp2 = player2 + " (" + p2score + ")";

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
        return "null";
    }
}

// main function for handling the AI - pass here once the player is done
function AI_main() {

    // temporary naive algorithm - random card placements

    AI_placement_counter++;

    // special case - first round
    if (playButtonCounter == 1 || (playButtonCounter == 2 && playerFirst == true)) {
        AI_positions = shuffle(AI_positions); // shuffle positions for random card placements
        for (i = 0; i < 5; i++) {
            var card = dealCard();
            var cardimg = document.createElement("img");
            cardimg.src = card.src;
            cardimg.name = card.name;
            cardimg.width = 109;
            cardimg.height = 150;

            document.getElementById(AI_positions[i]).appendChild(cardimg); // place img in div
            AI_cards.splice(i, 0, cardimg); // append card to appropriate position in array
        }
    }

    // general case
    else {
        var card = dealCard();
        var cardimg = document.createElement("img");
        cardimg.src = card.src;
        cardimg.name = card.name;
        cardimg.style.width = '109px';
        cardimg.style.height = '150px';

        document.getElementById(AI_positions[3 + AI_placement_counter]).appendChild(cardimg); // place img in div
        AI_cards.splice((3 + AI_placement_counter), 0, cardimg); // append card to appropriate position in array
    }
}

// © 2015 Alastair Kerr. All rights reserved.
// formatted with http://jsbeautifier.org/