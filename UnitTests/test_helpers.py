from unittest import TestCase

__author__ = 'Ali'

import helpers

import sys
import os


class Test_helpers(TestCase):
    def test_reformat_hand_xyy_yx1(self):
        # test a valid hand to format
        print "Testing helpers.py now...\n"
        print "\nTest #1 reformat_hand_xyy_yx1 ~ valid 5 #1 "
        hand = "c09c10c11c12c13"
        numCards = 5
        result = helpers.reformat_hand_xyy_yx(hand, numCards)
        self.assertEqual("9CTCJCQCKC", result)
        print "Passed!"

    def test_reformat_hand_xyy_yx2(self):
        # test another valid hand to format
        print "\nTest #2 reformat_hand_xyy_yx1 ~ valid 5 #2 "
        hand = "s07c10d01c05c08"
        numCards = 5
        result = helpers.reformat_hand_xyy_yx(hand, numCards)
        self.assertEqual("5C7S8CTCAD", result)
        print "Passed!"

    def test_reformat_hand_xyy_yx3(self):
        # test a valid 3 card hand
        print "\nTest #3 reformat_hand_xyy_yx1 ~ valid 3"
        hand = "c03d03s03"
        numCards = 3
        result = helpers.reformat_hand_xyy_yx(hand, numCards)
        self.assertEqual("3C3D3S", result)
        print "Passed!"

    def test_reformat_hand_xyy_yx4(self):
        # test an invalid hand to check error handling
        print "\nTest #4 reformat_hand_xyy_yx1 ~ invalid 5 #1"
        hand = "iaminvalid"
        numCards = 5
        # disable stdout to avoid screen clutter
        f = open(os.devnull, 'w')
        sys.stdout = f

        result = helpers.reformat_hand_xyy_yx(hand, numCards)

        f.close()
        # re-enable stdout
        sys.stdout = sys.__stdout__

        self.assertEqual(None, result)
        print "Passed!"

    def test_reformat_hand_xyy_yx5(self):
        # test an invalid hand to check error handling
        print "\nTest #5 reformat_hand_xyy_yx1 ~ invalid 5 #2"
        hand = "c05c07d07d08s13"
        numCards = 100
        # disable stdout to avoid screen clutter
        f = open(os.devnull, 'w')
        sys.stdout = f

        result = helpers.reformat_hand_xyy_yx(hand, numCards)

        f.close()
        # re-enable stdout
        sys.stdout = sys.__stdout__

        self.assertEqual(None, result)
        print "Passed!"