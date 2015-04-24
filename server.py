# -*- coding: utf-8 -*-

import cherrypy
import json
from datetime import datetime
import time
from pymongo import MongoClient
from bson.objectid import ObjectId
import pymongo
from itertools import izip

import db_backend
import config
import deck
import hands
import helpers
import OFCP_AI
#from config import application_config, cherrypy_config


class subpage(object):
        
    def calculate_scores(self, **params):
        ''' takes game_state as input. Converts hands, classifies them and returns the scores for each row '''
        try:
                game_state = json.loads(params['game-state']) # loads as dictionary 
        except: 
                ef = open('error_log.txt','a')
                ef.write( '\n{} invalid json: {}'.format(datetime.now(), params) )
                raise cherrypy.HTTPError(403, "There was an error with the given game state.")
                
                
        scores_array = helpers.scoring_helper(game_state)
        OFCP_AI.reset() # reset AI variables/ states 
        
        # scores_array format [ [winnerid, winners_bottom_royalty, losers_bottom_royalty], 
        #    [winnerid, winners_middle_royalty, losers_middle_royalty] , 
        #    [winnerid, winners_top_royalty, losers_top_royalty] ]
        
        print '\n   Back to server.py!\nScores -->', scores_array, '\n'     
        
        return json.dumps(scores_array)
    
    def AI_calculate_first_5(self, **params):
        ''' calculate where AI will place first 5 cards '''
        try:
                game_state = json.loads(params['game-state']) # loads as dictionary

        except: 
                ef = open('error_log.txt','a')
                ef.write( '\n{} invalid json: {}'.format(datetime.now(), params) )
                raise cherrypy.HTTPError(403, "There was an error with the given game state.")
        
        OFCP_AI.loop_elapsed = 0
        
        current_milli_time = lambda: int(round(time.time() * 1000))
        stime = current_milli_time()
        
        # read in cards to be placed 
        cards = []
        for i in range(0,5):
            cards.append(str(game_state['properties2']['cards']['items']['card'+str(i+1)]))
        iterations_timer = 4500   # Sets time in ms to spend simulating games. As iterations increases diverges to optimal solution 
        AI_placements = OFCP_AI.chooseMove(game_state,cards,iterations_timer)
        
        print "\nTime taken calculating 5 placements:", current_milli_time() - stime, "ms"
        
        print "Total time spent scoring hands: ", OFCP_AI.loop_elapsed, "ms"
        
        return json.dumps(AI_placements)
    
    def AI_calculate_one(self, **params):
        ''' calculate where AI should placed a given card '''
        try:
                game_state = json.loads(params['game-state']) # loads as dictionary 
        except: 
                ef = open('error_log.txt','a')
                ef.write( '\n{} invalid json: {}'.format(datetime.now(), params) )
                raise cherrypy.HTTPError(403, "There was an error with the given game state.")
        
        OFCP_AI.loop_elapsed = 0
        
        current_milli_time = lambda: int(round(time.time() * 1000))
        stime = current_milli_time()
        
        card = str(game_state['properties2']['cards']['items']['card'])
        iterations_timer = 3000
        AI_placement = OFCP_AI.chooseMove(game_state,card,iterations_timer)
        
        print "\nTime taken calculating 1 placement:", current_milli_time() - stime, "ms"
        
        print "Total time spent scoring hands: ", OFCP_AI.loop_elapsed, "ms"
        
        return json.dumps(AI_placement)

    def ofc_backend(self, **params):
        ''' This page handles the OFC backend
        Validates game state and updates changes in database
        Deals cards, calls AI script
        '''
        try:
                game_state = json.loads(params['game-state']) # loads as dictionary
        except:
                ef = open('error_log.txt','a')
                ef.write( '\n{} invalid json: {}'.format(datetime.now(), params) )
                raise cherrypy.HTTPError(403, "There was an error with the given game state.")

        # compare game state passed to game state from db - validate legitimacy
        # if blank game state deal cards
        # update game state changes, call AI

        current_milli_time = lambda: int(round(time.time() * 1000))

        # retrieve database for this game
        games = db_backend.get_database_collection()
        game_id = params['game-id']
        state =	games.find_one({'_id': ObjectId(game_id)})

        # find if player acted first this round and how many cards have been placed in order to work out current game position
        count = 0
        playerFirst = state["playerFirst"]
        for i in range(0,13):
            for j in range(0,2):
                if game_state['properties'+str(j+1)]['cards']['items']['position'+str(i+1)] is not None:
                    count += 1

        print game_state, "\nCards placed:", count

        if playerFirst:
            if count == 0: # player's first turn
                cdeck = deck.Deck() # creates deck
                cards = cdeck.deal_n(5)
                state['deck'] = {} # initialise deck dic within game state
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

            elif count == 5: # AI's first turn
                print "\nAI's first turn!\n"

                # remove first 5 cards entry from db now that these have been placed on the board
                del state['first5cards']

                #print "Deck:", state['deck']['cards'], "of length", len(state['deck']['cards']), ", current pos:", state['deck']['current-position']
                cdeck = deck.Deck(state['deck']['cards'], state['deck']['current-position'])

                # validate game state
                dealt_cards = cdeck.cards[:5]
                print "\nDealt cards:", dealt_cards
                for i in range(1,14):
                    t = game_state['properties1']['cards']['items']['position'+str(i)]
                    if t is not None:
                        if t in dealt_cards:
                            dealt_cards.remove(t)
                            state['properties1']['cards']['items']['position'+str(i)] = t
                        else:
                            raise cherrypy.HTTPError(500, "Error in player's POSTed game state: inconsistency with stored state in database!")

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

                print "\nStored game state in database:", state

                del state['deck'] # don't return deck info to frontend
                del state['_id']
                #state.pop('_id', None)

                print "\nReturning state to player:", state

                return json.dumps(state)

            elif count < 26:
                # general case for every other round after initial 5 placements by player and AI

                cdeck = deck.Deck(state['deck']['cards'], state['deck']['current-position'])

                # validate game state
                dealt_cards = cdeck.cards[:count]
                #print "\nDEALT CARDS:\n", dealt_cards, "\n"
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


    ofc_backend.exposed = True
    calculate_scores.exposed = True
    AI_calculate_first_5.exposed = True
    AI_calculate_one.exposed = True

