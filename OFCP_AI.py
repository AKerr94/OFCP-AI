__author__ = 'Alastair Kerr'
# -*- coding: utf-8 -*-

from random import randint
import random
import helpers
import hands
import copy 
import time
import itertools 
from datetime import datetime

num_top_first_count = 0  # ensure that initial 5 card placement doesn't put too many top (very unlikely but possible)

number_top = 0       # keep track of cards placed top. When this reaches 3 prevent any more
number_middle = 0    # max 5
number_bottom = 0    # max 5

deck = []            # random deck for simulations
placed_cards_s = []  # stores records of simulated placed cards

nullscoringhands = 0
scoringhands = 0
losinghands = 0
counthands = 0
zeroscorehands = 0

loop_elapsed = 0

rankmappingdic = {'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'T':10,'J':11,'Q':12,'K':13,'A':14}
backrankmappingdic = {2:'2',3:'3',4:'4',5:'5',6:'6',7:'7',8:'8',9:'9',10:'T',11:'J',12:'Q',13:'K',14:'A'}

def reset():
    ''' reset variables for a new round '''
    global num_top_first_count
    global deck
    global placed_cards_s
    
    num_top_first_count = 0
    deck = []
    placed_cards_s = []
        
def find_valid_moves(game_state):
    ''' reads game state and detects how many valid placements are available for each row '''
    global number_bottom
    global number_middle
    global number_top
    
    number_bottom = 0
    number_middle = 0
    number_top = 0
    
    for i in range(1,14):
        temp = game_state['properties2']['cards']['items']['position'+str(i)]
        if temp != None:
            if i <= 5:
                number_bottom += 1
            elif i <= 10:
                number_middle += 1
            elif i <= 13:
                number_top += 1

    return [number_bottom, number_middle, number_top]
    #print "Valid placements: Bottom", 5 - number_bottom, ", Middle", 5 - number_middle, ", Top", 3 - number_top, "\n"

def produce_deck_of_cards():
    ''' generates a standard deck of 52 cards. Ranks ace -> king; Suits hearts, diamonds, spades and clubs'''
    global deck
    deck = []
    suits = ["h", "d", "s", "c"]
    for suit in suits:
        for i in range(1,14):
            temp = suit
            if i < 10:
                temp += "0"
            temp += str(i)
            deck.append(temp)
    random.shuffle(deck)
    return deck

def prune_deck_of_cards(game_state):
    ''' prunes deck of cards - reads in game state and removes any cards that have already been played on the board '''
    global deck
    
    #print 'game_state\n' + str(game_state) + '\n'
    
    unavailable_cards = []
    for i in range(1,14):
        for j in range(1,3):
            temp = game_state['properties'+str(j)]['cards']['items']['position'+str(i)]
            if temp != None:
                unavailable_cards.append(temp)
    
    for x in unavailable_cards: # remove any occurrences of placed cards from the deck
        deck[:] = (value for value in deck if value != x)
    
    #print 'Pruned deck\n' + str(game_state)+'\n\n'
    
def simulateGame(game_state, row, card, bAppend, op_deck=None):
    ''' takes in game state and chosen row to place given card in if bAppend == True
    else if bAppend is false skip appending any specific card.
    randomly simulates rest of game and returns score '''
	
    gs_copy = copy.deepcopy(game_state) # deepcopy copies all elements including nested ones 
    if bAppend == True:
        gs_copy = simulate_append_card(gs_copy, row, card, True)    # append card to appropriate position in game state     
    prune_deck_of_cards(gs_copy)        
    
    #print gs_copy

    if op_deck is None:
        global deck     # get available cards for placement
        tdeck = deck[:]
        random.shuffle(tdeck)
    else:
        # use a specific passed deck (e.g. for consistent unit testing)
        tdeck = op_deck[:]
    
    # populate empty slots in game board with random cards
    for i in range(1,14):
        if gs_copy['properties2']['cards']['items']['position'+str(i)] == None:
            gs_copy['properties2']['cards']['items']['position'+str(i)] = tdeck.pop(0)
                    
        if gs_copy['properties1']['cards']['items']['position'+str(i)] == None:
            gs_copy['properties1']['cards']['items']['position'+str(i)] = tdeck.pop(0)
    

    current_milli_time = lambda: int(round(time.time() * 1000))
    stime2 = current_milli_time()
    
    scores = helpers.scoring_helper(gs_copy) # score game board 
    
    
    global loop_elapsed
    loop_elapsed += (current_milli_time() - stime2)
    
    p2score = (helpers.scores_arr_to_int(scores)) * -1 # function returns p1's score. Get the inverse of this for AI's EV
    
    global counthands
    counthands += 1
    
    if scores[3][1] == False or scores[3][0] == False: # only printing valid results (fouled simulated hands from both players omitted)

        if p2score > 0:
            global scoringhands
            scoringhands += 1
        elif p2score == 0:
            global zeroscorehands
            zeroscorehands += 1
        else:
            global losinghands
            losinghands += 1
    
    else:
        global nullscoringhands
        nullscoringhands += 1
        
    return p2score
    #return randint(0,50) # return random score between 0-50 inclusive for test purposes

def simulate_append_card(game_state, row, card, force_place):
    ''' pass in game_state + a card and destination row
    returns a modified game_state with that card added to that row '''

    global placed_cards_s
    global number_bottom
    global number_middle
    global number_top
    
    if card in placed_cards_s and force_place == False: # avoid duplicate placements 
        #print "AVOIDED PLACING A DUPLICATED", card + "."
        return game_state
    
    #print "Appending", card, "to row", row, "on board state:", str(game_state['properties2']['cards']['items']), '\n'
    
    if row == 1:
        for i in range(1,6):
            if game_state['properties2']['cards']['items']['position'+str(i)] == None:
                game_state['properties2']['cards']['items']['position'+str(i)] = card
                placed_cards_s.append(card)
                number_bottom += 1
                break
    
    elif row == 2:
        for i in range(6,11):
            if game_state['properties2']['cards']['items']['position'+str(i)] == None:
                game_state['properties2']['cards']['items']['position'+str(i)] = card
                placed_cards_s.append(card)
                number_middle += 1
                break

    elif row == 3:
        for i in range(11,14):
            if game_state['properties2']['cards']['items']['position'+str(i)] == None:
                game_state['properties2']['cards']['items']['position'+str(i)] = card
                placed_cards_s.append(card)
                number_top += 1
                break    
    
    else:
        print "Invalid row passed to simulate_append_card:\n", row
        return None
    
    #print "New AI board state:", str(game_state['properties2']['cards']['items']), '\n'
    return game_state
 
def produce_histogram(cards):
    ''' takes in cards as input e.g. ['AS','AD','7H','5C','5H']
    and returns histogram of ranks '''

    if len(cards) != 5:
        return None

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

    for i in range(0,5):
        try:
            temp = rankmappingdic[cards[i][0]]
            histogram[temp -2][1] += 1
        except:
            return None

    return histogram 

def place_5(game_state, cards, sim_timer, test_deck=None):
    ''' takes game_state, first 5 cards and allocated simulated time in ms as inputs.
    Aggregates scores for simulations of each permutation of the first possible placements 
    and returns an optimal placement as a list with index i = card i+1's allocated row
    e.g. return [1,1,2,2,3] = card 1 in row 1, card 2 in row 1, card 3 in row 2, card 4 in row 2, card 5 in row 3'''

    # if a test deck is passed assign it to global
    if test_deck != None:
        global deck
        deck = test_deck

    try:
        cdic = {cards[0]:1, cards[1]:2, cards[2]:3, cards[3]:4, cards[4]:5} # keep a permanent record of which card was which index

    except Exception:
        print "Invalid cards passed to place_5:", cards
        raise Exception

    print "\n####\nPlace_5:", cards, "\nSimulation Timer:", sim_timer, "ms.\n"

    cstring = ""
    for i in range(0,5):
        cstring += cards[i][0] + cards[i][1] + cards[i][2]
    print cstring

    cstring = helpers.reformat_hand_xyy_yx(cstring, 5)

    cformatted = []
    for i in xrange(0,10,2):
        tstr = cstring[i] + cstring[i+1]
        cformatted.append(tstr)

    # ctemp = 13 elements: 5 cards + 8 '' blanks (13 containers on a player's OFC board)
    ctemp = cards[:]
    for i in range(0,8):
        ctemp.append(None)
        
    pbot = set(itertools.combinations(ctemp,5)) # produce set of combinations for a 5 card row
    pbot = list(pbot)

    pmid = pbot[:] # combinations middle same as bottom

    ptop = set(itertools.combinations(ctemp,3)) # produce set of combinations for a 3 card row
    ptop = list(ptop)

    rowlists = [pbot, pmid, ptop]

    x = set(itertools.product(*rowlists)) # product of all possible row combinations

    # histogram maps frequency of each rank - used to prune states to reduce complexity when there are pairs, trips etc.
    # e.g. if we have pair of Aces removes states where these aces are not placed together
    # as it is very unlikely this would be an optimal placement
    hist = produce_histogram(cformatted)
    if hist == None:
        raise ValueError("Invalid values passed to produce_histogram")
    print "Histogram:", hist, "\n"

    highestfreq = 1 # look for quads or trips or a pair
    thatrank = None
    for item in hist:
        if item[1] > highestfreq:
            highestfreq = item[1]
            thatrank = item[0]

    nexthighestfreq = 1 
    secondrank = None
    if highestfreq < 4: # look for 2nd pair
        for item in hist:
            if item[1] > nexthighestfreq and item[0] is not thatrank:
                nexthighestfreq = item[1]
                secondrank = item[0]
    
    # look for straights and higher, return immediately if found
    cards1 = helpers.reformat_hand_xyy_yx("".join(cards), 5)
    hand_score = hands.score_5(cards1)
    if hand_score[0] >= 5:
        print "Found", hands.classify_5(cards1), ", choosing this in bottom row!"
        return [1,1,1,1,1]

    print "Highest Freq:",highestfreq,"Rank:",thatrank,"... Next Highest Freq:",nexthighestfreq,"Rank:",secondrank
    
    final = []
    # post-processing removes duplicates and validates state has all cards placed 
    for rows in x:
        duplicate = False
        c_count = 0
        for pos in rows[0]:
            if pos is not None:
                c_count += 1
                if pos in rows[1] or pos in rows[2]:
                    duplicate = True
                    break

        if not duplicate:
            for pos in rows[1]:
                if pos is not None:
                    c_count += 1
                    if pos in rows[2]:
                        duplicate = True
                        break
            for pos in rows[2]:
                if pos is not None:
                    c_count += 1
            if c_count == 5 and not duplicate:
                final.append(rows)

    final2 = []

    # 2nd round of post-processing if there are pairs, trips or quads - remove states that don't place these optimally
    if thatrank is not None:
        for state in final:
            counts = [0,0,0]
            for i in range(0,3):
                for x in state[i]:
                    if x is not None:
                        x = int(x[1] + x[2])
                        if x == 1:
                            x = 14
                        if x == thatrank:
                            counts[i] += 1

            if counts[0] < highestfreq and counts[1] < highestfreq and counts[2] < highestfreq: # not all placed together
                # remove this non-optimal state
                pass
            else:
                final2.append(state) # append this state which has all instances of thatrank paired together
    else:
        final2 = final
        
    final3 = []
    
    # 3rd round for any second pair
    if secondrank is not None:
         for state in final2:
            counts = [0,0,0]
            for i in range(0,3):
                for x in state[i]:
                    if x is not None:
                        x = int(x[1] + x[2])
                        if x == 1:
                            x = 14
                        if x == secondrank:
                            counts[i] += 1

            if counts[0] < nexthighestfreq and counts[1] < nexthighestfreq and counts[2] < nexthighestfreq: # not all placed together
                # remove this non-optimal state
                pass
            else:
                final3.append(state) # append this state which has all instances of thatrank paired together
    else:
        final3 = final2

    final4 = []    
        
    # 4th round - if there are still lots of states to consider, prune some sub-optimal placements e.g. all cards placed in middle 
    if len(final3) > 20:
        for state in final3:
            # remove states with an empty or full bottom row
            count = 0
            for item in state[0]:
                if item is not None:
                    count += 1
            if count > 0 and count < 5:
                count = 0
                for item in state[2]:
                    if item is not None:
                        count += 1
                # prune states which have dumped 3 cards top
                if count < 3:
                    final4.append(state)
    else:
        final4 = final3  
        
    final = final4
    final2 = None #wipe
    final3 = None #wipe
    final4 = None #wipe
                 
    s_count = 0
    for state in final:
        s_count += 1
        #print str(s_count) + ":", state
        
    print "Total states:", s_count
    
    current_milli_time = lambda: int(round(time.time() * 1000))
    
    # produce every possible initial game state dictionary for AI placements 
    state_id = 1
    states_scores = []
    random.shuffle(final)
    for state in final:
        gs_copy = copy.deepcopy(game_state)
        for item in state[0]: # bottom
            if item is not None:
                gs_copy = simulate_append_card(gs_copy, 1, item, False)
        for item in state[1]: # middle
            if item is not None:
                gs_copy = simulate_append_card(gs_copy, 2, item, False)
        for item in state[2]: # top
            if item is not None:
                gs_copy = simulate_append_card(gs_copy, 3, item, False)
        
        stime = current_milli_time()
        
        s_ev = 0
        iterations = 0
        while ( (current_milli_time() - stime) < (sim_timer / s_count) ): # each state gets an equal % of iteration time
            s_ev += simulateGame(gs_copy, None, None, False) # simulates random placements of rest of cards on game board and returns EV
            iterations += 1
        
        states_scores.append([state_id, s_ev, iterations])
        
        state_id += 1

    print "\nSTATE SCORES:", states_scores, "\n\n"   
        
    # find the state selection with the highest EV
    highest_ev = 0
    best_state_score = [0,0,0]
    count = 0
    for result in states_scores:
        print "State:", final[count], "-> Total score", result[1], "from", result[2], "iterations = EV:", "{0:.2f}".format(float(result[1])/float(result[2]))
        if float(result[1])/float(result[2]) > highest_ev: # total ev / iterations -> equal weighting between all states , find best score
            best_state_score = result
            highest_ev = result[1]
        count += 1
    
    print "\nBest state score:", best_state_score
    
    best_state_id = best_state_score[0]
    best_state = final[best_state_id -1]
        
    print "~best state got:", best_state    
    
    ftw = open("states_ev.txt", "w")
    s = ""
    for line in states_scores:
        s = "ID: " + str(line[0]) + ", EV: " + str(line[1]) + " from " + str(line[2]) + " iterations. "
        s += str(final[line[0]-1]) + "\n"
        ftw.write(s)
    ftw.close()
    
    brow = best_state[0]
    mrow = best_state[1]
    trow = best_state[2]
    
    r_placements = [0,0,0,0,0]
    
    for item in brow:
        if item is not None:
            t = cdic[item]
            r_placements[t -1] = 1 # bottom
    for item in mrow:
        if item is not None:
            t = cdic[item]
            r_placements[t -1] = 2 # middle
    for item in trow:
        if item is not None:
            t = cdic[item]
            r_placements[t -1] = 3 # top
    
    a = "\nPlacements: "
    for i in range(0,5):
        a += cards[i] + " -> Row " + str(r_placements[i])
        if i is not 4:
            a += ", "
        else:
            a += "."
    print a
    return r_placements 
    
  
def chooseMove(game_state, card, iterations_timer):
    ''' takes game state and dealt card as input, produces tree from monte carlo
    simulations and returns optimal move - 1 for bottom, 2 for middle, 3 for top '''

    global deck
    global num_top_first_count

    #### calculate 5 card placements ####
    if type(card) == type([]): 
        if (len(card) == 5):
            num_top_first_count = 0
            deck = produce_deck_of_cards()
            prune_deck_of_cards(game_state)
            moves = place_5(game_state, card, iterations_timer)
            return moves
        else:
            print "Invalid amount of cards - need 5!"
            return None
    
    #### calculate 1 card placement ####
    elif type(card) == type('') and len(card) == 3: 
    
        find_valid_moves(game_state)  # finds free spaces in each row and records counts in global vars number_bottom, number_middle, number_top

        print "\n=========== Calculcating for card", card, "==========="
        
        global number_top
        global number_middle
        global number_bottom
        
        print "Current cards placed top:", number_top, ", middle:",number_middle,",bottom:",number_bottom,"and original top:",num_top_first_count,"\n"
        
        # booleans - True if there are free slots in row 
        valid_bottom = True
        valid_middle = True
        valid_top = True
        valid_rows = [1,2,3]

        # if a row is full set bool to false - disallow more placements there
        if number_bottom == 5:
            valid_bottom = False
            valid_rows.remove(1)
        if number_middle == 5:
            valid_middle = False
            valid_rows.remove(2)
        if number_top == 3 or num_top_first_count == 3:
            valid_top = False
            valid_rows.remove(3)
        
        # if there is only one row with free slots save some processing time and just return that move without calculating scores
        if valid_bottom == False and valid_middle == False and valid_top == True:
            return 3 # top 
        elif valid_top == False and valid_bottom == False and valid_middle == True:
            return 2 # middle
        elif valid_middle == False and valid_top == False and valid_bottom == True:
            return 1 # bottom
        elif valid_bottom == False and valid_middle == False and valid_top == False:
            print "\nThere are no valid places to move! Check game state for duplicates/ errors!\nGame State:", game_state['properties2']
            f = open('error_log_invalid_rows.txt','a')
            f.write('{} No valid rows left!\n gamestate:{}\ncard: {}\nIterations Timer: {} \n'.format(datetime.now(), game_state, card, iterations_timer))
            f.close()
            #raw_input('waiting...')
            return None 
        
        deck = produce_deck_of_cards()
        prune_deck_of_cards(game_state)
          
        global nullscoringhands
        global scoringhands
        global counthands 
        global losinghands
        global zeroscorehands
        nullscoringhands = 0
        scoringhands = 0
        losinghands = 0
        counthands = 0
        zeroscorehands = 0
        
        predicted_scores = [ [1,0], [2,0], [3,0] ] # first index: row choice, second index: EV
        
        count = 0
        row_sim_counts = [[1,0],[2,0],[3,0]]
        
        current_milli_time = lambda: int(round(time.time() * 1000))
        stime = current_milli_time()
        
        while ( (current_milli_time() - stime) < iterations_timer ):
            #row = random.choice(valid_rows)
            for row in valid_rows:
                predicted_scores[row -1][1] += simulateGame(game_state, row, card, True) # get expected value for random simulated game with card placed in that row
                count += 1
                row_sim_counts[row -1][1] += 1

        print "\nSimulated", count, "games with asserted time limit of", iterations_timer, "ms. Actual time taken:", current_milli_time() - stime, "ms"
        
        print "There were", nullscoringhands, "null boards &", scoringhands, "positive scoring boards &", zeroscorehands, "zero-scoring boards &", losinghands, "losing boards. Total simulations:", counthands
        print "Final scores predictions~~\nEV Totals from placing",str(card),"in bottom:", str(predicted_scores[0][1]),"~ iter:",row_sim_counts[0][1],", middle:",str(predicted_scores[1][1]),"~ iter:", row_sim_counts[1][1],", top:",str(predicted_scores[2][1]),"~ iter:", row_sim_counts[2][1]
        
        #print str(game_state)
        
        # do not recommend placement in an invalid row
        if valid_bottom == False:
            predicted_scores[0][1] = -99999
        if valid_middle == False:
            predicted_scores[1][1] = -99999
        if valid_top == False:
            predicted_scores[2][1] = -99999
        
        t1 = predicted_scores[0][1]
        t2 = predicted_scores[1][1]
        t3 = predicted_scores[2][1]        
        
        # use slight weighting so that preference for placements is bottom > middle > top
        if t1 >= t2:
            if valid_bottom == True and t1 >= t3 :
                return 1             #bottom
            elif valid_top == True and t3 > t2:
                num_top_first_count += 1
                return 3             #top    
            elif valid_middle == True:
                return 2             #middle
            
        if t2 >= t1:
            if valid_middle == True and t2 >= t3:
                return 2             #middle
            elif valid_top == True:
                num_top_first_count += 1
                return 3             #top
                
        if t3 >= t1:
            if valid_top == True and t3 >= t2:
                num_top_first_count += 1
                return 3             #top
            elif valid_middle == True:
                return 2             #middle

        else:
            return None
    
    else:
        print "Invalid cards.", card, ". Need type: String e.g. 's01' (ace of spades)"
        return None

def place_one_test(game_state, card, iterations, timer):
    ''' takes game_state, card and iterations as parameters
    determines optimal placement for card given game state 
    
    Test function - server calls chooseMove function directly'''
    
    row_counts = [0,0,0]
    x = iterations
    global number_top
    for i in range(0,x):  # run x simulations of iterations each 
        number_top = 0 # reset
        chosen_row = chooseMove(game_state, card, timer)
        row_counts[chosen_row -1] += 1
    print row_counts
    
    chosenrow = 0
    if row_counts[0] >= row_counts[1]:
        if row_counts[0] >= row_counts[2]:
            chosenrow = 'Bottom'
        else:
            chosenrow = 'Top'
    
    elif row_counts[1] >=  row_counts[0]:
        if row_counts[1] >= row_counts[2]:
            chosenrow = 'Middle'
        else:
            chosenrow = 'Top'
    
    else:
        chosenrow = 'Top'
   
    return chosenrow

def place_five_initial_test(game_state, cards, iterations, timer):
    ''' takes game_state, cards array and iterations as parameters
    determines optimal placement for cards given game state 
    
    Test function - server calls chooseMove function directly'''
    
    count_row_1 = 0
    count_row_2 = 0
    count_row_3 = 0 
    
    illegal_moves = 0
    global number_top
    
    #row_counts = [0,0,0]
    x = iterations
    for i in range(0,x):  # # run x simulations of iterations each 
        card_placements = [0,0,0,0,0]
        number_top = 0 # reset num top
        
        chosen_rows = chooseMove(game_state, cards, timer)
        
        j = 0
        for row in chosen_rows:
            card_placements[j] += row
            j += 1
            
        cardid = 1
        t_count_top = 0
        for placement in card_placements:
            print "Place card", cardid, "in row", placement 
            if placement == 1:
                count_row_1 += 1
            elif placement == 2:
                count_row_2 += 1
            elif placement == 3:
                count_row_3 += 1
                t_count_top += 1
            else:
                print "AN EROR OCCURRED\n"
            cardid += 1
        
        if t_count_top > 3:
            print "Illegal amount of placements in top row!"
            illegal_moves += 1
        
        print "" #linebreak
    
    print "Row 1:", count_row_1, ", Row 2:", count_row_2, ", Row 3:", count_row_3
    
    print "There were", illegal_moves, "illegal recommended moves in this simulation.\n"
    
    return card_placements
    
    
if __name__ == "__main__":

    print "Test run: Modelling simulations of placing cards!...\n"
    user_choice = raw_input(" Type 0 to test a single card,\n Type 1 to test 5 card initial placement.\n\
    Anything else: exit.\n")
    
    ### exit ###
    if user_choice not in ['0','1']:
        print "Exiting now..."
        raw_input("Press Enter to continue...")
        quit()
    
    msValid = False
    itValid = False
    while (True):
        try:
            iteration_timer = raw_input("How many ms for simulations? \n")
            iteration_timer = int(iteration_timer)
            msValid = True
            iterations = raw_input("How many tests would you like to run? \n")
            iterations = int(iterations)
            itValid = True
            break
        except:
            if msValid == False:
                print "Invalid input:", iteration_timer, "Required type: integer. [input] ms\n"
            else:
                print "Invalid input:", iterations, "Required type: integer. [input] tests\n"
            input = raw_input("Try again Y/ Quit N: ")
            if input == 'n' or input == 'N':
                break

    if msValid == False or itValid == False:
        quit()

    # create empty game state
    game_state = {}
    game_state['properties1'] = {}
    game_state['properties1']['cards'] = {}
    game_state['properties1']['cards']['items'] = {}
    game_state['properties2'] = {}
    game_state['properties2']['cards'] = {}
    game_state['properties2']['cards']['items'] = {}

    for i in range(1,3):
        for j in range(1,14):
            game_state['properties'+str(i)]['cards']['items']['position'+str(j)] = None

    deck = produce_deck_of_cards()

    #### 1 card test ####
    if user_choice == "0":

        card = random.sample(deck, 1)
        for i in range(0, iterations):
            chosenrow = place_one_test(game_state, card, iteration_timer)
            print "Recommendation: Place card in", chosenrow, "row!"
    

    #### 5 card test ####
    elif user_choice == "1":

        placements_array = []
        for i in range(0, iterations):
            cards = random.sample(deck, 5)
            placements_array.append( place_five_initial_test(game_state, cards, 1, iteration_timer) )
        print "\n##############################\nSimulations results: "
        for i in range(0, len(placements_array)):
            print str(i) + ":", placements_array[i]
    
    print "\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
    print "OFCP AI script. Intended use: import module externally. Ran from command line for testing options.\n"
    
    raw_input("Press Enter to continue...")
