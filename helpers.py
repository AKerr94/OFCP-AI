# -*- coding: utf-8 -*-

import hands

rank_dic1 = {'10':'T', '11':'J', '12':'Q', '13':'K', '14':'A'} # numerical value -> char value
rank_dic2 = {'T':'10', 'J':'11', 'Q':'12', 'K':'13', 'A':'14'} # char value -> numerical value

def reformat_hand_xyy_yx(hand, numCards):
    ''' Hand passed in as string (suit)(rank as 2 chars) *5. 
        Return hand as string(rank as 1 char)(suit) *5 

        Converts 5 card hand to valid string format for use in "kmanley"'s poker hand evaluator
        Can also convert 3 card hand to valid string, if value of 3 is passed as 2nd parameter
        
        e.g. c09c10c11c12c13 -> 9CTCJCQCKC
        e.g. h01s01c05h05d12 -> AHAS5C5HQD '''
        
    if (numCards == 5 or numCards == 3):
        
        def getKey(item): # returns rank for use in sorting
            return int(item[0])

        try:
            hand = str(hand)
        except:
            pass # caught by if statement below
        
        if (type(hand) is not str):
            print "Invalid hand (required type = string), " + str(hand) + " is " + str(type(hand)) + "\n"
            return None
            
        if ( (len(hand) != 15 and numCards == 5) or (len(hand) != 9 and numCards == 3) ):
            print "Invalid Hand:", hand, ". Required format e.g: c09c10c11c12c13 (clubs straight flush 9->King)\n"
            return None
        
        try:
            #print ('Reading in hand: ' + str(hand) + '. Reformatting now...' )
            cards_list = []
            formatted_hand = ""
            
            for i in xrange(0,numCards*3,3):            # decode string to get each card name. index 0 -> 14 step 3
                suit = hand[i]
                rank_p1 = hand[i+1]
                rank_p2 = hand[i+2]
                
                suit = suit.upper()             # evaluator needs suit as uppercase char
                
                if suit not in ('H','D','S','C'):
                    print "Invalid suit! Expected H, D, S or C. Actual:", suit
                    return None
                
                rank = int(rank_p1 + rank_p2)   # get numerical value for rank
                if ( rank < 1 or rank > 14):
                    print "Invalid rank. Accepted range 1-14.\n"
                    return None
                    
                if rank == 1:                   # ace is high, convert 1 -> 14 
                    rank = 14

                cards_list.append( [str(rank), str(suit)] )      # list of lists - inner lists comprising of rank & suit for a card 

            
            #print cards_list, ": Formatted"
            cards_list = sorted( cards_list, key=getKey) # sort array based on key (rank value)
            #print cards_list, ": Sorted\n"
            
            for card in cards_list:
                try:                            # converts numerical Ten, Jack, Queen, King, Ace -> appropriate char (T,J,Q,K,A)
                    card[0] = rank_dic1[card[0]]
                except:
                    pass                        # ranks deuce -> nine do not need any conversion 
                    
                formatted_hand += card[0] + card[1]
            
            return formatted_hand
            
        except: 
            print "An error occured! Ensure a valid hand was passed."
            return None
    
    print "Invalid parameters. Parameter 1: Hand string, Parameter 2: Num cards (3 or 5)"
    return None # invalid supplied parameters
    
        
