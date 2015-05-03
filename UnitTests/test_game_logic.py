from unittest import TestCase

__author__ = 'Ali'

'''
    Run these tests from server with following command:  pypy -m unittest discover --pattern=test*.py
    Ensure this file is in root folder with rest of backend scripts
'''

import game_logic
import db_backend
import deck

from bson.objectid import ObjectId
import json

import sys
import os


class Test_game_logic(TestCase):

    def test_handle_game_logic1(self):
        print "Running Tests for game_logic.py now...\n"
        print "\nTest #1 game logic @ empty gs (player to place 5)"

        # test player first empty gs receives 5 cards
        xs = create_test_gs_vars()
        test_game_state = xs[0]
        test_game_id = xs[1]

        # disable stdout to avoid screen clutter
        f = open(os.devnull, 'w')
        sys.stdout = f

        # call game_logic function
        result = json.loads( game_logic.handle_game_logic(test_game_state, test_game_id) )

        f.close()
        # re-enable stdout
        sys.stdout = sys.__stdout__

        # assert that 5 cards have been returned
        for potential_card in result:
            self.assertEqual(True, isCard(str(potential_card)))

        print "Passed!"

    def test_handle_game_logic2(self):
        print "\nTest #2 game logic @ AIs first turn"

        # test player first AI's round 1 - should see updated db state
        xs = create_test_gs_vars()
        test_game_state = xs[0]
        test_game_id = xs[1]
        test_db_state = xs[2]
        test_games = xs[3]

        # set up test database to replicate a game state after a player's initial turn
        test_db_state['deck'] = {}
        test_db_state['deck']['cards'] = possible_cards # default order h 1-13, s 1-13, d 1-13, c 1-13
        test_db_state['deck']['current-position'] = 5
        test_db_state['first5cards'] = "h01h02h03h04h05"

        update = test_games.update({
            '_id': ObjectId(test_game_id)
            }, {
            '$set': test_db_state
        })

        # simulate placement of deck's first 5 cards
        for i in range(1,6):
            test_game_state['properties1']['cards']['items']['position'+str(i)] = possible_cards[i -1]

        # disable stdout temporarily to avoid cluttering screen
        f = open(os.devnull, 'w')
        sys.stdout = f

        # get result of game_logic function
        result = json.loads( game_logic.handle_game_logic(test_game_state, test_game_id) )
        f.close()

        # re-enable stdout
        sys.stdout = sys.__stdout__

        if 'cardtoplace' not in result:
            raise KeyError()

        # ensure a valid card was returned for player's next turn
        self.assertEqual(True, isCard( str(result['cardtoplace']) ) )

        # check database was updated with appropriate cards
        p2CardCount = 0
        for i in range(1,14):
            x = result['properties1']['cards']['items']['position'+str(i)]
            # we tested p1's cards placed in bottom row
            if i < 6:
                self.assertEqual(True, isCard(str(x)))
            else:
                self.assertEqual(None, x)

            # count AI's cards and validate type
            y = result['properties2']['cards']['items']['position'+str(i)]
            if y is not None:
                p2CardCount += 1
                self.assertEqual(True, isCard(str(y)))
        self.assertEqual(5,p2CardCount)

        print "Passed!"

    def test_handle_game_logic3(self):
        print "\nTest #3 game logic @ general case"

        xs = create_test_gs_vars()
        test_game_state = xs[0]
        test_game_id = xs[1]
        test_db_state = xs[2]
        test_games = xs[3]

        test_db_state['deck'] = {}
        test_db_state['deck']['cards'] = possible_cards
        test_db_state['deck']['current-position'] = 10

        # initialise both players first 5 cards
        for i in range(1,6):
            test_db_state['properties1']['cards']['items']['position'+str(i)] = possible_cards[i -1]
            test_db_state['properties2']['cards']['items']['position'+str(i)] = possible_cards[i +4]

        update = test_games.update({
            '_id': ObjectId(test_game_id)
            }, {
            '$set': test_db_state
        })

        # add player's placed card from this round
        test_game_state = test_db_state
        test_game_state['properties1']['cards']['items']['position6'] = possible_cards[10]

        # disable stdout temporarily to avoid cluttering screen
        f = open(os.devnull, 'w')
        sys.stdout = f

        # get result of game_logic function
        result = json.loads( game_logic.handle_game_logic(test_game_state, test_game_id) )
        f.close()

        # re-enable stdout
        sys.stdout = sys.__stdout__

        if 'cardtoplace' not in result:
            raise KeyError()

        # ensure a valid card was returned for player's next turn
        self.assertEqual(True, isCard( str(result['cardtoplace']) ) )

        # check database was updated with appropriate cards
        p2CardCount = 0
        for i in range(1,14):
            x = result['properties1']['cards']['items']['position'+str(i)]
            if i < 7:
                self.assertEqual(True, isCard(str(x)))
            else:
                self.assertEqual(None, x)

            # count AI's cards and validate type
            y = result['properties2']['cards']['items']['position'+str(i)]
            if y is not None:
                p2CardCount += 1
                self.assertEqual(True, isCard(str(y)))
        self.assertEqual(6,p2CardCount)

        print "Passed!"

    def test_handle_game_logic4(self):
        print "\nTest #4 game logic @ game end"

        xs = create_test_gs_vars()
        test_game_state = xs[0]
        test_game_id = xs[1]
        test_db_state = xs[2]
        test_games = xs[3]

        test_db_state['deck'] = {}
        test_db_state['deck']['cards'] = possible_cards
        test_db_state['deck']['current-position'] = 25

        # initialise both players final game states (full boards)
        for i in range(1,14):
            test_db_state['properties1']['cards']['items']['position'+str(i)] = possible_cards[i -1]
            test_db_state['properties2']['cards']['items']['position'+str(i)] = possible_cards[i +12]
        test_db_state['cardtoplace'] = possible_cards[12] # stripped in scorer
        test_db_state['score'] = 0

        update = test_games.update({
            '_id': ObjectId(test_game_id)
            }, {
            '$set': test_db_state
        })

        test_game_state = test_db_state

        # disable stdout temporarily to avoid cluttering screen
        f = open(os.devnull, 'w')
        sys.stdout = f

        # get result of game_logic function
        result = json.loads( game_logic.handle_game_logic(test_game_state, test_game_id) )
        f.close()

        # re-enable stdout
        sys.stdout = sys.__stdout__

        # assert that a valid score array was returned
        self.assertEqual(type([]), type(result))
        self.assertEqual(5, len(result))
        for i in range(0,3):
            for j in range(0,3):
                self.assertEqual(type(1), type(result[i][j]))
        for x in result[3]:
            self.assertEqual(type(True), type(x))
        self.assertEqual(type(1), type(result[4][0]))

        print "Passed!"

    def test_validate_and_update_state(self):
        # test whether game_logic helper function reads in, validates and updates state correctly
        print "\nTest #5 validate_and_update_state helper function"
        xs = create_test_gs_vars()
        test_game_state = xs[0]
        test_game_id = xs[1]
        test_db_state = xs[2]

        # generating test game state for player
        dcount = 0
        for i in range(1,12):
            test_game_state['properties1']['cards']['items']['position'+str(i)] = possible_cards[i -1]
            dcount += 1

        t_deck = deck.Deck(possible_cards, dcount)

        result = game_logic.validate_and_update_state(t_deck, dcount, test_game_state, test_db_state)

        if 'properties1' not in result or 'cards' not in result['properties1'] or 'items' not in result['properties1']['cards']:
            raise KeyError()

        for i in range(0,13):
            val = result['properties1']['cards']['items']['position'+str(i+1)]
            if val is not None:
                self.assertEqual(True, isCard(str(val)))

        print "Passed!"

    def test_zip_placements_cards(self):
        # test game_logic helper for zipping calculated placements and cards, and updating state
        print "\nTest #6 game_logic helper function zip_placement_cards"

        xs = create_test_gs_vars()
        test_db_state = xs[2]

        # some test data
        placements = [1,1,3,2,1]
        cards_list = ["d01", "h01","c12","c13","s01"]

        result = game_logic.zip_placements_cards(placements, cards_list, test_db_state)

        try:
            x = result['properties2']['cards']['items']
        except:
            raise KeyError()

        asserted_positions = ['position1', 'position2', 'position11', 'position6', 'position3']
        for i in range(0,5):
            self.assertEqual(cards_list[i], x[asserted_positions[i]])

        print "Passed!"

# test helper functions
def create_test_gs_vars():
    # create a database entry and game state for use in controlled testing
    # return empty game state and unique database identifier
    test_games = db_backend.get_database_collection()
    test_game_state = db_backend.make_state()
    test_game_id = str(test_games.insert(test_game_state))
    test_db_state = test_games.find_one({'_id': ObjectId(test_game_id)})

    return [test_game_state, test_game_id, test_db_state, test_games]

def generate_deck():
    # generate deck of cards for testing
    deck_of_cards = []
    for suit in ['h','s','d','c']:
        for i in range(1,14):
            cardname = str(suit)
            if i < 10:
                cardname += str(0)
            cardname += str(i)
            deck_of_cards.append(cardname)
    return deck_of_cards

def isCard(test_me):
    # return True if this is a card, else return False
    # card format char 1: h/d/s/c char2: 0-9 char3: 0-9

    # test for valid type
    if type(test_me) is not str:
        return False

    # test for valid suit
    if test_me[0] not in ['h','d','s','c']:
        return False

    # test for valid rank
    try:
        val = int(str(test_me[1]) + str(test_me[2]))
        if val > 14 or val < 1:
            return False
    except:
        return False

    # valid card!
    return True

possible_cards = generate_deck()
