# -*- coding: utf-8 -*-
# 5 card hand evaluator by kmanley. Original source: https://github.com/kmanley/hands

RANKS = "23456789TJQKA"
RANK_TO_VALUE = {rank : i+2 for i, rank in enumerate(RANKS)}
VALUE_TO_RANK = [None, None] + list(RANKS)
STRAIGHTS = set([(RANKS + RANKS)[i:i+5] for i in range(9)] + ["A2345"])

def score_5(hand):
    '''
    Evaluates the 5-card poker hand and returns a "score" in 
    the form of a tuple of ints. The tuple can be compared to
    the score of another hand using tuple arithmetic to determine
    which hand has a higher score.
    
    hand: 10-character string. Note: cards must be sorted by rank 
    and suits must be uppercase
    
    >>> True if (score_5("THJHQHKHAH") > score_5("4C4H4D4SAH")) else False
    True
    
    >>> score_5("THJHQHKHAH")
    (9, 14)
    
    >>> score_5("2H3H4H5H6H")
    (9, 6)
    
    >>> score_5("4C4H4D4SAH")
    (8, 4, 14)
    
    >>> score_5("3H3D4C4D4S")
    (7, 4, 3)
    
    >>> score_5("3C4C5C9CAC")
    (6, 14, 9, 5, 4, 3)
    
    >>> score_5("2C3C4D5H6S")
    (5, 6)
    
    >>> score_5("6S7D8H9STH")
    (5, 10)
    
    >>> score_5("6S6D6H9STH")
    (4, 6, 10, 9)
    
    >>> score_5("4S4DTHTS3H")
    (3, 10, 4, 3)
    
    >>> score_5("3H4S4D7S7H")
    (3, 7, 4, 3)
    
    >>> score_5("3H4S7S7HJD")
    (2, 7, 11, 4, 3)
    
    >>> score_5("3H4STSJDQH")
    (1, 12, 11, 10, 4, 3)
    '''
    ranks = hand[::2]
    suits = set(hand[1::2])
    counts = [None, [], [], [], []] 
    for rank in ranks:
        counts[ranks.count(rank)].append(RANK_TO_VALUE[rank])
    straight = ranks in STRAIGHTS
    counts_4 = counts[4]
    counts_3 = counts[3]
    counts_2 = counts[2]
    counts_1 = counts[1]
    flush = len(suits)==1
    if flush:
        if straight:
            # straight flush, possibly ace-high (royal flush)
            return (9, counts_1[-1])
        else:
            # flush
            return (6, counts_1[-1], counts_1[-2], counts_1[-3], counts_1[-4], counts_1[-5])
    elif counts_4:
        # 4 of a kind
        return (8, counts_4[0], counts_1[-1])
    elif counts_3:
        if counts_2:
            # full house
            return (7, counts_3[0], counts_2[0])
        else:
            # counts[x] is a list of cards in low to high order, so top kicker is in counts_1[-1] 
            return (4, counts_3[0], counts_1[-1], counts_1[-2])                
    elif straight:
        # straight
        return (5, counts_1[-1])
    elif counts_2:
        if len(counts_2) == 4:
            # 2 pair
            return (3, counts_2[-1], counts_2[0], counts_1[-1])
        else:
            # 1 pair
            return (2, counts_2[-1], counts_1[-1], counts_1[-2], counts_1[-3])
    else:
        # high card
        return (1, counts_1[-1], counts_1[-2], counts_1[-3], counts_1[-4], counts_1[-5])
    
def classify_5(hand_or_score):
    '''
    Given a hand (or score) returns a string describing 
    the hand.
    
    >>> classify_5("THJHQHKHAH")
    'Royal Flush'

    >>> classify_5("2H3H4H5H6H")
    'Straight Flush - 6 high'

    >>> classify_5("4C4H4D4SAH")
    '4 of a Kind - 4s with A kicker'

    >>> classify_5("4C3H4D4S3D")
    'Full House - 4s full of 3s'

    >>> classify_5("4C3C5C9CAC")
    'Flush - A high with 9 kicker'

    >>> classify_5("2C3C4D5H6S")
    'Straight - 6 high'

    >>> classify_5("6S7D8H9STH")
    'Straight - T high'

    >>> classify_5("6S6D6H9STH")
    '3 of a Kind - 6s with T kicker'

    >>> classify_5("4S4DTHTS3H")
    '2 Pair - Ts and 4s with 3 kicker'

    >>> classify_5("3H4D4S7S7H")
    '2 Pair - 7s and 4s with 3 kicker'

    >>> classify_5("7S7H4S3HJD")
    'Pair of 7s with J kicker'

    >>> classify_5("3H4STSJDQH")
    'High Card - Q with J kicker'
    
    >>> classify_5((3, 10, 4, 3))
    '2 Pair - Ts and 4s with 3 kicker'
    '''
    if type(hand_or_score) == tuple:
        score = hand_or_score
    else:
        score = score_5(hand_or_score)
    category = score[0]
    cards = [VALUE_TO_RANK[x] for x in score[1:]]
    high_card = cards[0]
    if category==9:
        if high_card == "A":
            return "Royal Flush"
        else:
            return "Straight Flush - %s high" % high_card
    elif category == 8:
        return "4 of a Kind - %ss with %s kicker" % (high_card, cards[1])
    elif category == 7:
        # no kicker in this case; full house uses all 5 cards
        return "Full House - %ss full of %ss" % (high_card, cards[1])
    elif category == 6:
        return "Flush - %s high with %s kicker" % (high_card, cards[1])
    elif category == 5:
        return "Straight - %s high" % high_card
    elif category == 4:
        # we know that besides the set we have 2 random cards, otherwise we would have had a full house
        # counts[x] is a list of cards in low to high order, so top kicker is in counts[1][1]
        return "3 of a Kind - %ss with %s kicker" % (high_card, cards[1])
    elif category == 3:
        return "2 Pair - %ss and %ss with %s kicker" % (high_card, cards[1], cards[2])
    elif category == 2:
        return "Pair of %ss with %s kicker" % (high_card, cards[1])
    elif category == 1:
        return "High Card - %s with %s kicker" % (high_card, cards[1])
    else:
        raise AssertionError, "invalid score: %s" % repr(score)    

if __name__ == "__main__":
    import doctest
    doctest.testmod()
