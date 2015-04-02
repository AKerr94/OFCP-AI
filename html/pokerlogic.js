var isFlush = false,
    isStraight = false;
var thisrank = 0;

// take 2 hands as parameters and return the best one
function compareHands(hand1, hand2) {
    var h1rank = getHandRank(hand1);
    var h2rank = getHandRank(hand2);
    if (h1rank > h2rank) {
        return hand1;
    } else if (h1rank < h2rank) {
        return hand2;
    }

    // TBD - if both hands are the same rank must check which is the best e.g. both pairs but h1 has 8s and h2 has 6s - h1 wins
    
    // TBD - work out kickers!! 
    
    return null;
}

// take a hand as a parameter and return its ranking #
function getHandRank(hand) {

    // initialise variables 
    thisrank = 0;
    isStraight = false;
    isFlush = false;

    // ranks: 0 high card, 1 pair, 2 two pair, 3 trips, 4 straight, 5 flush, 
    // 6 full house, 7 four of a kind, 8 straight flush, 9 royal flush

    // use histogram approach - map frequency of each card rank to check for pairs, trips etc.
    // hist [card ?][0] = card rank, [card ?][1] = rank frequency
    // histogram = [ [2,0],[3,0],[4,0],[5,0],[6,0],[7,0],[8,0],[9,0],[10,0],[11,0],[12,0],[13,0],[14,0] ]
    var hist = generateHistogram(hand);

    // check for pairs etc.
    
    var highestfreq = 0,        
        nexthighestfreq = 0,
        highestfreqrank = 0,
        nexthighestfreqrank = 0;

    for (i = 0; i < hist.length; i++) { // first pass finds the highest frequency rank
        var temp = hist[i][1];
        if (temp > highestfreq) {
            highestfreq = temp;
            highestfreqrank = hist[i][0];
        }
    }

    for (i = 0; i < hist.length; i++) { // second pass finds second highest frequency rank 
        var temp = hist[i][1];
        if (temp > nexthighestfreq && temp <= highestfreq && hist[i][0] != highestfreqrank) {
            nexthighestfreq = temp;
            nexthighestfreqrank = hist[i][0];
        }
    }

    if (highestfreq == 4) { // Quads
        thisrank = 7;
    } else if (highestfreq == 3) {
        if (nexthighestfreq == 2) {
            thisrank = 6; // Full House
        } else {
            thisrank = 3; // Three of a Kind
        }
    } else if (highestfreq == 2) {
        if (nexthighestfreq == 2) {
            thisrank = 2; // Two Pair
        } else {
            thisrank = 1; // Pair
        }
    }

    // check 5 card hands to see if they have a straight or flush
    else if (hand.length == 5) { // this is true for bottom and middle rows, but not top row 

        // check for flush
        isFlush = checkFlush(hand);

        // check for straight
        if (highestfreq == 1) { // if frequency of any card rank is > 1 there cannot be a straight
            isStraight = checkStraight(hand);
        }

        // now factor in straights and flushes....
        if (isFlush && isStraight) {
            thisrank = 8; // Straight Flush
        } else if (isFlush && thisrank < 5) {
            thisrank = 5; // Flush
        } else if (isStraight && thisrank < 4) {
            thisrank = 4; // Straight
        }
    }

    // else high card ( rank 0 )

    return thisrank;
}

function checkFlush(hand) {
    var suit1 = "",
        suit2 = "";

    // iterate through cards and check if each are the same suit
    for (i = 0; i < (hand.length) - 1; i++) {
        suit1 = hand[i].name.charAt(0); // first character indicates suit e.g. h = hearts
        suit2 = hand[i + 1].name.charAt(0);

        if (suit1 != suit2) {
            return false; // if any two cards have different suits return false
        }
    }
    return true;
}

function checkStraight(hand) {

    var temparray = [];

    for (i = 0; i < hand.length; i++) {
        var temp = "" + hand[i].name;
        temp = temp.substr(1); // strip leading suit character
        temp = parseInt(temp); //convert to int
        if (temp == 1) { // convert ace to correct rank 
            temp = 14;
        }
        temparray.push(temp);
    }

    temparray.sort(function(a, b) {
        return a - b
    });

    if (temparray[4] - temparray[0] == 4) { // if highest - lowest = 4 this is a straight
        return true;
    } else if (temparray[0] == 2 && temparray[1] == 3 && temparray[2] == 4 // special 'wheel' case - (ace is low)
        && temparray[3] == 5 && temparray[4] == 14) {

        return true;
    }

    return false;
}

function generateHistogram(hand) {

    // use histogram approach - map frequency of each card rank to check for pairs, trips etc.
    // hist [card ?][0] = card rank, [card ?][1] = rank frequency
    histogram = [
        [2, 0],
        [3, 0],
        [4, 0],
        [5, 0],
        [6, 0],
        [7, 0],
        [8, 0],
        [9, 0],
        [10, 0],
        [11, 0],
        [12, 0],
        [13, 0],
        [14, 0]
    ]

    // strip hand name to get rank and then update frequencies in histogram
    for (i = 0; i < hand.length; i++) {
        var temp = "" + hand[i].name;
        temp = temp.substr(1); // strip leading suit character
        temp = parseInt(temp); //convert to int
        if (temp == 1) { // convert ace to correct rank 
            temp = 14;
        }
        histogram[temp - 2][1] += 1; //increment frequency 
    }

    /*
    var alertstringhist = "";
	for (i = 0; i < histogram.length; i++) {
		alertstringhist += "Rank: " + histogram[i][0] + " , Frequency: " + histogram[i][1] + ".\n";
	}
	alert(alertstringhist);	*/

    return histogram;
}

// © 2015 Alastair Kerr. All rights reserved.
// formatted with http://jsbeautifier.org/