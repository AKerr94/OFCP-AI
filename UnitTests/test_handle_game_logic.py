from unittest import TestCase

__author__ = 'Ali'

import game_logic
import db_backend

from bson.objectid import ObjectId
import json

def create_test_gs_vars():
    # create a database entry and blank game state for use in controlled testing
    # return empty game state and unique database identifier
    test_games = db_backend.get_database_collection()
    test_game_state = db_backend.make_state()
    test_game_id = str(test_games.insert(test_game_state))
    test_db_state = test_games.find_one({'_id': ObjectId(test_game_id)})

    return [test_game_state, test_game_id]

class TestHandle_game_logic(TestCase):

    def test_handle_game_logic(self):
        xs = create_test_gs_vars()
        test_game_state = xs[0]
        test_game_id = xs[1]

        result = json.loads( game_logic.handle_game_logic(test_game_state, test_game_id) )
        self.assertEqual(type(result), type([]) )
        #self.fail()