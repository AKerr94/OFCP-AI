# -*- coding: utf-8 -*-

import cherrypy
import json
import hands 
import helpers
import OFCP_AI
from datetime import datetime
import time
from pymongo import MongoClient
from bson.objectid import ObjectId
import pymongo
import db_backend
import config
import deck
#from config import application_config, cherrypy_config


class subpage(object):
        
    def eval_one_hand_test(self, **params): #test function. Classifies 1 poker hand 
        # catch invalid JSON 
        try:
                game_state = json.loads(params['game-state']) # loads as dictionary 
        except: 
                ef = open('error_log.txt','a')
                ef.write( '\n{} invalid json: {}'.format(datetime.now(), params) )
                raise cherrypy.HTTPError(403, "There was an error with the given game state.")
        f = open('test_output.txt', 'w')
       
        hand_string = ''
        for i in range (1,6):
                hand_string += game_state['properties1']['cards']['items']['position'+str(i)] # take card info for p1 bottom row 
        f.write('Hand String: ' + hand_string + '\n = ' +  hands.classify_5(hand_string) +
                '\n Score: ' + str(hands.score_5(hand_string)) )
        
        f.close()
        
        '''
        test_items = ( 'c05c06c07c08c09','s05c05h09s08d13','h13c01s03d05c07','invalid',100,'fakestring',('i','am','invalid'),'123456789112345' )
        for item in test_items:
            format_resp = helpers.reformat_hand_xyy_yx(item,5)
            if format_resp != None:
                print 'Formatted ' + str(item) + ' -> ' + str(format_resp) + '\n'
        '''
        
        return '{}'.format(game_state)
        
    def server_hands(self, **params):
        # catch invalid JSON 
        try:
                game_state = json.loads(params['game-state']) # loads as dictionary 
        except: 
                ef = open('error_log.txt','a')
                #ef.write(str(datetime.now()) + ': Invalid JSON error. \n ' + str(params) + '\n\n')
                ef.write( '\n{} invalid json: {}'.format(datetime.now(), params) )
                raise cherrypy.HTTPError(403, "There was an error with the given game state.")
        
        # handle game state stuff here - send to function for hand eval's, AI simulation etc....
        
        return '{}'.format(game_state)
        
        # dead code (for now)
        output = []
        for card in game_state['cards']:
                output.append(card['value'])
                
        db_user = application_config['database_connection']['username']
                
        return ''.join(output)
        
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
        Validates game state and updates changes
        '''
        try:
                game_state = json.loads(params['game-state']) # loads as dictionary
        except:
                ef = open('error_log.txt','a')
                ef.write( '\n{} invalid json: {}'.format(datetime.now(), params) )
                raise cherrypy.HTTPError(403, "There was an error with the given game state.")

        # compare game state passed to game state for db
        # if blank game state deal cards
        # update game state changes, call AI

        games = db_backend.get_database_collection()
        game_id = params['game-id']
        state =	games.find_one({'_id': ObjectId(game_id)})

        count = 0
        playerFirst = state["playerFirst"]
        for i in range(0,13):
            for j in range(0,2):
                if game_state['properties'+str(j+1)]['cards']['items']['position'+str(i+1)] is not None:
                    count += 1

        print game_state

        print "\n### COUNT:", count
        if playerFirst:
            if count == 0: # player's first turn
                cdeck = deck.Deck()
                cards = cdeck.deal_n(5)
                state['deck'] = {} # initialise deck dic within game state
                state['deck']['cards'] = cdeck.cards
                state['deck']['current-position'] = cdeck.current_position
                update = games.update({
                    '_id': ObjectId(game_id)
                    }, {
                    '$set': state
                })
                #games.update({'deck':{'cards':cdeck.cards,'current-position':cdeck.current_position}}, {"$set": POST}, upsert=True)

                return json.dumps(cards)
            if count == 5: # AI's first turn
                print "\n HELLO"


                print state['deck']['cards'],"of len",len(state['deck']['cards']), ", current pos:", state['deck']['current-position']
                cdeck = deck.Deck(state['deck']['cards'], state['deck']['current-position'])

                dealt_cards = cdeck.cards[:5]
                for i in range(1,14):
                    t = game_state['properties1']['cards']['items']['position'+str(i)]
                    if t is not None:
                        if t in dealt_cards:
                            dealt_cards.remove(t)
                            state['properties1']['cards']['items']['position'+str(i)] = t
                        else:
                            raise cherrypy.HTTPError(500, "Error in player's POSTed game state")

                cards = cdeck.deal_n(5)
                OFCP_AI.loop_elapsed = 0

                current_milli_time = lambda: int(round(time.time() * 1000))
                stime = current_milli_time()

                iterations_timer = 4500   # Sets time in ms to spend simulating games. As iterations increases diverges to optimal solution
                AI_placements = OFCP_AI.chooseMove(game_state,cards,iterations_timer)

                print "\nTime taken calculating 5 placements:", current_milli_time() - stime, "ms"

                print "Total time spent scoring hands: ", OFCP_AI.loop_elapsed, "ms"

                # count = 0
                # for placement in AI_placements: # update game state/ database
                #     print placement
                #     if placement == 1: # bottom
                #         for i in range(0,5):
                #             if state['properties2']['cards']['items']['position'+str(i+1)] is None:
                #                 state['properties2']['cards']['items']['position'+str(i+1)] = cards[count]
                #                 break
                #     elif placement == 2: # middle
                #         for i in range(5,10):
                #             if state['properties2']['cards']['items']['position'+str(i+1)] is None:
                #                 state['properties2']['cards']['items']['position'+str(i+1)] = cards[count]
                #                 break
                #     elif placement == 3: # top
                #         for i in range(10,13):
                #             if state['properties2']['cards']['items']['position'+str(i+1)] is None:
                #                 state['properties2']['cards']['items']['position'+str(i+1)] = cards[count]
                #                 break
                #     count += 1

                from itertools import izip

                for placement, card in izip(AI_placements, cards):
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
                    for i in range(start, end+1):
                        if state['properties2']['cards']['items']['position'+str(i)] is None:
                            state['properties2']['cards']['items']['position'+str(i)] = card
                            break

                # deal player's next card
                card = cdeck.deal_one()

                # update game state
                state['deck']['cards'] = cdeck.cards
                state['deck']['current-position'] = cdeck.current_position
                state['cardtoplace'] = card
                update = games.update({
                    '_id': ObjectId(game_id)
                    }, {
                    '$set': state
                })

                print "Stored game state in database:", state

                del state['deck'] # dont return deck info to frontend

                state.pop('_id', None)

                print "Returning state to player:", state

                return json.dumps(state)


        else:
            cdeck = Deck(game_state['deck']['cards'], game_state['deck']['current-position']) # recreates deck

            games.update(game_state)


    #index.exposed = False
    server_hands.exposed = False
    eval_one_hand_test.exposed = False
    ofc_backend.exposed = True
    calculate_scores.exposed = True
    AI_calculate_first_5.exposed = True
    AI_calculate_one.exposed = True

class Root(object):
    #make a subpage
    subpage = subpage()

    def play(self, game_id=None):
        if game_id is None:
            games = db_backend.get_database_collection()
            game_state = db_backend.make_state()

            game_id = str(games.insert(game_state))

            raise cherrypy.HTTPRedirect("/ofc/play/{}".format(game_id))

        games = db_backend.get_database_collection()
        game_state = games.find_one({'_id': ObjectId(game_id)})
        playerFirst = game_state['playerFirst']
        return render_template('OFCP_game.html', game_id=game_id, playerFirst=playerFirst)

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
