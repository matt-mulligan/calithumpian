"""
Deck of cards class.
produces a deck of cards object to be used by the game class
"""

import random


class Deck (object):

    def __init__(self):
        self.cards_all = self.build_all_cards()
        self.cards_avaliable = self.cards_all
        self.cards_used = list()

    def build_all_cards(self):
        """
        Method to populate the self.cards_all attribute

        :return: list of all 52 playing card objects
        """

        cards = list()

        for suit in range(0, 3):
            for value in range(2, 15):
                cards.append(Card(value, suit))

        return cards

    def shuffle(self):
        """
        shuffles the avaliable cards in the deck, reordering self.avaliable_cards object

        :return: None
        """

        random.shuffle(self.cards_avaliable)

    def draw(self, num=1):
        """
        draws the number of cards from the deck as specified.

        :param num: the number of cards to draw
        :return: the number of card objecs specified
        """

        if num > len(self.cards_avaliable):
            raise ValueError("Not enough cards left in the deck!")

        # Select the cards to return
        cards = self.cards_avaliable[:num]

        # Add the cards to the used list
        self.cards_used.extend(cards)

        # remove the cards from the availiable list
        self.cards_avaliable = self.cards_avaliable[num:]

        return cards

    def reset(self):
        """
        resets the cards in the deck. removes all cards from the self.cards_used list and adds all cards to the
        self.cards_avaliable list

        :return: None
        """

        self.cards_used = []
        self.cards_avaliable = self.cards_all


class Card (object):
    """
    Class representing a single playing card
    """
    def __init__(self, card_value, suit_value):
        """
        the Init method of the card class.

        :param card_value: integer representing the value of the card between 2 and 14
        (where 2 represents a 2 and 14 represents and ace)
        :param suit_value: Integer representing the suit of the card between 0 and 3 mapping to the suit of the card
        (0=Clubs, 1=Diamonds, 2=Hearts, 3=Spades)
        """

        self.value = card_value
        self.suit = self.determine_suit(suit_value)
        self.rank = self.determine_rank()
        self.name = self.determine_name()

    @staticmethod
    def determine_suit(suit_value):
        """
        determines the suite of the card based on the given value
        (0=Clubs, 1=Diamonds, 2=Hearts, 3=Spades)

        :param suit_value: value of the cards suit
        :return:
        """

        return {0: "Clubs", 1: "Diamonds", 2: "Hearts", 3: "Spades"}[suit_value]

    def determine_rank(self):
        """
        returns the english rank of the card based on the value.

        :param value: integer specifying the rank, Where 2 is the lowest value (representing a two card) and 14 is
        the Highest Value (representing an Ace)
        :return: English rank of the card
        """

        if self.value not in range(2, 15):
            raise ValueError("Specified card value is not in allowed range. Remember that card values should be "
                             "between 2 and 14, with 14 being the Ace value.")

        return {
            2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six", 7: "Seven", 8: "Eight", 9: "Nine", 10: "Ten",
            11: "Jack", 12: "Queen", 13: "King", 14: "Ace"
        }[self.value]

    def determine_name(self):
        """
        Simple method to return the full english name of a card

        :return: Full english name of the card
        """

        return f"{self.rank} of {self.suit}"
