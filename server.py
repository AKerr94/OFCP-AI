# -*- coding: utf-8 -*-

import cherrypy
import json
import hands 
import helpers
import OFCP_AI
from datetime import datetime

from config import application_config, cherrypy_config

class subpage(object):

    def index(self):
        return render_template("page.html")
        
    def eval_one_hand_test(self, **params): #test function. Classifies 1 poker hand 
        # catch invalid JSON 
        try:
                game_state = json.loads(params['game-state']) # loads as dictionary 
        except: 
                ef = open('error_log.txt','a')
                ef.write(str(datetime.now()) + ': Invalid JSON error. \n ' + str(params) + '\n\n')
                return None
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
                ef.write(str(datetime.now()) + ': Invalid JSON error. \n ' + str(params) + '\n\n')
                return None
        
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
                ef.write(str(datetime.now()) + ': Invalid JSON error. \n ' + str(params) + '\n\n')
                return None
                
                
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
                ef.write(str(datetime.now()) + ': Invalid JSON error. \n ' + str(params) + '\n\n')
                return None
        
        # read in cards to be placed 
        cards = []
        for i in range(0,5):
            cards.append(str(game_state['properties2']['cards']['items']['card'+str(i+1)]))
        iterations = 1000   # as iterations increases diverges to optimal solution 
        AI_placements = OFCP_AI.chooseMove(game_state,cards,iterations)
        
        return json.dumps(AI_placements)
    
    def AI_calculate_one(self, **params):
        ''' calculate where AI should placed a given card '''
        try:
                game_state = json.loads(params['game-state']) # loads as dictionary 
        except: 
                ef = open('error_log.txt','a')
                ef.write(str(datetime.now()) + ': Invalid JSON error. \n ' + str(params) + '\n\n')
                return None
        
        card = str(game_state['properties2']['cards']['items']['card'])
        iterations = 1000
        AI_placement = OFCP_AI.chooseMove(game_state,card,iterations)
        
        return json.dumps(AI_placement)
    
    index.exposed = True
    server_hands.exposed = True
    eval_one_hand_test.exposed = True
    calculate_scores.exposed = True
    AI_calculate_first_5.exposed = True
    AI_calculate_one.exposed = True

class Root(object):
    #make a subpage
    subpage = subpage()

    def index(self):
        return 'Hello world'

    def test(self, name='freddie'):
        return "Hello {name}".format(name=name)

    #mark a function as exposed to make it into a page
    index.exposed = True
    test.exposed = True

def render_template(template, **kwargs):
    return jinja_env.get_template(template).render(**kwargs)

from jinja2 import Environment, FileSystemLoader
jinja_env = Environment(loader=FileSystemLoader(application_config['template_path']))
cherrypy.quickstart(Root(), '/', cherrypy_config)
