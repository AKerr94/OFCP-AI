from unittest import TestCase

__author__ = 'Ali'

'''
    Run these tests from server with following command:  pypy -m unittest discover --pattern=test*.py
    Ensure this file is in root folder with rest of backend scripts
'''

import OFCP_AI

import sys
import os

import copy

class Test_OFCP_AI(TestCase):

    def test_chooseMove_1(self):
        print "\n###################\nRunning Tests for OFCP_AI.py now...\n"

        # testing AI chooseMoove function
        print "\nTest #1 testing OFCP_AI chooseMove #1 individual card"
        test_game_state = copy.deepcopy( make_state() )
        x = test_game_state['properties2']['cards']['items']
        test_cards = ['h09', 'h10', 'd05', 'd09', 'c12']
        for i in range(1,6):
            x['position'+str(i*2)] = test_cards[i -1]
        f = open(os.devnull, 'w')
        sys.stdout = f
        result = OFCP_AI.chooseMove(test_game_state, 'c01', 300)
        f.close()
        sys.stdout = sys.__stdout__
        self.assertEqual(type(1), type(result))
        print "Passed!"

    def test_chooseMove_2(self):
        # testing AI chooseMoove function
        print "\nTest #2 testing OFCP_AI chooseMove #2 5 card placements"
        test_game_state = copy.deepcopy( make_state() )
        f = open(os.devnull, 'w')
        sys.stdout = f
        result = OFCP_AI.chooseMove(test_game_state, ['c01','s01','d08','h03', 'h04'], 300)
        f.close()
        sys.stdout = sys.__stdout__
        self.assertEqual(5, len(result))
        for item in result:
            self.assertEqual(type(1), type(item))
        print "Passed!"

    def test_chooseMove_3(self):
        # testing AI chooseMoove function
        print "\nTest #3 testing OFCP_AI chooseMove #3 - validation of cards"
        test_game_state = copy.deepcopy( make_state() )
        f = open(os.devnull, 'w')
        sys.stdout = f
        result = OFCP_AI.chooseMove(test_game_state, ['invalid'], 300)
        f.close()
        sys.stdout = sys.__stdout__
        self.assertEqual(None, result)
        print "Passed!"

    def test_chooseMove_4(self):
        # testing AI chooseMoove function
        print "\nTest #4 testing OFCP_AI chooseMove #4 - validation of row placements"
        test_game_state = copy.deepcopy( make_state() )
        test_game_state['name1'] = "#### ~UNIT TESTING~ #####"
        f = open(os.devnull, 'w')
        sys.stdout = f
        result = OFCP_AI.chooseMove(test_game_state, ['invalid'], 300)
        f.close()
        sys.stdout = sys.__stdout__
        self.assertEqual(None, result)
        print "Passed!"

    def test_find_valid_moves1(self):
        # test if AI can correctly detect valid placements for each row
        print "\nTest #5 testing OFCP-AI find_valid_moves #1 (Empty gs)"
        test_game_state = copy.deepcopy( make_state() )
        result = OFCP_AI.find_valid_moves(test_game_state) # [cards placed bot, cards placed mid, cards placed top]
        for item in result:
            self.assertEqual(0, item)
        print "Passed!"

    def test_find_valid_moves2(self):
        # test if AI can correctly detect valid placements for each row
        print "\nTest #6 testing OFCP-AI find_valid_moves #2 (Bottom full)"
        test_game_state = copy.deepcopy( make_state() )

        test_deck = generate_deck()

        x = test_game_state['properties2']['cards']['items']
        for i in range(1,6):
            x['position'+str(i)] = test_deck[i]

        result = OFCP_AI.find_valid_moves(test_game_state)

        self.assertEqual(5, result[0])
        self.assertEqual(0, result[1])
        self.assertEqual(0, result[2])
        print "Passed!"

    def test_find_valid_moves3(self):
        # test if AI can correctly detect valid placements for each row
        print "\nTest #7 testing OFCP-AI find_valid_moves #3 (Middle full)"
        test_game_state = copy.deepcopy( make_state() )

        test_deck = generate_deck()

        x = test_game_state['properties2']['cards']['items']
        for i in range(6,11):
            x['position'+str(i)] = test_deck[i]

        result = OFCP_AI.find_valid_moves(test_game_state)

        self.assertEqual(0, result[0])
        self.assertEqual(5, result[1])
        self.assertEqual(0, result[2])
        print "Passed!"

    def test_find_valid_moves4(self):
        # test if AI can correctly detect valid placements for each row
        print "\nTest #8 testing OFCP-AI find_valid_moves #4 (Top full)"
        test_game_state = copy.deepcopy( make_state() )

        test_deck = generate_deck()

        x = test_game_state['properties2']['cards']['items']
        for i in range(11,14):
            x['position'+str(i)] = test_deck[i]

        result = OFCP_AI.find_valid_moves(test_game_state)

        self.assertEqual(0, result[0])
        self.assertEqual(0, result[1])
        self.assertEqual(3, result[2])
        print "Passed!"

    def test_find_valid_moves5(self):
        # test if AI can correctly detect valid placements for each row
        print "\nTest #9 testing OFCP-AI find_valid_moves #5 (gs full)"
        test_game_state = copy.deepcopy( make_state() )

        test_deck = generate_deck()

        x = test_game_state['properties2']['cards']['items']
        for i in range(1,14):
            x['position'+str(i)] = test_deck[i]

        result = OFCP_AI.find_valid_moves(test_game_state)

        self.assertEqual(5, result[0])
        self.assertEqual(5, result[1])
        self.assertEqual(3, result[2])
        print "Passed!"

    def test_find_valid_moves6(self):
        # test if AI can correctly detect valid placements for each row
        print "\nTest #10 testing OFCP-AI find_valid_moves #6 (gs edge cases)"
        test_game_state = copy.deepcopy( make_state() )

        test_deck = generate_deck()

        x = test_game_state['properties2']['cards']['items']
        for i in range(1,14):
            if i == 5 or i == 10 or i == 13:
                continue
            x['position'+str(i)] = test_deck[i]

        result = OFCP_AI.find_valid_moves(test_game_state)

        self.assertEqual(4, result[0])
        self.assertEqual(4, result[1])
        self.assertEqual(2, result[2])
        print "Passed!"

    def test_place_5_1(self):
        # test main function handling placement of AIs first 5 cards
        print "\nTest #11 OFCP_AI place_5 #1"
        test_game_state = copy.deepcopy( make_state() )

        # stop stdout
        f = open(os.devnull, 'w')
        sys.stdout = f
        # get r_placements result
        result = OFCP_AI.place_5(test_game_state, ["c01","s01","d01","h07","c08"], 300, generate_deck())
        f.close()
        sys.stdout = sys.__stdout__

        self.assertEqual(5, len(result))
        for item in result:
            self.assertEqual(type(1), type(item))
            self.assertTrue(0 < item < 4)
        print "Passed!"

    def test_place_5_2(self):
        # test main function handling placement of AIs first 5 cards
        print "\nTest #12 OFCP_AI place_5 #2"
        test_game_state = copy.deepcopy( make_state() )

        # stop stdout
        f = open(os.devnull, 'w')
        sys.stdout = f
        # get r_placements result
        result = OFCP_AI.place_5(test_game_state, ["d08","s08","h05","h13","c02"], 300, generate_deck())
        f.close()
        sys.stdout = sys.__stdout__

        self.assertEqual(5, len(result))
        for item in result:
            self.assertEqual(type(1), type(item))
            self.assertTrue(0 < item < 4)
        print "Passed!"

    def test_produce_deck_of_cards(self):
        # test if AI script generates a legitimate deck of cards
        print "\nTest #13 testing OFCP-AI deck generation"
        test_deck = generate_deck()
        result = OFCP_AI.produce_deck_of_cards()

        self.assertEqual(len(test_deck), len(result))
        self.assertEqual(set(test_deck), set(result))
        print "Passed!"

    def test_produce_histogram1(self):
        # test AI can accurately chart rank frequencies given an input hand
        print "\nTest #14 testing produce_histogram for mapping rank frequencies #1"
        result = OFCP_AI.produce_histogram(['AS','AD','AH','6S','9C'])
        self.assertEqual(1, result[4][1])
        self.assertEqual(1, result[7][1])
        self.assertEqual(3, result[12][1])
        print "Passed!"

    def test_produce_histogram2(self):
        # test AI can accurately chart rank frequencies given an input hand
        print "\nTest #15 testing produce_histogram for mapping rank frequencies #2"
        result = OFCP_AI.produce_histogram(['KS','KD','KH','KC','2C'])
        self.assertEqual(1, result[0][1])
        self.assertEqual(4, result[11][1])
        print "Passed!"

    def test_produce_histogram3(self):
        # test AI can accurately chart rank frequencies given an input hand
        print "\nTest #16 testing produce_histogram for mapping rank frequencies - validation"
        result = OFCP_AI.produce_histogram(['KS','KD','KH','KC','erroneous entry'])
        self.assertEqual(None, result)
        print "Passed!"

    def test_simulateGame1(self):
        # testing simulateGame function
        print "\nTest #17 testing OFCP_AI simulateGame basic functionality"
        test_game_state = copy.deepcopy( make_state() )
        test_deck = generate_deck()
        result = OFCP_AI.simulateGame(test_game_state, None, None, False, test_deck[:])
        self.assertEqual(type(1), type(result))
        print "Passed!"

    def test_simulateGame2(self):
        # testing simulateGame function
        print "\nTest #18 testing OFCP_AI simulateGame with appending functionality #1"
        test_game_state = copy.deepcopy( make_state() )
        test_deck = generate_deck()
        result = OFCP_AI.simulateGame(test_game_state, 1, "s09", True, test_deck[:])
        self.assertEqual(type(1), type(result))
        print "Passed!"

    def test_simulateGame3(self):
        # testing simulateGame function
        print "\nTest #19 testing OFCP_AI simulateGame with appending functionality #2"
        test_game_state = copy.deepcopy( make_state() )
        test_deck = generate_deck()
        result = OFCP_AI.simulateGame(test_game_state, 2, "d13", True, test_deck[15:])
        self.assertEqual(type(1), type(result))
        print "Passed!"

    def test_simulateGame4(self):
        # testing simulateGame function
        print "\nTest #20 testing OFCP_AI simulateGame with appending functionality #3"
        test_game_state = copy.deepcopy( make_state() )
        test_deck = generate_deck()
        result = OFCP_AI.simulateGame(test_game_state, 3, "c06", True, test_deck[25:])
        self.assertEqual(type(1), type(result))
        print "Passed!"

    def test_simulate_append_card1(self):
        # testing simulated append function
        print "\nTest #21 testing simulate_append_card #1"
        test_game_state = copy.deepcopy( make_state() )
        result = OFCP_AI.simulate_append_card(test_game_state, 1, 'h01', False)
        try:
            x = result['properties2']['cards']['items']
        except:
            raise KeyError()
        self.assertEqual("h01", x['position1'])
        print "Passed!"

    def test_simulate_append_card2(self):
        # testing simulated append function
        print "\nTest #22 testing simulate_append_card #2"
        test_game_state = copy.deepcopy( make_state() )
        result = OFCP_AI.simulate_append_card(test_game_state, 2, 's07', False)
        try:
            x = result['properties2']['cards']['items']
        except:
            raise KeyError()
        self.assertEqual("s07", x['position6'])
        print "Passed!"

    def test_simulate_append_card3(self):
        # testing simulated append function
        print "\nTest #23 testing simulate_append_card #3"
        test_game_state = copy.deepcopy( make_state() )
        result = OFCP_AI.simulate_append_card(test_game_state, 3, 'd09', False)
        try:
            x = result['properties2']['cards']['items']
        except:
            raise KeyError()
        self.assertEqual("d09", x['position11'])
        print "Passed!"

    def test_simulate_append_card4(self):
        # testing simulated append function
        print "\nTest #24 testing simulate_append_card validation"
        test_game_state = copy.deepcopy( make_state() )

        # disable stdout to reduce clutter
        f = open(os.devnull, 'w')
        sys.stdout = f
        # get result - should be invalid and return None
        result = OFCP_AI.simulate_append_card(test_game_state,'invalidrow', 'd11', False)
        f.close()
        # re-enable stdout
        sys.stdout = sys.__stdout__

        self.assertEqual(None, result)
        print "Passed!"





# helper functions for testing
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