def scoring_helper(game_state):
    ''' Reads game state and works out winner for each row, validates hands and calculates appropriate royalties '''
    
    def decode_state_hand(min,max,hands_list,numCards):
        ''' used to read cards for rows and call formatter. Returns updated hands_list '''
        
        t1 = ""
        t2 = ""
        for i in range (min,max):
            t1 += str( game_state['properties1']['cards']['items']['position'+str(i)] ) # take card info for p1's row
            t2 += str( game_state['properties2']['cards']['items']['position'+str(i)] ) # take card info for p2's row
        hands_list.append([reformat_hand_xyy_yx(t1,numCards)])
        hands_list.append([reformat_hand_xyy_yx(t2,numCards)])
        
        return hands_list
      
    def calculate_royalties(hand_tuple,row):
        ''' hand_tuple in format as read from hand evaluator.
            row = 'bottom', 'middle' or 'top'
            
            returns appropriate royalty based on row, hand rank and value 
        '''
        
        # check if the hand is fouled (indicated by a score of -1). If so return immediately 
        if (hand_tuple == -1):
            return 0
        
        # rankings: 1 High Card, 2 Pair, 3 Two Pair, 4 Three of a kind, 5 Straight, 6 Flush, 7 Full House, 8 4 of a Kind, 9 Straight Flush 
        
        if ( row == 'bottom' ):
            royalties_dic = {5:2, 6:4, 7:6, 8:10, 9:15} # straight:2, flush:4, full house: 6, quads: 10, straight flush: 15
            try: 
                royalty = royalties_dic[hand_tuple[0]]
                if royalty == 15 and hand_tuple[1] == 14:
                    royalty = 25 # royal flush 
            except:
                return 0
            return royalty
            
        elif ( row == 'middle' ):
            royalties_dic = {4:2, 5:4, 6:8, 7:12, 8:20, 9:30} # 3ofakind:2, straight:4, flush:8, full house: 12, quads: 20, straight flush: 30
            try:
                royalty = royalties_dic[hand_tuple[0]]
                if royalty == 15 and hand_tuple[1] == 14:
                    royalty = 50 # royal flush 
            except:
                return 0
            return royalty 
        
        elif ( row == 'top' ):
            try:
                if hand_tuple[0] == 4:      # trips 
                    royalties_dic = {2:10,3:11,4:12,5:13,6:14,7:15,8:16,9:17,10:18,11:19,12:20,13:21,14:22}
                    royalty = royalties_dic[hand_tuple[1]]
                elif hand_tuple[0] == 2:    # pair
                    royalties_dic = {6:1,7:2,8:3,9:4,10:5,11:6,12:7,13:8,14:9}
                    royalty = royalties_dic[hand_tuple[1]]
                else:
                    return 0
                return royalty
            except:
                return 0
            
        else:
            print "Invalid parameters. Row id req 'top' 'middle' or 'bottom"
            return None 
    
    def validate_hands(players_row_scores):
        ''' validate hands. If a player has fouled set scores to -1 '''
        if not ( (players_row_scores[0] > players_row_scores[1]) and (players_row_scores[1] > players_row_scores[2]) ):
            #print "\nA player fouled! Hand:", players_row_scores
            return 0
        return players_row_scores
         
    # work out scores for 5 card hands (Bottom and middle rows)     
            
    hands_list = []
    hands_list = decode_state_hand(1,6,hands_list,5)    # append bottom
    hands_list = decode_state_hand(6,11,hands_list,5)   # append middle
    hands_list = decode_state_hand(11,14,hands_list,3)  # append top
    
    scores = []                     # format: p1 bot, p2 bot, p1 mid, p2 mid, p1 top, p2 top. Type: score tuples
    classifications = []            # format: p1 bot, p2 bot, p1 mid, p2 mid, p1 top, p2 top. Type: Strings
    
    count = 0
    for poker_hand in hands_list:   # calculate scores and classifications for each hand
        if count < 4:               # evaluate 5 card hands
            scores.append( hands.score_5(poker_hand[0]) )
            #classifications.append( hands.classify_5(poker_hand[0]) )
            
        else:                       # evaluate 3 card hands
            result = simple_3card_evaluator(poker_hand[0])
            scores.append(result)
            #classifications.append(classify_3(result))
                
        count += 1  
        
    # validate each hand. If a player fouls set their scores to -1    
    p1invalid = False
    p2invalid = False
    for i in range(0,2):        # validate player 1 then validate player 2
        handisvalid = validate_hands([scores[0+i],scores[2+i],scores[4+i]])
        if(handisvalid == 0):
            if (i == 0):
                scores = [(-1),scores[1],(-1),scores[3],(-1),scores[5]]
                p1invalid = True
            else:
                scores = [scores[0],(-1),scores[2],(-1),scores[4],(-1)]
                p2invalid = True
    
    #print "\nSCORES: ", scores
    
    scores_final = []               # keep track of who wins which row and what royalties to give them 
                                    # List Structure [ [winner id(1 or 2), royalty] ]
                                    # e.g. [ [1,6], [2,2], [1,0] ]  =  p1 wins bot with +6, p2 wins mid with +2, p1 wins top with no royalty
    
    p1_royalty = 0
    p2_royalty = 0
    winnerid = 0
    
    if scores[0] > scores[1]:       # player 1 wins bottom
        winnerid = 1
    elif scores[0] < scores[1]:     # player 2 wins bottom
        winnerid = 2
    else:
        winnerid = 0
    
    p1_royalty = calculate_royalties( scores[0], 'bottom' )
    p2_royalty = calculate_royalties( scores[1], 'bottom' )
    scores_final.append([winnerid, p1_royalty, p2_royalty])
    
    if scores[2] > scores[3]:       # player 1 wins middle
        winnerid = 1
    elif scores[2] < scores[3]:     # player 2 wins middle
        winnerid = 2
    else:
        winnerid = 0
    
    p1_royalty = calculate_royalties( scores[2], 'middle' )
    p2_royalty = calculate_royalties( scores[3], 'middle' )
    scores_final.append([winnerid, p1_royalty, p2_royalty])
    
    if scores[4] > scores[5]:       # player 1 wins top
        winnerid = 1
    elif scores[4] < scores[5]:     # player 2 wins top
        winnerid = 2
    else:
        winnerid = 0
    
    p1_royalty = calculate_royalties( scores[4], 'top' )
    p2_royalty = calculate_royalties( scores[5], 'top' )
    scores_final.append([winnerid, p1_royalty, p2_royalty])
    
    scores_final.append([p1invalid,p2invalid]) 
        
    #print scores_final, '\n', hands_list, '\n', classifications
    
    return scores_final

