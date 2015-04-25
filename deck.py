__author__ = 'Alastair Kerr'
# -*- coding: utf-8 -*-

import random


class Deck(object):

    def __init__(self, deck=None, current_position=0):
        if deck is None:
            possible_cards = []
            suits = ["h", "d", "s", "c"]
            for suit in suits:
                for i in range(1,14):
                    temp = suit
                    if i < 10:
                        temp += "0"
                    temp += str(i)
                    possible_cards.append(temp)
            random.shuffle(possible_cards)
            self.cards = possible_cards
        else:
            self.cards = deck

        self.current_position = current_position

    def deal_one(self):
        self.current_position += 1
        return self.cards[self.current_position - 1]

    def __iter__(self):
        while self.current_position < len(possible_cards):
            yield deal_one()

    def peep(self):
        return self.cards[self.current_position]

    def deal_n(self, n):
        return [self.deal_one() for i in range(0, n)]
