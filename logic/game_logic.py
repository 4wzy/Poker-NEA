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
        self.disconnected = False
        self.all_in = False
        self.busted = False

    def add_card(self, card):
        self.hand.cards.append(card)


class Game:
    def __init__(self, starting_chips=200, player_limit=6):
        self.players: List[Player] = []
        self.client_sockets = []
        self.available_positions = ["top_left", "top_middle", "top_right", "bottom_right", "bottom_middle",
                                    "bottom_left"]
        self.last_position_index = -1
        self.pot = Pot()
        self.starting_chips = starting_chips
        self.board = []
        self.deck = Deck()
        self.current_player_turn = -1
        self.game_started = False
        self.small_blind = 5
        self.big_blind = 10
        self.dealer_position = -1
        self.small_blind_position = -1
        self.big_blind_position = -1
        self.current_highest_bet = self.big_blind
        self.current_round = "preflop"
        self.player_limit = player_limit
        self.first_player_to_act = None
        self.last_player_to_act = None
        self.first_player_acted = False

    def is_betting_round_over(self):
        if not self.first_player_acted:
            if self.current_player_turn == self.first_player_to_act:
                self.first_player_acted = True

        print("-------------- IS_BETTING_ROUND_OVER ----------------")
        print(f"first_player_to_act: {self.first_player_to_act}")
        print(f"last_player_to_act: {self.last_player_to_act}")
        print(f"current_player_turn: {self.current_player_turn}")
        print(f"has self.first_player_acted: {self.first_player_acted}")
        print("------------------------------")

        # Check if all active players have bet the same amount
        active_players = self.get_active_players()
        if len(set(player.current_bet for player in active_players)) > 1:
            print("Current betting round not over as not all players have gone")
            return False

        return self.first_player_acted and self.current_player_turn == self.last_player_to_act

    def start_new_round(self, round_type):
        if round_type == "preflop":
            # First player to act: player after the big blind
            # Last player to act: Big blid player
            self.first_player_to_act = self.get_next_active_player(self.big_blind_position, False)
            self.last_player_to_act = self.big_blind_position
        elif round_type == "flop":
            # First player to act: small blind player or first active player after
            # Last player to act: dealer player or first active player before
            self.first_player_to_act = self.get_next_active_player(self.dealer_position, False)
            self.last_player_to_act = self.get_previous_active_player(self.small_blind_position, False)
            self.current_player_turn = self.first_player_to_act
        else:
            self.first_player_to_act = self.get_next_active_player(self.first_player_to_act, True)
            self.last_player_to_act = self.get_previous_active_player(self.last_player_to_act, True)
            self.current_player_turn = self.first_player_to_act

        print("-------------- START_NEW_ROUND ----------------")
        print(f"first_player_to_act: {self.first_player_to_act}")
        print(f"last_player_to_act: {self.last_player_to_act}")
        print(f"current_player_turn: {self.current_player_turn}")
        print(f"has self.first_player_acted: {self.first_player_acted}")
        print("------------------------------")

        self.first_player_acted = False

    def handle_player_leaving(self, leaving_player):
        # Check if the leaving player is first or last to act and update accordingly
        print(f"player {leaving_player} leaving!")
        print(f"First player to act: {self.first_player_to_act}, Last player to act: {self.last_player_to_act}")
        if leaving_player == self.players[self.current_player_turn]:
            if self.players[self.first_player_to_act] == leaving_player:
                print("First player to act == leaving player")
                self.first_player_to_act = self.get_next_active_player(self.first_player_to_act, False)
            elif self.players[self.last_player_to_act] == leaving_player:
                print("Last player to act == leaving player")
                self.last_player_to_act = self.get_previous_active_player(self.last_player_to_act, False)
            print("Updating current player turn")
            self.current_player_turn = self.get_next_active_player(self.current_player_turn, False)

    def get_next_active_player(self, current_position, use_current_player):
        if len(self.get_active_players()) == 0:
            # If the server is force terminated, stop it from being in an infinite loop
            return 0

        if use_current_player:
            if self.is_player_active(current_position):
                return current_position

        print(f"(get_next_active_player): {current_position}")

        while True:
            current_position = (current_position + 1) % len(self.players)
            print(f"(get_next_active_player): {current_position}")
            if self.is_player_active(current_position):
                return current_position

    def is_player_active(self, current_position):
        return not (self.players[current_position].folded or
                    self.players[current_position].disconnected or
                    self.players[current_position].busted)

    def get_previous_active_player(self, current_position, use_current_player):
        if use_current_player:
            if self.is_player_active(current_position):
                return current_position

        while True:
            current_position = (current_position - 1) % len(self.players)
            if self.is_player_active(current_position):
                return current_position

    def get_active_players(self):
        return [p for index, p in enumerate(self.players) if self.is_player_active(index)]

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

        self.start_new_round(self.current_round)

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
                         "blinds": p.blinds, "dealer": p.dealer, "folded": p.folded, "disconnected": p.disconnected,
                         "busted": p.busted} for p in self.players],
            'pot': self.pot.chips,
            'board': [str(card) for card in self.board],
            'current_player_turn': self.current_player_turn,
            'hand': [str(card) for card in player.hand.cards]
        }
        print(f"(game_logic.py): returning {state} to {player}")
        return state

    def get_game_state_for_reconnecting_player(self, player):
        state = {
            'players': [{'name': p.name, 'user_id': p.user_id, 'chips': p.chips, 'current_bet': p.current_bet,
                         "blinds": p.blinds, "dealer": p.dealer, "folded": p.folded, "disconnected": p.disconnected,
                         "busted": p.busted, "position": p.position} for p in self.players],
            'pot': self.pot.chips,
            'board': [str(card) for card in self.board],
            'current_player_turn': self.current_player_turn,
            'hand': [str(card) for card in player.hand.cards],
            'player_limit': self.player_limit
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

    def reconnect_player(self, user_id, client_socket):
        player = next((p for p in self.players if p.user_id == user_id), None)
        player.client_socket = client_socket
        player.disconnected = False

    def remove_player(self, user_id, completely_remove):
        if completely_remove:
            self.players = [player for player in self.players if player.user_id != user_id]
        else:
            player = next((player for player in self.players if player.user_id == user_id), None)
            if player:
                # The following flags allow a player to rejoin in the future.
                # The player will remain folded, so that they do not interrupt a round that is already being played
                player.disconnected = True
                player.folded = True
                print(f"Found player {player.name} and set disconnected to true")
                self.handle_player_leaving(player)

    def deal_cards(self, num_cards, player):
        if not player.disconnected:
            for i in range(num_cards):
                card = self.deck.deal_card()
                player.add_card(card)

    def start_round(self):
        self.board = []
        self.deck.reset_deck()
        self.deck.shuffle()
        for player in self.players:
            player.current_bet = 0
            player.hand.cards = []
            player.folded = False
            player.blinds = []
            player.dealer = False
            self.deal_cards(2, player)
            if not player.busted and player.chips == 0 and player.all_in:
                player.busted = True
            else:
                player.all_in = False

            if player.disconnected:
                player.folded = True

        self.current_highest_bet = self.big_blind
        self.current_round = "preflop"
        self.first_player_to_act = 0
        self.last_player_to_act = len(self.players) - 1
        self.first_player_acted = False

        self.dealer_position = self.get_next_active_player(self.dealer_position, False)
        self.small_blind_position = self.get_next_active_player(self.dealer_position, False)
        self.big_blind_position = self.get_next_active_player(self.small_blind_position, False)
        self.current_player_turn = self.get_next_active_player(self.big_blind_position, False)
        print(f"Current player turn: {self.current_player_turn}")

        self.players[self.small_blind_position].chips -= self.small_blind
        self.players[self.big_blind_position].chips -= self.big_blind
        self.players[self.small_blind_position].current_bet = self.small_blind
        self.players[self.big_blind_position].current_bet = self.big_blind

        self.players[self.small_blind_position].blinds.append("SB")
        self.players[self.big_blind_position].blinds.append("BB")
        self.players[self.dealer_position].dealer = True

        self.pot.add_chips(self.small_blind + self.big_blind)
        self.start_new_round(self.current_round)

    def flop(self):
        for i in range(3):
            card = self.deck.deal_card()
            self.board.append(card)

    def turn_river(self):
        card = self.deck.deal_card()
        self.board.append(card)

    def player_fold(self, player):
        message = f"{player.name} folds"

        player.folded = True
        if player == self.players[self.first_player_to_act]:
            self.first_player_to_act = self.get_next_active_player(self.first_player_to_act, False)
        elif player == self.players[self.last_player_to_act]:
            self.last_player_to_act = self.get_previous_active_player(self.last_player_to_act, False)

        return message

    def player_call(self, player):
        bet_amount = self.current_highest_bet - player.current_bet
        if player.chips >= bet_amount:
            player.chips -= bet_amount
            self.pot.add_chips(bet_amount)
            player.current_bet = self.current_highest_bet
            if player.chips == 0:
                player.all_in = True
        else:
            return {"success": False, "error": "You do not have enough chips to call"}

        return {"success": True}

    def player_raise(self, player, raise_amount):
        # The player raises over the current highest bet
        total_bet = raise_amount + player.current_bet
        if total_bet <= self.current_highest_bet or raise_amount <= 0:
            return {"success": False,
                    "error": f"You need to raise by at least {self.current_highest_bet - player.current_bet}."}
        # Previously only game.current_highest_bet above instead of taking away player.current_bet
        if raise_amount > player.chips:
            return {"success": False, "error": "You don't have enough chips to raise this amount."}
        else:
            player.chips -= raise_amount
            self.pot.add_chips(raise_amount)
            player.current_bet = total_bet
            self.current_highest_bet = total_bet
            message = f"{player.name} raises by {raise_amount} chips to a total of {total_bet} chips"
            print(message)
            if player.chips == 0:
                player.all_in = True
            return {"success": True}

    def process_player_action(self, player, action, raise_amount):
        message = ""
        # Check if it's the player's turn
        if player != self.players[self.current_player_turn]:
            return {"success": False, "error": "It's not your turn!"}

        # Defensive programming: if the game hasn't started yet, nobody should be able to act yet.
        if not self.game_started:
            return {"success": False, "error": "The game has not started yet."}

        # IF THERE IS ONLY 1 PLAYER LEFT, EVALUATE THE WIN CONDITION OR ELSE THERE WILL BE AN INFINITE LOOP
        last_player_folded = False
        if player.folded:
            return {"success": False, "error": "This player has folded."}
        if action == 'fold':
            message = self.player_fold(player)
            print(message)

        elif action == 'call':
            action_response = self.player_call(player)
            if not action_response['success']:
                return action_response

        elif action == 'raise':
            action_response = self.player_raise(player, raise_amount)
            if not action_response['success']:
                return action_response

        print(f"About to check if only one player active in list of active players: {self.get_active_players()}")
        # Check if everyone has folded apart from one player
        if self.only_one_player_active():
            # The remaining active player wins the pot
            remaining_player = self.get_active_players()[0]
            remaining_player.chips += self.pot.chips
            self.pot.chips = 0
            message = f"{remaining_player.name} wins the pot as everyone else folded!"
            self.start_round()
        else:
            # If not, the current Poker round is still in action, so check if the betting round is over
            if self.is_betting_round_over():
                print(f"{self.current_round} round over!")
                self.progress_to_next_round()
            else:
                # If the betting round is not over, go to next player's turn
                self.current_player_turn = self.get_next_active_player(self.current_player_turn, False)
            print(
                f"Next player's turn: Player index {(self.current_player_turn)}, {self.players[self.current_player_turn]}")

        return {"success": True, "message": message}


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
