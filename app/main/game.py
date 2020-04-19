"""
GAME LOGIC MODULE
holds and runs all the calithumpian game logic.
"""
import random
from collections import deque, OrderedDict
from time import sleep

from .deck import Deck
from ..main import events

ROUNDS = ["2-ASC", "3-ASC", "4-ASC", "5-ASC", "6-ASC", "7-ASC", "8-ASC", "9-ASC", "10-ASC",
          "10-DES", "9-DES", "8-DES", "7-DES", "6-DES", "5-DES", "4-DES", "3-DES", "2-DES"]

# ROUNDS = ["2-ASC", "3-ASC", "4-ASC"]


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

    def __init__(self):
        self._kill = False
        self.players = None
        self.deck = Deck()
        self.scores = dict()
        self.hands = dict()
        self.order = None
        self.dealer = None
        self.bets = dict()
        self.current_trick_played_cards = OrderedDict()
        self.current_trick_lead_suit = None
        self.player_turn = None

    def play(self, players):
        """
        main logic loop of game
        :return:
        """

        self.configure(players)

        for round_id in ROUNDS:
            if self._kill:
                print("KILL SIGNAL RECIEVED FOR GAME INSTANCE. ENDING PLAY")
                return
            round_cards = int(round_id.split("-")[0])
            events.update_round(round_cards)

            self.set_dealer()
            self.shuffle_deck()
            self.deal_cards(round_cards)
            trump_suit = self.set_trump_suite()
            self.set_bets(round_cards, trump_suit)

            # logic loop for each trick of the round
            play_order = self.order.copy()
            for index in range(round_cards):
                self.play_cards(play_order)
                if self._kill:
                    print("KILL SIGNAL RECIEVED FOR GAME INSTANCE. ENDING PLAY")
                    return
                trick_winner = self.determine_trick_winner(self.current_trick_played_cards, self.current_trick_lead_suit, trump_suit)
                self.bets[trick_winner]["wins"] += 1
                events.update_bets_table(self.bets)
                self.update_play_order(play_order, trick_winner)
                events.refresh_played_cards({})

            self.update_scores(self.bets, round_id)
            events.update_bets_table({})

        self.announce_winner()

    def kill_game(self):
        """
        sets the internal kill signal to true so the game logic loop will stop
        :return:
        """

        self._kill = True

    def configure(self, players):
        """
        inital setup required before the game starts
        :return:
        """

        self._kill = False
        self.players = players
        self._determine_order()
        self._setup_scores()
        self._reset_hands()

    def shuffle_deck(self):
        """
        resets the deck with all of the cards and shuffles them
        :return:
        """

        for player, value in self.hands.items():
            self.hands[player] = []

        self.deck.reset()
        self.deck.shuffle()

    def deal_cards(self, hand_size):
        """
        deals out the correct number of cards to each player
        :param hand_size: the number of cards per hand
        :return: None
        """

        # Add delay to make gameplay seem more natural
        sleep(2)

        events.update_action("Dealing cards to players")

        for card_index in range(hand_size):
            for player in self.order:
                new_card = self.deck.draw()[0]
                self.hands[player].append(new_card)
                print(f"SERVER LOGGING: player {player} draw card {new_card.name}")

        for player, hand in self.hands.items():
            self.hands[player] = self.deck.order_cards(hand)

        events.refresh_player_cards(self.players, self.hands)

    def set_trump_suite(self):
        """
        determines what the trump suite will be for this round.
        :return: Trump suit
        """

        events.update_action("Selecting the trump suit for this round")
        card = self.deck.draw()[0]

        events.update_action(f"Trump suit for this round is {card.suit}")
        events.update_trump(card.suit)
        return card.suit

    def set_bets(self, round_num, trump):
        """
        all players set their bets for the round
        :return: dictionary of player names and bets.
        """

        # Add delay to make gameplay seem more natural
        sleep(2)

        self.bets = {}
        for player in self.order:
            events.update_action(f"{player}, please enter your bet")
            events.get_player_bet(self.players[player]["sid"], round_num, trump)

            # blocking waiting for the value to come back and be set
            while player not in self.bets.keys():
                if self._kill:
                    print("KILL SIGNAL RECIEVED FOR GAME. ENDING PLAY")
                    return
                print(f"WAITING FOR BET VALUE FROM PLAYER {player} to be returned")
                sleep(2)

            events.update_action(f"{player} bets {self.bets[player]['bet']} tricks this round!")
            events.update_bets_table(self.bets)

    def play_cards(self, play_order):
        """
        in order, go around the players with each player selecting their card to play
        play_order: the order of which you play your cards
        :return:
        """

        self.current_trick_lead_suit = None
        self.current_trick_played_cards = OrderedDict()

        for player in play_order:
            # Add delay to make gameplay seem more natural
            sleep(1)

            self.player_turn = player
            events.update_action(f"{player}, please play a card")
            # events.play_card(player)

            # check if player choice has come back and been validated yet.
            while player not in self.current_trick_played_cards.keys():
                if self._kill:
                    print("KILL SIGNAL RECIEVED FOR GAME INSTANCE. ENDING PLAY")
                    return
                print(f"WAITING FOR PLAYER {player} TO PICK A CARD")
                # wait 2 seconds then reassess
                sleep(2)

            card = self.current_trick_played_cards[player]
            self.hands[player].remove(card)
            events.update_action(f"{player} has played {card.name}")
            events.refresh_player_cards(self.players, self.hands)
            events.refresh_played_cards(self.current_trick_played_cards)

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

        events.update_action(f"Determining who won the trick")
        sleep(2)
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

        events.update_action(f"Winner of the trick is {winner} with {played_cards[winner].name}")
        print(f"Winner of the trick is {winner} with {played_cards[winner].name}")
        sleep(3)
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

    def update_scores(self, bets, round_id):
        """
        updates the scores for each player
        :param bets: dictionary of key=player value=dictionary holding the bet and wins
        :return: None
        """

        print("Updating player scores.")
        events.update_action(f"Updating the scores!")

        for player, bet_vals in bets.items():
            if bet_vals["bet"] == bet_vals["wins"]:
                score = 10 + bet_vals["bet"]
            else:
                score = 0
            self.scores[player].append(score)

            events.update_action(f"player {player} scored {score} points that round")
            print(f"player {player} scored {score} that round, bringing their total to {sum(self.scores[player])}")
            sleep(1)

        events.update_score_table(self.players, self.scores)

    def announce_winner(self):
        """
        announce the winner!
        :return:
        """

        events.update_action("AND THE FINAL SCORES ARE...")
        final_scores = []
        for player, round_scores in self.scores.items():
            final_scores.append((player, sum(round_scores)))
        final_scores.sort(reverse=True, key=lambda tup: tup[1])

        print("AND THE FINAL SCORES ARE:")
        for score in final_scores:
            sleep(1)
            events.update_action(f"{score[0]} with a score of {score[1]}")
            print(f"{score[0]} with a score of {score[1]}")

        sleep(1)
        events.update_action(f"Thanks for playing! press start game to play again")
        print("THANKS FOR PLAYING!!!")

    def _determine_order(self):
        """
        determines the order of play for the players in the game
        :return:
        """

        events.update_action("Determining Player Order")
        self.order = deque(list(self.players.keys()))

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

    def check_legal_move(self, player, card_img_path):
        """
        checks that the card choosen by the player is a legal move.
        the card played by a player must be of the same suit as the lead suit if they have a card of that suit in their hand.

        :param card: the card played by the player
        :param hand: the cards in the players hand
        :param lead_suit: the lead suite to judge against
        :return: boolean. True if legal, False if illegal
        """

        hand = self.hands[player]
        card = self._resolve_card_from_img(hand, card_img_path)

        if not self.current_trick_lead_suit:
            self.current_trick_lead_suit = card.suit
            self.current_trick_played_cards[player] = card
            return True
        elif card.suit == self.current_trick_lead_suit:
            self.current_trick_played_cards[player] = card
            return True
        else:
            has_suit = False
            for hold_card in hand:
                if hold_card.suit == self.current_trick_lead_suit:
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

        # Add delay to make gameplay seem more natural
        sleep(2)

        events.update_action("Selecting Dealer")

        print(f"PREVIOUS DEALER = {self.dealer}")
        print(f"PREVIOUS ORDER = {self.order}")

        if self.dealer:
            print("INSIDE DEALER UPDATE")
            self.order.rotate(-1)
            self.dealer = self.order[-1]
        else:
            events.update_action("No dealer currently selected, high card for dealer position")

            self.shuffle_deck()
            values = []
            for player in self.order:
                card = self.deck.draw()[0]
                values.append((player, card.value))
                events.update_action(f"{player} draws {card.name}")

            values.sort(reverse=True, key=lambda tup: tup[1])
            self.dealer = values[0][0]

            # determine the number of stpes to move the self.order deque object so that the new dealer is now in last position
            reorder_steps = (self.order.index(self.dealer) + 1) * -1
            self.order.rotate(reorder_steps)

        events.update_action(f"Dealer is {self.dealer}")
        events.update_round_order(list(self.order))

        print(f"NEW DEALER = {self.dealer}")
        print(f"NEW ORDER = {self.order}")

    def _resolve_card_from_img(self, hand, img_path):
        """
        resolves the card object from the hand based on img path

        :param hand:
        :param img_path:
        :return:
        """

        for card in hand:
            if card.img == img_path:
                return card

    def set_player_bet(self, player, bet_dict):
        """
        sets the players bets for a round. called from the event class after reciving a response from the player

        :param player:
        :param bet_dict:
        :return:
        """

        self.bets[player] = bet_dict

    def get_player_turn(self):
        return self.player_turn

    def add_card_to_played_cards(self, player, card_img):
        """
        This method will add the
        :param player:
        :param card_img:
        :return:
        """
        card = self.deck.get_card_from_img_path(card_img)
        self.current_trick_played_cards[player] = card