def scores_arr_to_int(scores):
    '''
    scores: takes scores_array from scoring_helper
    works out what player 1's score is and returns this
    (p2's score is the inverse)
    '''

    #print "\nScoring a board! Scores array:", scores
    
    p1score = 0
    p2score = 0
    p1_multiplier = 1
    p2_multiplier = 1
    if scores[3][0] == True: # p1 fouls, scores 0
        p1_multiplier = 0
    if scores[3][1] == True: # p2 fouls, scores 0
        p2_multiplier = 0

    # handle points for winning rows
    p1wins = 0
    p2wins = 0
    for i in range(0,3):
        if scores[i][0] == 2:
            p2wins += 1
        elif scores[i][0] == 1:
            p1wins += 1

    if p2wins == 3:
        p2score += 6
        p1score += -6
    elif p1wins == 3:
        p2score += -6
        p1score += 6
    else:
        p2score += (p2wins - p1wins)
        p1score += (p1wins - p2wins)

    # add extra points for royalties
    p1score += (scores[0][1] + scores[1][1] + scores[2][1]) * p1_multiplier
    p2score += (scores[0][2] + scores[1][2] + scores[2][2]) * p2_multiplier

    #print "Helpers scores:" 
    #print "p1 score:", p1score, "wins:", p1wins, "multiplier:", p1_multiplier
    #print "p2 score:", p2score, "wins:", p2wins, "multiplier:", p2_multiplier
    #print "from:", scores
    
    # finalise scores
    if p1score > p2score:
        p2score = -p1score
    elif p1score < p2score:
        p1score = - p2score
    
    #print "Final score: Player 1 -", p1score, ", Computer:", p2score
    
    return p1score

def classify_3(eval_result):
    ''' takes result tuple from simple_3card_evaluator output and classifies hand
        e.g. 'Three of a Kind Ks', 'Pair of As, 7 kicker' '''
    
    c3_dic = {4:'Three of a Kind ', 2:'Pair of ', 1:'High Card: '}
    hand_name = c3_dic[eval_result[0]]
    if eval_result[0] == 4:
        hand_name += str(eval_result[1]) + 's '
    elif eval_result[0] == 2:
        hand_name += str(eval_result[1]) + 's, ' + str(eval_result[2]) + ' kicker.'
    elif eval_result[0] == 1:
        hand_name += str(eval_result[1]) + ', kickers: ' + str(eval_result[2]) + ', ' + str(eval_result[3])
    else:
        print "Error! Invalid tuple?..."
    
    return hand_name
    
    
def simple_3card_evaluator(hand):
    ''' takes in 3 card poker hand and evaluates for high card, pair or three of a kind '''
    
    def generate_histogram(hand):
        ''' use histogram approach - map frequency of each card rank to check for pairs, trips etc.
        hist [card x][0] = card x's rank value, [card x][1] = card x's rank frequency '''
        
        histogram = [
            [2, 0],     # Deuce
            [3, 0],     # 3
            [4, 0],     # 4
            [5, 0],     # 5
            [6, 0],     # 6
            [7, 0],     # 7
            [8, 0],     # 8
            [9, 0],     # 9
            [10, 0],    # 10
            [11, 0],    # Jack
            [12, 0],    # Queen
            [13, 0],    # King
            [14, 0]     # Ace
        ]
        
        # strip hand name to get rank and then update frequencies in histogram
        ranks = [0,0,0,0,0]
        for i in xrange (0,5,2):
            try:
                ranks[i] = rank_dic2[hand[i]]    # convert TJQKA -> number  
            except:
                ranks[i] = hand[i]
                
            try:
                temp = int(ranks[i])
            except:
                print "Invalid value! ", hand[i], "could not be converted to int.\n"
                return None
                
            histogram[temp - 2][1] += 1 # increment frequency for appropriate rank 
        
        return histogram 
    
    #print hand
    hist = generate_histogram(hand)
    
    if hist != None:
            
        highestfreq = 0    
        nexthighestfreq = 0
        highestfreqrank = 0
        nexthighestfreqrank = 0

        for item in hist:                       # first pass finds the highest frequency rank
            temp = item[1];
            if (temp >= highestfreq and item[0] >= highestfreqrank):
                highestfreq = temp
                highestfreqrank = item[0]

        if highestfreq < 3:                         # small optimisation - no need for second loop if there is a 3 of a kind
            for item in hist:                       # second pass finds second highest frequency rank 
                temp = item[1]
                if (temp >= nexthighestfreq and temp <= highestfreq and item[0] != highestfreqrank):
                    nexthighestfreq = temp
                    nexthighestfreqrank = item[0]
        
        if highestfreq == 1:                         # if high card, we need to locate third kicker 
            for item in hist:
                if item[0] not in (highestfreqrank, nexthighestfreqrank) and item[1] > 0:
                    thirdkicker = item[0]
                    break

                    
        if (highestfreq == 3):
            thisrank = 4 # Three of a Kind
            return (4,highestfreqrank)
            
        elif (highestfreq == 2):
            thisrank = 2 # Pair
            return (2,highestfreqrank,nexthighestfreqrank)
            
        else:
            thisrank = 1 # High Card
            return (1,highestfreqrank,nexthighestfreqrank, thirdkicker)
    
    else:
        return None
    
        
if __name__ == "__main__":
    print "helper functions: import to use"
    
# © 2015 Alastair Kerr