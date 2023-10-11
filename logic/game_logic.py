from random import randint
from typing import List


class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def __str__(self):
        return f"{self.rank} {self.suit}"


class Deck:
    def __init__(self):
        self.cards = []
        self.reset_deck()

    def shuffle(self):
        for i in range(len(self.cards)):
            swap_number = randint(0, len(self.cards) - 1)
            self.cards[swap_number], self.cards[i] = self.cards[i], self.cards[swap_number]

    def reset_deck(self):
        self.cards = [Card(suit, rank)
                      for suit in ["Clubs", "Diamonds", "Spades", "Hearts"] for rank in
                      ["2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King", "Ace"]]

    # Debug method
    def print_cards(self):
        for card in self.cards:
            print(card)

    def deal_card(self):
        # This method deals a single card from the top of the deck
        return self.cards.pop()


class Player:
    def __init__(self, name, user_id, chips, position):
        self.client_socket = None
        self.name = name
        self.user_id = user_id
        self.profile_picture = None
        self.chips = chips
        self.current_bet = 0
        self.hand = Hand([])
        self.position = position
        self.blinds = []
        self.dealer = False
        self.folded = False
        self.all_in = False

    def add_card(self, card):
        self.hand.cards.append(card)


class Game:
    def __init__(self, starting_chips=200, player_limit=6):
        self.players: List[Player] = []
        self.client_sockets = []
        self.available_positions = ["top_left", "top_middle", "top_right", "bottom_right", "bottom_middle",
                                    "bottom_left"]

        self.pot = Pot()
        self.starting_chips = starting_chips
        self.board = []
        self.deck = Deck()
        self.current_player_turn = -1
        self.is_game_starting = False
        self.small_blind = 5
        self.big_blind = 10
        self.dealer_position = -1
        self.small_blind_position = -1
        self.big_blind_position = -1
        self.current_highest_bet = self.big_blind
        self.current_round = "preflop"
        self.player_limit = player_limit

    def is_betting_round_over(self, last_player_folded):
        # Check if all active players have bet the same amount
        active_players = self.get_active_players()
        if len(set(p.current_bet for p in active_players)) > 1:
            print("Current betting round not over as not all players have gone")
            return False

        # Check if every player has had an opportunity to act
        if self.current_round == "preflop":
            last_player = self.get_last_player(self.big_blind_position)
            print("-------------------------------")
            print("PREFLOP")
            print(f"big blind position: {self.big_blind_position}")
            print(f"Last player: {last_player}")
            # If the last player folded, and they were supposed to be the last one to bet,
            # the last player variable will currently hold the first player who hasn't folded before the last player
            # adding one to this gets us the actual last player who we are looking for (with modulus)
            if last_player_folded:
                last_player = (last_player + 1) % len(self.players)
            print(f"New last player: {last_player}")
            print("-------------------------------")

            if self.current_player_turn != last_player:
                print("Current betting round not over as the current player is not the big blind player")
                return False
        else:
            last_player = self.get_last_player(self.dealer_position)
            print("-------------------------------")
            print("NOT PREFLOP")
            print(f"big blind position: {self.big_blind_position}")
            print(f"Last player: {last_player}")
            if last_player_folded:
                last_player = (last_player + 1) % len(self.players)
            print(f"New last player: {last_player}")
            print("-------------------------------")

            if self.current_player_turn != last_player:
                print("Current betting round not over as the current player is not the dealer button player")
                return False

        self.current_player_turn = self.small_blind_position
        print(f"Current player turn = small blind positoin: {self.current_player_turn}")
        self.set_next_available_player()
        print(f"New current player turn: {self.current_player_turn}")

        return True

    def set_next_available_player(self):
        while self.players[self.current_player_turn].folded:
            print(f"{self.players[self.current_player_turn]} has folded so moving to next player")
            self.current_player_turn = (self.current_player_turn + 1) % len(self.players)

    def get_last_player(self, last_player):
        while self.players[last_player].folded:
            last_player = (last_player - 1) % len(self.players)
        return last_player

    def get_active_players(self):
        return [p for p in self.players if not p.folded]

    def only_one_player_active(self):
        active_players = self.get_active_players()
        return len(active_players) == 1

    def progress_to_next_round(self):

        if self.current_round == "preflop":
            self.flop()
            self.current_round = "flop"
        elif self.current_round == "flop":
            self.turn_river()
            self.current_round = "turn"
        elif self.current_round == "turn":
            self.turn_river()
            self.current_round = "river"
        elif self.current_round == "river":
            self.showdown()

    def showdown(self):
        print("showdown has been reached")

    def get_initial_state(self):
        state = {
            'players': [{'name': p.name, 'user_id': p.user_id, 'chips': p.chips, 'position': p.position} for p in
                        self.players],
            'pot': self.pot.chips,
            'board': [str(card) for card in self.board],
            'player_limit': self.player_limit,
        }
        return state

    def get_game_state(self):
        # The general state of the game
        state = {
            'players': [{'name': p.name, 'user_id': p.user_id, 'chips': p.chips, 'current_bet': p.current_bet,
                         "blinds": p.blinds} for p in self.players],
            'pot': self.pot.chips,
            'board': [str(card) for card in self.board],
            'current_player_turn': self.current_player_turn,
        }
        return state

    def get_game_state_for_player(self, player):
        # The state of the game to be sent to a specific player
        state = {
            'players': [{'name': p.name, 'user_id': p.user_id, 'chips': p.chips, 'current_bet': p.current_bet,
                         "blinds": p.blinds, "dealer": p.dealer, "folded": p.folded} for p in self.players],
            'pot': self.pot.chips,
            'board': [str(card) for card in self.board],
            'current_player_turn': self.current_player_turn,
            'hand': [str(card) for card in player.hand.cards]
        }
        print(f"(game_logic.py): returning {state} to {player}")
        return state

    def send_game_state(self):
        # Prepare the game state for each player and return it
        game_states = {}
        for player in self.players:
            game_states[player.user_id] = self.get_game_state_for_player(player)
        return game_states

    def get_player_left_state(self):
        # The state of a game after a player has left
        state = {
            'players': [{'name': p.name, 'user_id': p.user_id, 'chips': p.chips, 'position': p.position} for p in
                        self.players],
            'pot': self.pot.chips,
            'board': [str(card) for card in self.board],
            'current_player_turn': self.current_player_turn,
        }
        return state

    def add_player(self, player: Player, client_socket):
        player.client_socket = client_socket
        self.players.append(player)

    def remove_player(self, user_id):
        self.players = [player for player in self.players if player.user_id != user_id]

    def deal_cards(self, num_cards, player):
        for i in range(num_cards):
            card = self.deck.deal_card()
            player.add_card(card)

    def start_round(self):
        for player in self.players:
            player.current_bet = 0
            player.hand.cards = []
            player.folded = False
        self.deck.reset_deck()
        self.deck.shuffle()
        self.current_highest_bet = self.big_blind
        self.current_round = "preflop"

        self.board = []
        for player in self.players:
            self.deal_cards(2, player)
            player.folded = False

        # Clear any players of any previous attributes if there are any
        if self.small_blind_position != -1 and self.big_blind_position != -1 and self.dealer_position != -1:
            self.players[self.small_blind_position].blinds = []
            self.players[self.big_blind_position].blinds = []
            self.players[self.dealer_position].dealer = False

        self.dealer_position = (self.dealer_position + 1) % len(self.players)
        self.small_blind_position = (self.dealer_position + 1) % len(self.players)
        self.big_blind_position = (self.small_blind_position + 1) % len(self.players)
        self.current_player_turn = (self.big_blind_position + 1) % len(self.players)
        print(f"Current player turn: {self.current_player_turn}")

        self.players[self.small_blind_position].chips -= self.small_blind
        self.players[self.big_blind_position].chips -= self.big_blind
        self.players[self.small_blind_position].current_bet = self.small_blind
        self.players[self.big_blind_position].current_bet = self.big_blind

        self.players[self.small_blind_position].blinds.append("SB")
        self.players[self.big_blind_position].blinds.append("BB")
        self.players[self.dealer_position].dealer = True

        self.pot.add_chips(self.small_blind + self.big_blind)

    def flop(self):
        for i in range(3):
            card = self.deck.deal_card()
            self.board.append(card)

    def turn_river(self):
        card = self.deck.deal_card()
        self.board.append(card)

    def process_player_action(self, player_id, action):
        # Process a player action (fold, call, raise) and update the game state
        pass


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
