# Cards: https://opengameart.org/content/playing-cards-vector-png

from random import randint


class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def __str__(self):
        return f"{self.rank} {self.suit}"

    def __repr__(self) -> str:
        return f"{self.rank} {self.suit}"


class Deck:
    def __init__(self):
        self.cards = [Card(suit, rank)
                      for suit in ["Clubs", "Diamonds", "Spades", "Hearts"] for rank in ["2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King", "Ace"]]

    def shuffle(self):
        for i in range(len(self.cards)):
            swap_number = randint(0, len(self.cards) - 1)
            self.cards[swap_number], self.cards[i] = self.cards[i], self.cards[swap_number]

    # The following function is for testing purposes only, remove at the end of project
    def print_cards(self):
        for card in self.cards:
            print(card)

    def deal_card(self):
        # This method deals a single card from the top of the deck
        return self.cards.pop()


class Player:
    def __init__(self, name, chips):
        self.name = name
        self.chips = chips
        self.hand = Hand([])
        self.is_all_in = False
        self.has_folded = False
        self.has_acted = False

    def add_card(self, card):
        self.hand.cards.append(card)


class Game:
    def __init__(self, player_names, starting_chips=100):
        self.players = [Player(name, starting_chips) for name in player_names]
        self.big_blind_value = 4
        self.small_blind_value = 2
        self.pot = Pot()
        self.board = []
        self.deck = Deck()
        self.deck.shuffle()
        self.minimum_raise_amount = self.big_blind_value * 2
        self.player_bets = {}
        self.players_in_round = self.players.copy()
        self.dealer_button_player_index = randint(
            0, len(self.players_in_round) - 1)
        self.small_blind_player_index = 0
        self.big_blind_player_index = 0
        self.current_highest_bet = 0

    def get_player_cards(self):
        # Create poker card images
        cards = []
        for player in self.players:
            for card in player.hand.cards:
                cards.append(f"{card.rank}_of_{card.suit}")

        # Show which player has the big blind and the small blind
        # print(self.small_blind_player_index,
        #       self.big_blind_player_index)

        return cards

    def get_board_cards(self):
        cards = []
        for card in self.board:
            cards.append(f"{card.rank}_of_{card.suit}")

        return cards

    def deal_cards(self, num_cards, player):
        for i in range(num_cards):
            card = self.deck.deal_card()
            player.add_card(card)

    def is_betting_round_over(self, current_player, last_player_index):
        active_players = [
            player for player in self.players_in_round if not player.has_folded]
        active_player_chips_contributed = [
            self.player_bets[player.name] for player in active_players if not player.is_all_in]
        unique_chips = set(active_player_chips_contributed)

        if len(active_players) == 1:
            return True
        elif len(unique_chips) == 1:
            if current_player != last_player_index or not self.players_in_round[last_player_index].has_acted:
                return False

            return True
        elif self.current_highest_bet == 0:
            return True
        return False

    def handle_blinds(self):
        amount_of_players = len(self.players_in_round)

        # Increment the small and big blind indexes by 1. Wraps around to the start if needed
        self.dealer_button_player_index = (
            self.dealer_button_player_index + 1) % amount_of_players
        self.small_blind_player_index = (
            self.dealer_button_player_index + 1) % amount_of_players
        self.big_blind_player_index = (
            self.small_blind_player_index + 1) % amount_of_players

        # Deducts the blind values from the appropriate player's chips and adds it to the pot
        self.players_in_round[self.big_blind_player_index].chips -= self.big_blind_value
        self.pot.add_chips(self.big_blind_value)

        self.players_in_round[self.small_blind_player_index].chips -= self.small_blind_value
        self.pot.add_chips(self.small_blind_value)

    def fold(self, player_index, last_player):
        self.players_in_round[player_index].has_folded = True

        # If the player who wants to fold is the last player who is supposed to bet,
        # the last player will now be the next available person to the right
        amount_of_players = len(self.players_in_round)
        if player_index == last_player:
            while self.players[last_player].has_folded:
                last_player = (last_player - 1) % amount_of_players

        return last_player

        # self.players_in_round.pop(player_index)

    def distribute_pot(self):
        pass

    def reset_bets(self):
        # Create variables to track each player's contribution to the pot and the current highest bet
        for player in self.players_in_round:
            self.player_bets[player.name] = 0

    def flop(self):
        for i in range(3):
            card = self.deck.deal_card()
            self.board.append(card)

    def turn_river(self):
        card = self.deck.deal_card()
        self.board.append(card)


class Pot:
    def __init__(self):
        self.chips = 0

    def add_chips(self, amount):
        self.chips += amount

    def subtract_chips(self, amount):
        self.chips -= amount

    def reset_pot(self):
        self.chips = 0


class Hand:
    def __init__(self, cards):
        self.cards = cards

    def evaluate_strength(self):
        pass
