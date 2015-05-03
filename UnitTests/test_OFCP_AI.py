from unittest import TestCase

__author__ = 'Ali'

import OFCP_AI

class Test_OFCP_AI(TestCase):
    def test_find_valid_moves1(self):
        print "\n###################\nRunning Tests for OFCP_AI.py now...\n"

        # test if AI can correctly detect valid placements for each row
        print "\nTest #1 testing OFCP-AI find_valid_moves #1 (Empty gs)"
        test_game_state = make_state()
        result = OFCP_AI.find_valid_moves(test_game_state) # [cards placed bot, cards placed mid, cards placed top]
        for item in result:
            self.assertEqual(0, item)
        print "Passed!"

    def test_find_valid_moves2(self):
        # test if AI can correctly detect valid placements for each row
        print "\nTest #2 testing OFCP-AI find_valid_moves #2 (Bottom full)"
        test_game_state = make_state()

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
        print "\nTest #3 testing OFCP-AI find_valid_moves #3 (Middle full)"
        test_game_state = make_state()

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
        print "\nTest #4 testing OFCP-AI find_valid_moves #4 (Top full)"
        test_game_state = make_state()

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
        print "\nTest #5 testing OFCP-AI find_valid_moves #5 (gs full)"
        test_game_state = make_state()

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
        print "\nTest #6 testing OFCP-AI find_valid_moves #6 (gs edge cases)"
        test_game_state = make_state()

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

    def test_produce_deck_of_cards(self):
        # test if AI script generates a legitimate deck of cards
        print "\nTest #7 testing OFCP-AI deck generation"
        test_deck = generate_deck()
        result = OFCP_AI.produce_deck_of_cards()

        self.assertEqual(len(test_deck), len(result))
        self.assertEqual(set(test_deck), set(result))
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