class Root(object):
    #make a subpage
    subpage = subpage()

    def make_game(self, player_first=True, score =0 ):
        games = db_backend.get_database_collection()
        game_state = db_backend.make_state()

        game_state['playerFirst'] = player_first
        game_state['score'] = score

        game_id = str(games.insert(game_state))

        raise cherrypy.HTTPRedirect("/ofc/play/{}".format(game_id))

    def play(self, game_id=None, next=None):
        if game_id is None:
            self.make_game()

        games = db_backend.get_database_collection()
        game_state = games.find_one({'_id': ObjectId(game_id)})
        playerFirst = game_state['playerFirst']
        score = game_state['score']

        if next == 'next':
            print "\nserver thinks that the Score is:", score, "\n"
            self.make_game(player_first = not playerFirst, score=score)

        print game_state.keys()

        return render_template('OFCP_game.html', game_id=game_id, playerFirst=playerFirst, score=score, game_state=game_state)

    def index(self):
        raise cherrypy.HTTPRedirect("/ofc/play")

    def test(self, name='freddie'):
        return "Hello {name}".format(name=name)

    #mark a function as exposed to make it into a page
    index.exposed = True
    test.exposed = True
    play.exposed = True

def render_template(template, **kwargs):
    return jinja_env.get_template(template).render(**kwargs)

from jinja2 import Environment, FileSystemLoader
jinja_env = Environment(loader=FileSystemLoader(config.application_config['template_path']))
cherrypy.quickstart(Root(), '/', config.cherrypy_config)
