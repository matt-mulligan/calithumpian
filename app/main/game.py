"""
GAME LOGIC MODULE
holds and runs all the calithumpian game logic.
"""
import random
from collections import deque

from .deck import Deck
from . import main
from ..main import events

ROUNDS = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 9, 8, 7, 6, 5, 4, 3, 2]


class Calithumpian(object):
    """
    The class within the app that holds all the game logic.

    Instance object definitions:
        PLAYERS: Dictionry of player names and client SID's
        DECK: Instance of the Deck class to represent the deck of cards
        SCORES: Dictionary of player names and a list of their score after each round
        HANDS: Dictionary of player names and a list representing the cards they are holding now
        ORDER: Collections.Deque showing the order of players turns, the first player should be the person immediately
        after the dealer
        DEALER: Name of the player who is currently the dealer
    """

    def __init__(self, players):
        self.players = players
        self.deck = Deck()
        self.scores = dict()
        self.hands = dict()
        self.order = None
        self.dealer = None

    def play(self):
        """
        main logic loop of game
        :return:
        """

        self.configure()

        for round in ROUNDS:
            self.set_dealer()
            self.shuffle_deck()
            self.deal_cards(round)
            trump_suite = self.set_trump_suite()
            bets = self.set_bets()

            # logic loop for each trick of the round
            play_order = self.order
            for index in range(round):
                lead_suit, played_cards = self.play_cards(play_order)
                trick_winner = self.determine_trick_winner(played_cards, lead_suit, trump_suite)
                bets[trick_winner]["wins"] += 1
                self.update_play_order(play_order, trick_winner)

            self.update_scores(bets)

        self.announce_winner()

    def configure(self):
        """
        inital setup required before the game starts
        :return:
        """

        self._determine_order()
        self._setup_scores()
        self._reset_hands()

    def shuffle_deck(self):
        """
        resets the deck with all of the cards and shuffles them
        :return:
        """

        for player, value in self.hands:
            self.hands[player] = []

        self.deck.reset()
        self.deck.shuffle()

    def deal_cards(self, hand_size):
        """
        deals out the correct number of cards to each player
        :param hand_size: the number of cards per hand
        :return: None
        """

        print("Dealing cards to players.")

        for card_index in range(hand_size):
            for player in self.order:
                self.hands[player].append(self.deck.draw())

    def set_trump_suite(self):
        """
        determines what the trump suite will be for this round.
        :return: Trump suit
        """

        print("Selecting trump suit for the round")
        card = self.deck.draw()
        print(f"Trump suite this round is {card.suit}")
        return card.suit

    def set_bets(self):
        """
        all players set their bets for the round
        :return: dictionary of player names and bets.
        """

        bets = {}
        for player in self.order:
            print(f"{player}, how many tricks would you like to bet this round?")
            # ADD LOGIC BELOW TO SEND AN EMIT TO THE SPECIFIC PLAYER FOR A POPUP. HARDCODED AS 1
            bets[player] = {"bet": 1, "wins": 0}
            print(f"{player} bets {bets[player]} tricks this round!")

        return bets

    def play_cards(self, play_order):
        """
        in order, go around the players with each player selecting their card to play
        play_order: the order of which you play your cards
        :return:
        """

        played_cards = {}
        lead_suit = None
        for player in play_order:

            # Looping logic used to allow players to pick a card, check if legal move and loop if not
            legal_move = False

            while not legal_move:
                print(f"{player}, select a card to play for this trick.")
                # ADD LOGIC BELOW TO SEND AN EMIT TO THE SPECIFIC PLAYER FOR A POPUP. HARDCODED AS FIRST CARD IN HAND
                card = self.hands[player][0]

                # If first player, then set the lead suit and continue
                if not lead_suit:
                    lead_suit = card.suit
                    played_cards[player] = card
                    legal_move = True
                elif self._check_legal_move(card, self.hands[player], lead_suit):
                    self.hands[player].remove(card)
                    played_cards[player] = card
                    legal_move = True
                else:
                    print(f"ILLEGAL MOVE by player {player}. "
                          f"You have at least one card with the same suit as the lead card. "
                          f"Please pick a card of suit {lead_suit}")

        return lead_suit, played_cards

    def determine_trick_winner(self, played_cards, lead_suit, trump_suite):
        """
        determines who won the trick.
        Order of victory is
            - Highest trump card
            - Highest lead card

        :param played_cards: the cards each player played
        :param lead_suit: the lead suit
        :param trump_suite: the trump suit
        :return: name of the winner
        """

        trump_cards = {}
        lead_cards = {}
        for player, card in played_cards.items():
            if card.suit == trump_suite:
                trump_cards[player] = card
            elif card.suit == lead_suit:
                lead_cards[player] = card

        if len(trump_cards) > 0:
            winner = self._get_highest_card(trump_cards)
        else:
            winner = self._get_highest_card(lead_cards)

        print("Winner of the trick is {winner} with {played_cards[winner].name}")
        return winner

    def update_play_order(self, play_order, trick_winner):
        """
        updates the play_order based on who won the last trick

        :param play_order: the order of players
        :param trick_winner: the winner of the last trick
        :return:
        """

        reorder_steps = play_order.index(trick_winner) * -1
        play_order.rotate(reorder_steps)

    def update_scores(self, bets):
        """
        updates the scores for each player
        :param bets: dictionary of key=player value=dictionary holding the bet and wins
        :return: None
        """

        print("Updating player scores.")

        for player, bet_vals in bets.items():
            if bet_vals["bet"] == bet_vals["wins"]:
                score = 10 + bet_vals["bet"]
            else:
                score = 0
            self.scores[player].append(score)

            print(f"player {player} scored {score} that round, bringing their total to {sum(self.scores[player])}")

    def announce_winner(self):
        """
        announce the winner!
        :return:
        """

        final_scores = []
        for player, round_scores in self.scores.items():
            final_scores.append((player, sum(round_scores)))
        final_scores.sort(reverse=True, key=lambda tup: tup[1])

        print("AND THE FINAL SCORES ARE:")
        for score in final_scores:
            print(f"{score[0]} with a score of {score[1]}")

        print("THANKS FOR PLAYING!!!")

    def _determine_order(self):
        """
        randomly determines the order of play for the players in the game
        :return:
        """

        events.message_player_chat("SYSTEM: randomly determining the player order.")

        player_list = self.players.keys()
        random.shuffle(player_list)
        self.order = deque(player_list)

        print(f"Player order determined to be {self.order}")

    def _setup_scores(self):
        """
        sets up the score object before the start of play
        :return: None
        """

        for player in self.order:
            self.scores[player] = []

    def _reset_hands(self):
        """
        resets / sets up hands before play
        :return: None
        """

        for player in self.order:
            self.hands[player] = []

    def _check_legal_move(self, card, hand, lead_suit):
        """
        checks that the card choosen by the player is a legal move.
        the card played by a player must be of the same suit as the lead suit if they have a card of that suit in their hand.

        :param card: the card played by the player
        :param hand: the cards in the players hand
        :param lead_suit: the lead suite to judge against
        :return: boolean. True if legal, False if illegal
        """

        if card.suit == lead_suit:
            return True
        else:
            has_suit = False
            for hold_card in hand:
                if hold_card.suit == lead_suit:
                    has_suit = True
            return False if has_suit else True

    def _get_highest_card(self, played_cards):
        """
        checks for the outright highest value of the cards, returns the winning players name

        :param played_cards: dictionary in format key=player, value=card
        :return: winning player name
        """

        values = []
        for player, card in played_cards.items():
            values.append((player, card.value))
        values.sort(reverse=True, key=lambda tup: tup[1])
        return values[0][0]

    def set_dealer(self):
        """
        determines the dealer for the next hand of play
        :return: None
        """

        print("Determining New dealer.")

        if self.dealer:
            self.order.rotate(-1)
            self.dealer = self.order[-1]
        else:
            print("No dealer currently selected, High card for dealer position!")

            self.shuffle_deck()
            values = []
            for player in self.order:
                card = self.deck.draw()
                values.append((player, card.value))
                print(f"Player {player} draws card {card.name}")

            values.sort(reverse=True, key=lambda tup: tup[1])
            self.dealer = values[0][0]

            # determine the number of stpes to move the self.order deque object so that the new dealer is now in last position
            reorder_steps = (self.order.index(self.dealer) + 1) * -1
            self.order.rotate(reorder_steps)

        print(f"Dealer is {self.dealer}")
