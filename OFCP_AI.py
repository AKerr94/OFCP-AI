# basis for MCTS
# very simple random monte carlo simulations
# TODO: integrate with scoring system to produce valid, useable results
#       produce tree from simulations 

from random import randint

class Node:
    ''' A node in the game tree '''
    def __init__(self):
        #self.moves_to_try = ?.findMoves()
        pass

def simulateGame(game_state, row, card):
    return randint(0,50) # return random score between 0-50 inclusive for test purposes
        
def chooseMove(game_state, card, iterations):
    ''' takes game state and dealt card as input, produces tree from monte carlo
    simulations and returns optimal move - 1 for bottom, 2 for middle, 3 for top '''
    predicted_scores = [ [1,0], [2,0], [3,0] ] # first index: row, second index: total score
    for i in range (1,iterations):
        row = randint(1,3) 
        predicted_scores[row -1][1] = simulateGame(game_state, row, card)
        
    t1 = predicted_scores[0][1]
    t2 = predicted_scores[1][1]
    t3 = predicted_scores[2][1]
    
    if t1 > t2 and t1 > t3:
        return 1
    elif t2 > t1 and t2 > t3:
        return 2
    elif t3 > t1 and t3 > t2:
        return 3
    else:
        return randint(1,3)

if __name__ == "__main__":
    row_counts = [0,0,0]
    for i in range(1,100):
        chosen_row = chooseMove(None,None,1000)
        row_counts[chosen_row -1] += 1
    print row_counts
    #print "This is a helper script implementing MCTS for OFCP.\n\
    #To use import module externally."
