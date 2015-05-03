from unittest import TestCase

__author__ = 'Ali'

import helpers

import sys
import os


class Test_helpers(TestCase):

    def test_classify_3_1(self):
        print "\n###################\nTesting helpers.py now...\n"

        # test classification of a 3 card hand rank
        print "\nTest #1 classifying 3 card rank tuple #1"
        result = helpers.classify_3((4,5))
        self.assertEqual("Three of a Kind 5s ", result)
        print "Passed!"

    def test_classify_3_2(self):
        # test classification of another 3 card hand rank
        print "\nTest #2 classifying 3 card rank tuple #2"
        result = helpers.classify_3((2,6,10))
        self.assertEqual("Pair of 6s, 10 kicker.", result)
        print "Passed!"

    def test_classify_3_3(self):
        # test classifications validation
        print "\nTest #3 testing validation of 3 card classifier"
        result = helpers.classify_3(("invalid",2,3))
        self.assertEqual(None, result)
        print "Passed!"

    def test_reformat_hand_xyy_yx1(self):
        # test a valid hand to format
        print "\nTest #4 reformat_hand_xyy_yx1 ~ valid 5 #1 "
        result = helpers.reformat_hand_xyy_yx("c09c10c11c12c13", 5)
        self.assertEqual("9CTCJCQCKC", result)
        print "Passed!"

    def test_reformat_hand_xyy_yx2(self):
        # test another valid hand to format
        print "\nTest #5 reformat_hand_xyy_yx2 ~ valid 5 #2 "
        result = helpers.reformat_hand_xyy_yx("s07c10d01c05c08", 5)
        self.assertEqual("5C7S8CTCAD", result)
        print "Passed!"

    def test_reformat_hand_xyy_yx3(self):
        # test a valid 3 card hand
        print "\nTest #6 reformat_hand_xyy_yx3 ~ valid 3"
        result = helpers.reformat_hand_xyy_yx("c03d03s03", 3)
        self.assertEqual("3C3D3S", result)
        print "Passed!"

    def test_reformat_hand_xyy_yx4(self):
        # test an invalid hand to check error handling
        print "\nTest #7 reformat_hand_xyy_yx4 ~ invalid 5 #1"

        # disable stdout to avoid screen clutter
        f = open(os.devnull, 'w')
        sys.stdout = f

        result = helpers.reformat_hand_xyy_yx("iaminvalid", 5)

        f.close()
        # re-enable stdout
        sys.stdout = sys.__stdout__

        self.assertEqual(None, result)
        print "Passed!"

    def test_reformat_hand_xyy_yx5(self):
        # test an invalid hand to check error handling
        print "\nTest #8 reformat_hand_xyy_yx5 ~ invalid 5 #2"

        # disable stdout to avoid screen clutter
        f = open(os.devnull, 'w')
        sys.stdout = f

        result = helpers.reformat_hand_xyy_yx("c05c07d07d08s13", 100)

        f.close()
        # re-enable stdout
        sys.stdout = sys.__stdout__

        self.assertEqual(None, result)
        print "Passed!"

    def test_reformat_hand_xyy_yx6(self):
        # test an invalid hand to check error handling
        print "\nTest #9 reformat_hand_xyy_yx6 ~ invalid 3"

        # disable stdout to avoid screen clutter
        f = open(os.devnull, 'w')
        sys.stdout = f

        result = helpers.reformat_hand_xyy_yx("3_non_existent", 3)

        f.close()
        # re-enable stdout
        sys.stdout = sys.__stdout__

        self.assertEqual(None, result)
        print "Passed!"

    def test_scores_arr_to_int1(self):
        # test that function correctly converts scores array to int (p1's score)
        print "\nTest #10 scores_arr_to_int #1"

        test_scores = [[1,3,0],[1,0,0],[2,0,0],[False, False]]
        result = helpers.scores_arr_to_int(test_scores)

        self.assertEqual(type(1), type(result))
        self.assertEqual(4, result)

        print "Passed!"

    def test_scores_arr_to_int2(self):
        # test that function correctly converts scores array to int (p1's score)
        print "\nTest #11 scores_arr_to_int #2"

        test_scores = [[2,0,5],[2,0,3],[2,0,6],[False, False]]
        result = helpers.scores_arr_to_int(test_scores)

        self.assertEqual(type(1), type(result))
        self.assertEqual(-20, result)

        print "Passed!"

    def test_scores_arr_to_int3(self):
        # test validation in scores_arr_to_int
        print "\nTest #12 scores_arr_to_int - validation #1"

        test_scores = "invalid type1"
        result = helpers.scores_arr_to_int(test_scores)

        self.assertEqual(None, result)
        print "Passed!"

    def test_scores_arr_to_int4(self):
        # test validation in scores_arr_to_int
        print "\nTest #13 scores_arr_to_int - validation #2"

        test_scores = ["invalid list length"]
        result = helpers.scores_arr_to_int(test_scores)

        self.assertEqual(None, result)
        print "Passed!"

    def test_scores_arr_to_int5(self):
        # test validation in scores_arr_to_int
        print "\nTest #14 scores_arr_to_int - validation #3"

        test_scores = [[1,0,0],[1,0,0],[1,0,"uh oh!"],[False,False]]
        result = helpers.scores_arr_to_int(test_scores)

        self.assertEqual(None, result)
        print "Passed!"

    def test_scores_arr_to_int6(self):
        # test validation in scores_arr_to_int
        print "\nTest #15 scores_arr_to_int - validation #4"

        test_scores = [[1,0,0],[1,0,0],[1,0,0],[False,"look im not a boolean!"]]
        result = helpers.scores_arr_to_int(test_scores)

        self.assertEqual(None, result)
        print "Passed!"

    def test_scoring_helper1(self):
        # test scoring helpers produces correct scores array
        print "\nTest #16 scoring_helper #1"
        test_game_state = make_state()
        test_cards_1 = ['d01','s01','h01','c01','s05','c13','s13','s10','h08','d09','c11','s03','d03','d08']
        test_cards_2 = ['d07','s07','h07','c09','s06','c13','s13','d10','c10','h09','h11','s04','d04','d02']
        for i in range(1,14):
            test_game_state['properties1']['cards']['items']['position'+str(i)] = test_cards_1[i -1]
            test_game_state['properties2']['cards']['items']['position'+str(i)] = test_cards_2[i -1]

        # disable stdout to avoid screen clutter
        f = open(os.devnull, 'w')
        sys.stdout = f
        # get scores_results
        scores_result = helpers.scoring_helper(test_game_state)
        f.close()
        sys.stdout = sys.__stdout__

        # assert that a valid score array was returned
        self.assertEqual(type([]), type(scores_result))
        self.assertEqual(4, len(scores_result))
        for i in range(0,3):
            for j in range(0,3):
                self.assertEqual(type(1), type(scores_result[i][j]))
        for x in scores_result[3]:
            self.assertEqual(type(True), type(x))
        print "Passed!"

    def test_scoring_helper2(self):
        # test error handling of scoring helper
        print "\nTest #17 scoring_helper #2 - testing validation"
        test_game_state = make_state()
        test_cards_1 = ['OOPS THIS IS INVALID!','s01','h01','c01','s05','c13','s13','s10','h08','d09','c11','s03','d03','d08']
        test_cards_2 = ['d07','s07','h07','c09','s06','c13','s13','d10','c10','h09','h11','s04','d04','d02']
        for i in range(1,14):
            test_game_state['properties1']['cards']['items']['position'+str(i)] = test_cards_1[i -1]
            test_game_state['properties2']['cards']['items']['position'+str(i)] = test_cards_2[i -1]

        # disable stdout to avoid screen clutter
        f = open(os.devnull, 'w')
        sys.stdout = f
        # call scoring_helper
        scores_result = helpers.scoring_helper(test_game_state)
        f.close()
        sys.stdout = sys.__stdout__

        self.assertEqual(scores_result, None)
        print "Passed!"

    def test_simple_3card_evaluator1(self):
        # test whether 3 card evaluator maps hands correctly
        print "\nTest #18 testing 3 card evaluator #1"
        result = helpers.simple_3card_evaluator("ADASAC")
        self.assertEqual((4,14), result)
        print "Passed!"

    def test_simple_3card_evaluator2(self):
        # test a different 3 card hand
        print "\nTest #19 testing 3 card evaluator #2"
        result = helpers.simple_3card_evaluator("TS6H3D")
        self.assertEqual((1,10,6,3), result)
        print "Passed!"

    def test_simple_3card_evaluator3(self):
        # test validation of 3card evaluator
        print "\nTest #20 testing 3 card evaluator - validation"

        f = open(os.devnull, 'w')
        sys.stdout = f
        result = helpers.simple_3card_evaluator("Invalid parameter")
        f.close()
        sys.stdout = sys.__stdout__

        self.assertEqual(None, result)
        print "Passed!"


# helper function for test - returns a blank game state
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