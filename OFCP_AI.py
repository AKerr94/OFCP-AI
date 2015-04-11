# basis for MCTS
# very simple random monte carlo simulations
# TODO: integrate with scoring system to produce valid, usable results
#       produce tree from simulations 

from random import randint
import helpers

number_top = 0 # keep track of cards placed top. When this reaches 3 prevent any more 

class Node:
    ''' A node in the game tree '''
    def __init__(self):
        #self.moves_to_try = ?.findMoves()
        pass

def simulateGame(game_state, row, card):
    ''' takes in game state and chosen row to place given card in. 
    randomly simulates rest of game and returns score '''
    return randint(0,50) # return random score between 0-50 inclusive for test purposes
        
def chooseMove(game_state, card, iterations):
    ''' takes game state and dealt card as input, produces tree from monte carlo
    simulations and returns optimal move - 1 for bottom, 2 for middle, 3 for top '''
    
    if type(card) == type([]): # calculate first 5 cards to place
        if (len(card) == 5):
            moves = []
            for c in card:
                moves.append(chooseMove(game_state, c, iterations)) # store recommend row id placement for each card c 
            print moves
            return moves
        else:
            print "Invalid amount of cards - need 5!"
            return None
    
    elif type(card) == type('') and len(card) == 3: # calculate 1 card placement
        predicted_scores = [ [1,0], [2,0], [3,0] ] # first index: row, second index: total score
        for i in range (1,iterations):
            row = randint(1,3)  # select a random row 
            predicted_scores[row -1][1] = simulateGame(game_state, row, card) #then get estimated score for simulated game with card placed in that row
            
        t1 = predicted_scores[0][1]
        t2 = predicted_scores[1][1]
        t3 = predicted_scores[2][1]

        global number_top
        
        # use slight weighting so that preference for placements is bottom > middle > top
        if t1 >= t2:
            if t1 >= t3:
                return 1             #bottom
            elif number_top < 3:
                number_top += 1
                return 3             #top    
            else:
                return randint(1,2)
            
        elif t2 > t1:
            if t2 >= t3:
                return 2             #middle
            elif number_top < 3:
                number_top += 1
                return 3             #top
            else:
                return randint(1,2)
                
        elif t3 > t1:
            if t3 > t2 and number_top < 3:
                number_top += 1
                return 3             #top
            else:
                return 2             #middle
                
        else:                        #shouldn't reach here
            return randint(1,3)
    
    else:
        print "Invalid cards. Need type: String e.g. 'AS' (ace of spades)"
        return None

def place_one(game_state, card, iterations):
    ''' takes game_state, card and iterations as parameters
    determines optimal placement for card given game state '''
    
    row_counts = [0,0,0]
    x = 1
    global number_top
    for i in range(0,x):  # run x simulations of iterations each 
        number_top = 0 # reset
        chosen_row = chooseMove(game_state, card, iterations)
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

def place_five_initial(game_state, cards, iterations):
    ''' takes game_state, cards array and iterations as parameters
    determines optimal placement for cards given game state '''
    count_row_1 = 0
    count_row_2 = 0
    count_row_3 = 0 
    
    illegal_moves = 0
    global number_top
    
    #row_counts = [0,0,0]
    x = 1
    for i in range(0,x):  # # run x simulations of iterations each 
        card_placements = [0,0,0,0,0]
        number_top = 0 # reset num top
        
        chosen_rows = chooseMove(game_state, cards, iterations)
        
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

    print "Test run: Modelling 100 simulations of placing cards!...\n"
    user_choice = raw_input(" Type 0 to test a single card,\n Type 1 to test 5 card initial placement.\n\
    Anything else: exit.\n")
    
    ### exit ###
    if user_choice not in ['0','1']:
        print "Exiting now..."
        quit()
    
    times_to_run = raw_input("How many test would you like to run? \n")
    
    valid = False
    try:
        times_to_run = int(times_to_run)
        valid = True 
    except:
        print "Invalid input! Required type: integer.\n"
    
    #### 1 card test ####
    if user_choice == "0" and valid == True:
        game_state = None
        card = 's01' # example test card (ace of spades)
        num_iterations = 500
        for i in range(0, times_to_run):
            chosenrow = place_one(game_state, card, num_iterations)
            print "Recommendation: Place card in", chosenrow, "row!"
    
    
    #### 5 card test ####
    elif user_choice == "1" and valid == True:
        
        game_state = None
        cards = ['s01', 'd01', 'h01', 'c10', 'd05']  # example test cards 
        num_iterations = 500
        placements_array = []
        for i in range(0, times_to_run):
            placements_array.append( place_five_initial(game_state, cards, num_iterations) )
        print "Simulations results: ", placements_array
    
    
    print "\nThis is a helper script implementing MCTS for OFCP.\n\
    Intended use: import module externally.\n"
    
    raw_input("Press Enter to continue...")
