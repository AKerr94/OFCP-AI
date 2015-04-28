__author__ = 'Alastair Kerr'
# -*- coding: utf-8 -*-

import cherrypy
import json
from datetime import datetime
import time
from pymongo import MongoClient
from bson.objectid import ObjectId
import pymongo

import db_backend
import config
import game_logic
#from config import application_config, cherrypy_config


class subpage(object):

    def ofc_backend(self, **params):
        ''' This page handles the OFC backend
        Loads game state and game id from POSTed params and passes to game_logic script
        return JSON dump of response to frontend
        '''
        try:
                game_state = json.loads(params['game-state']) # loads game state as dictionary
                game_id = params['game-id']
        except:
                ef = open('error_log.txt','a')
                ef.write( '\n{} invalid json: {}'.format(datetime.now(), params) )
                raise cherrypy.HTTPError(403, "There was an error loading the given game state.")

        response = game_logic.handle_game_logic(game_state, game_id)
        if response == 0:
            raise cherrypy.HTTPError(500, "Error in player's POSTed game state: inconsistency with stored state in database!")
        elif response == 1:
            raise cherrypy.HTTPError(500, "Error with AI's turn handling!")
        else:
            return response

    ofc_backend.exposed = True

class Root(object):
    #make a subpage
    subpage = subpage()

    def make_game(self, player_first=True, score =0, roundNum =0 ):
        games = db_backend.get_database_collection()
        game_state = db_backend.make_state()

        game_state['playerFirst'] = player_first
        game_state['score'] = score
        game_state['roundNumber'] = roundNum + 1

        game_id = str(games.insert(game_state))

        raise cherrypy.HTTPRedirect("/ofc/play/{}".format(game_id))

    def play(self, game_id=None, next=None):
        if game_id is None:
            self.make_game()

        games = db_backend.get_database_collection()
        game_state = games.find_one({'_id': ObjectId(game_id)})
        playerFirst = game_state['playerFirst']
        score = game_state['score']
        roundNumber = game_state['roundNumber']

        # if next round then invert playerFirst boolean and make game carrying over score from previous rounds
        if next == 'next':
            print "\nserver thinks that the Score is:", score, "\n"
            self.make_game(player_first = not playerFirst, score=score, roundNum=roundNumber)

        print game_state.keys()

        return render_template('OFCP_game.html', game_id=game_id, playerFirst=playerFirst, score=score, roundNumber=roundNumber, game_state=game_state)

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
