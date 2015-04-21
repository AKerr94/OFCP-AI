__author__ = 'Alastair Kerr'
# -*- coding: utf-8 -*-

from pymongo import MongoClient

def get_database_collection():
    connection = MongoClient()
    conn = connection['ofc']
    return conn.games

def make_state():
    game_state = {"name1":"Player1",
                        "properties1":
                            {"cards":
                                {"items":
                                     {"position1":None,
                                      "position2":None,
                                      "position3":None,
                                      "position4":None,
                                      "position5":None,
                                      "position6":None,
                                      "position7":None,
                                      "position8":None,
                                      "position9":None,
                                      "position10":None,
                                      "position11":None,
                                      "position12":None,
                                      "position13":None}
                                 }
                             },
                  "name2":"Player2",
                        "properties2":
                            {"cards":
                                 {"items":
                                      {"position1":None,
                                       "position2":None,
                                       "position3":None,
                                       "position4":None,
                                       "position5":None,
                                       "position6":None,
                                       "position7":None,
                                       "position8":None,
                                       "position9":None,
                                       "position10":None,
                                       "position11":None,
                                       "position12":None,
                                       "position13":None,
                                       }
                                  }
                             },
                  "playerFirst":True
                }
    return game_state

def next_move(self, game_id):
    games = get_database_collection()
    state =	games.find_one({'_id': ObjectId(game_id)})

    state['position-15'] = 'AK'