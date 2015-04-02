import cherrypy
import json
import hands 
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
                ef.write(str(datetime.now()) + ': Invalid JSON error.')
                return None
        f = open('test_output.txt', 'w')
       
        hand_string = ''
        for i in range (1,6):
                hand_string += game_state['properties1']['cards']['items']['position'+str(i)] # take card info for p1 bottom row 
        f.write('Hand String: ' + hand_string + '\n' +  hands.classify_5(hand_string))
        
        f.close()
        return '{}'.format(game_state)
        
    def server_hands(self, **params):
        # catch invalid JSON 
        try:
                game_state = json.loads(params['game-state']) # loads as dictionary 
        except: 
                ef = open('error_log.txt','a')
                ef.write(str(datetime.now()) + ': Invalid JSON error.')
                return None
        
        # handle game state stuff here - send to function for hand eval's, AI simulation etc.... 
        
        
        
        return '{}'.format(game_state)
        output = []
        for card in game_state['cards']:
                output.append(card['value'])
                
        db_user = application_config['database_connection']['username']
                
        return ''.join(output)
        
        
        
        
    index.exposed = True
    server_hands.exposed = True
    eval_one_hand_test.exposed = True

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
