__author__ = 'Ali'

from bson.objectid import ObjectId
import json
import time
from itertools import izip

import deck
import hands
import helpers
import OFCP_AI
import db_backend

def handle_game_logic(game_state, game_id):
    '''
    Take in game state from frontend and game id as inputs - use game id to get record from database
    Compare game state passed to game state from db - validate legitimacy
    Based off who went first and cards placed so far determine next action e.g. deal cards, AI, score board
    Update game state changes and store in database, call AI helper functions to determine optimal play
    Return appropriate response to server e.g. updated game state, cards to be placed, scores array
    '''

    current_milli_time = lambda: int(round(time.time() * 1000))

    # retrieve database for this game
    games = db_backend.get_database_collection()
    state =	games.find_one({'_id': ObjectId(game_id)})

    # find if player acted first this round and how many cards have been placed in order to work out current game position
    count = 0
    playerFirst = state["playerFirst"]
    for i in range(0,13):
        for j in range(0,2):
            if game_state['properties'+str(j+1)]['cards']['items']['position'+str(i+1)] is not None:
                count += 1

    print "\nCurrent game state:\n", game_state, "\nCards placed:", count

    if playerFirst:

        # Special case for player's first turn
        if count == 0:
            cdeck = deck.Deck()     # creates deck
            cards = cdeck.deal_n(5)
            state['deck'] = {}      # initialise deck dic within game state
            state['deck']['cards'] = cdeck.cards
            state['deck']['current-position'] = cdeck.current_position

            state['first5cards'] = cards

            # update game state in database
            update = games.update({
                '_id': ObjectId(game_id)
                }, {
                '$set': state
            })

            return json.dumps(cards)

        # Special case for AI's first turn
        elif count == 5:

            # remove first 5 cards entry from db now that these have been placed on the board
            del state['first5cards']

            # recreate deck from deck info in database
            cdeck = deck.Deck(state['deck']['cards'], state['deck']['current-position'])

            # validate game state
            state = validate_state(cdeck, count, game_state, state)
            if state == 0:
                return 0 # raise cherrypy 500 error

            # calculate AI's first 5 card placements
            cards = cdeck.deal_n(5)
            OFCP_AI.loop_elapsed = 0

            stime = current_milli_time()

            iterations_timer = 4000   # Sets time in ms to spend simulating games. As iterations increases diverges to optimal solution
            AI_placements = OFCP_AI.chooseMove(game_state,cards,iterations_timer)

            print "\nTime taken calculating 5 placements:", current_milli_time() - stime, "ms"
            print "Total time spent scoring hands: ", OFCP_AI.loop_elapsed, "ms"

            # zip optimal placements -> appropriate cards, and update state dic with each placement
            for placement, card in izip(AI_placements, cards):
                # row 1 (bottom) pos 1-5, row 2 (middle) pos 6-10, row 3 (top) pos 11-13
                if placement == 1:
                    start = 1
                    end = 5
                elif placement == 2:
                    start = 6
                    end = 10
                    pass
                elif placement == 3:
                    start = 11
                    end = 13
                    pass
                else:
                    print "Invalid row returned from OFCP_AI.chooseMove(...):", AI_placement
                    return None

                for i in range(start, end+1):
                    if state['properties2']['cards']['items']['position'+str(i)] is None:
                        state['properties2']['cards']['items']['position'+str(i)] = card
                        break

            # deal player's next card
            card = cdeck.deal_one()

            # update game state with deck info
            state['deck']['cards'] = cdeck.cards
            state['deck']['current-position'] = cdeck.current_position

            # records game state in database
            state['cardtoplace'] = card
            update = games.update({
                '_id': ObjectId(game_id)
                }, {
                '$set': state
                ,'$unset': {
                'first5cards': 1
            }
            })

            #print "\nStored game state in database:", state

            del state['deck'] # don't return deck info to frontend
            del state['_id']
            #state.pop('_id', None)

            #print "\nReturning state to player:", state

            return json.dumps(state)

        # general case for every other round after initial 5 placements by player and AI
        elif count < 26:

            cdeck = deck.Deck(state['deck']['cards'], state['deck']['current-position'])

            # validate game state
            state = validate_state(cdeck, count, game_state, state)
            if state == 0:
                return 0 # raise cherrypy 500 error

            # AI's next move
            card = str(cdeck.deal_one())
            OFCP_AI.loop_elapsed = 0

            stime = current_milli_time()
            iterations_timer = 3000
            AI_placement = OFCP_AI.chooseMove(game_state,card,iterations_timer)

            print "\nTime taken calculating 1 placement:", current_milli_time() - stime, "ms"
            print "Total time spent scoring hands: ", OFCP_AI.loop_elapsed, "ms"

            if AI_placement == 1:
                start = 1
                end = 5
            elif AI_placement == 2:
                start = 6
                end = 10
                pass
            elif AI_placement == 3:
                start = 11
                end = 13
                pass
            else:
                print "Invalid row returned from OFCP_AI.chooseMove(...):", AI_placement
                return None

            for i in range(start, end+1):
                if state['properties2']['cards']['items']['position'+str(i)] is None:
                    state['properties2']['cards']['items']['position'+str(i)] = card
                    break

            # deal player's next card
            card = cdeck.deal_one()

            # update game state with deck info
            state['deck']['cards'] = cdeck.cards
            state['deck']['current-position'] = cdeck.current_position

            # records game state in database
            state['cardtoplace'] = card
            update = games.update({
                '_id': ObjectId(game_id)
                }, {
                '$set': state
            })

            print "\nStored game state in database:", state

            del state['deck'] # don't return deck info to frontend
            del state['_id']

            #print "\nReturning state to player:", state

            return json.dumps(state)

        else:
            # game over - score game board

            cdeck = deck.Deck(state['deck']['cards'], state['deck']['current-position'])

            # validate game state
            dealt_cards = cdeck.cards[:count]
            print "\nDEALT CARDS:\n", dealt_cards, "\n"
            for i in range(1,14):
                t = game_state['properties1']['cards']['items']['position'+str(i)]
                if t is not None:
                    if t in dealt_cards:
                        dealt_cards.remove(t)
                        state['properties1']['cards']['items']['position'+str(i)] = t
                    else:
                        print "Player posted game state:\n", game_state
                        print "\nError with card:", t, "with remaining deck:", dealt_cards
                        raise cherrypy.HTTPError(500, "Error in player's POSTed game state")

            # update game state with deck info
            state['deck']['cards'] = cdeck.cards
            state['deck']['current-position'] = cdeck.current_position

            # score game board
            scores_array = helpers.scoring_helper(game_state)

            # store p1's score in database
            state['score'] = helpers.scores_arr_to_int(scores_array)
            print "\nState score recorded as:", state['score'], "!\n"
            print "scores_array was", scores_array

            # records game state in database
            del state['cardtoplace']
            update = games.update({
                '_id': ObjectId(game_id)
                }, {
                '$set': state
            })

            OFCP_AI.reset() # reset AI variables/ states

            # scores_array format [ [winnerid, winners_bottom_royalty, losers_bottom_royalty],
            #    [winnerid, winners_middle_royalty, losers_middle_royalty] ,
            #    [winnerid, winners_top_royalty, losers_top_royalty] ]

            print '\n   Scores -->', scores_array, '\n'

            return json.dumps(scores_array)

    else:
        print "\n\nPlayer not First! ~Hello from server.py page ofc-backend!!\n"
        cdeck = Deck(game_state['deck']['cards'], game_state['deck']['current-position']) # recreates deck

        #games.update(game_state)

def validate_state(cdeck, dealt_count, game_state, state):
    '''
    validate game state
    '''
    dealt_cards = cdeck.cards[:dealt_count]
    for i in range(1,14):
        t = game_state['properties1']['cards']['items']['position'+str(i)]
        if t is not None:
            if t in dealt_cards:
                dealt_cards.remove(t)
                state['properties1']['cards']['items']['position'+str(i)] = t
            else:
                return 0 # will raise cherry py 500 error in server.py
    return state