import time
from itertools import combinations
from random import randint
from typing import List
from collections import Counter


class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def __eq__(self, other):
        if isinstance(other, Card):
            return self.rank == other.rank and self.suit == other.suit
        return False

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
        # Variables for game statistics
        self.amount_of_times_raised = 0
        self.amount_of_times_all_in = 0
        self.amount_of_times_called = 0
        self.amount_of_times_checked = 0
        self.amount_of_times_folded = 0
        self.amount_of_times_acted = 0
        self.won_round = False
        self.won_game = False
        self.finishing_position = 0
        self.aggressiveness_score = 0
        self.conservativeness_score = 0

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
        self.total_pot = self.starting_chips * self.player_limit
        self.first_player_to_act = None
        self.last_player_to_act = None
        self.first_player_acted = False
        self.hand_rankings = ["High Card", "Pair", "Two Pair", "Three of a Kind",
                              "Straight", "Flush", "Full House", "Four of a Kind",
                              "Straight Flush", "Royal Flush"]
        self.non_active_player = None
        self.game_completed = False
        self.players_acted = []
        self.next_available_finishing_position = self.player_limit + 1

    def is_betting_round_over(self):
        active_players = self.get_players_for_showdown()
        all_in_players = [player for player in active_players if player.all_in]
        non_all_in_players = [player for player in active_players if not player.all_in]

        # If all but one player are all-in, and the last non-all-in player has acted, the round is over
        if len(non_all_in_players) == 1 and non_all_in_players[0] in self.players_acted:
            return True

        # If all non-all-in players have matching current bets and have acted, the round is over
        if all(player in self.players_acted for player in non_all_in_players):
            non_all_in_bets = [player.current_bet for player in non_all_in_players]
            if len(set(non_all_in_bets)) == 1:
                return True

        # If all active players have acted at least once and their bet amounts match, the round is over
        if self.first_player_acted and all(player in self.players_acted for player in active_players):
            all_bets = [player.current_bet for player in active_players]
            if len(set(all_bets)) == 1:
                return True

        return False

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
                self.non_active_player = leaving_player
                self.last_player_to_act = self.get_previous_active_player(self.last_player_to_act, False)
            print("Updating current player turn")
            self.current_player_turn = self.get_next_active_player(self.current_player_turn, False)

    def get_next_active_player(self, current_position, use_current_player):
        original_player = current_position

        if len(self.get_players_for_showdown()) == 0:
            # If the server is force terminated, stop it from being in an infinite loop
            print("ERROR ERROR ERROR: NO PLAYERS AVAILABLE FOR GET_NEXT_ACTIVE_PLAYER")
            print(f"{[f'{player.name}: {player.all_in}, {player.busted}, {player.folded}' for player in self.players]}")
            return 0

        if use_current_player:
            if self.is_player_active(current_position):
                print(f"(get_next_active_player) FINAL: {current_position}")
                return current_position

        # The loop below should check if all the players are looped through, and should return the original player
        # in order to avoid an infinite loop below
        checked_once = False
        while True:
            if checked_once:
                if current_position == original_player:
                    print("Returning 999")
                    return 999

            current_position = (current_position + 1) % len(self.players)
            print(f"(get_next_active_player): {current_position}")
            if self.is_player_active(current_position):
                return current_position
            checked_once = True

    def get_previous_active_player(self, current_position, use_current_player):
        if len(self.get_players_for_showdown()) == 0:
            # If the server is force terminated, stop it from being in an infinite loop
            print("ERROR ERROR ERROR: NO PLAYERS AVAILABLE FOR GET_NEXT_ACTIVE_PLAYER")
            print(f"{[f'{player.name}: {player.all_in}, {player.busted}, {player.folded}' for player in self.players]}")
            return 0

        if use_current_player:
            if self.is_player_active(current_position):
                print(f"(get_previous_active_player) FINAL: {current_position}")
                return current_position

        while True:
            current_position = (current_position - 1) % len(self.players)
            print(f"(get_previous_active_player): {current_position}")
            if self.is_player_active(current_position):
                return current_position

    def is_player_active(self, current_position):
        return not (self.players[current_position].folded or
                    self.players[current_position].disconnected or
                    self.players[current_position].busted or
                    self.players[current_position].all_in)

    def is_player_active_showdown(self, current_position):
        return not (self.players[current_position].folded or
                    self.players[current_position].disconnected or
                    self.players[current_position].busted)

    def get_players_for_showdown(self):
        return [p for index, p in enumerate(self.players) if self.is_player_active_showdown(index)]

    def get_active_players(self):
        return [p for index, p in enumerate(self.players) if self.is_player_active(index)]

    def only_one_player_active(self):
        active_players = self.get_players_for_showdown()
        print(f"(ONLY_ONE_PLAYER_ACTIVE) active_players: {[player.name for player in active_players]}")
        return len(active_players) == 1

    def progress_to_next_betting_round(self):
        # Reset the players who have acted this betting round
        self.players_acted = []
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
            showdown_data = self.showdown()

            if self.start_round() == "game_completed":
                print("game completed!")
                return {"success": True, "game_completed": True, "showdown_data": showdown_data}

            return {"success": True, "type": "showdown_data", "showdown_data": showdown_data}

        self.start_new_round(self.current_round)

    def skip_through_betting_rounds(self):
        if self.current_round == "preflop":
            self.flop()
            self.current_round = "flop"
        if self.current_round == "flop":
            self.turn_river()
            self.current_round = "turn"
        if self.current_round == "turn":
            self.turn_river()
            self.current_round = "river"
        message = self.showdown()

        return message

    def determine_winner_from_eligible_players(self, best_hands, eligible_players):
        # Filter out the best hands only for eligible players
        eligible_best_hands = {player: hand for player, hand in best_hands.items() if player in eligible_players}

        # Determine the maximum rank among eligible players
        max_rank = max(eligible_best_hands.values(), key=lambda x: x[0])[0]

        # Filter players with the max rank
        max_rank_players = {player: cards for player, (rank, cards) in eligible_best_hands.items() if rank == max_rank}

        # Sort players based on their card values
        sorted_players = sorted(max_rank_players.keys(), key=lambda x: max_rank_players[x], reverse=True)

        # The first player is the one with the best cards
        winners = [sorted_players[0]]

        # Check for ties
        for player in sorted_players[1:]:
            if max_rank_players[player] == max_rank_players[winners[0]]:
                winners.append(player)
            else:
                break

        return winners

    def evaluate_player_hands(self, remaining_players):
        best_hand_per_player = {}

        for player in remaining_players:
            all_seven_cards = player.hand.cards + self.board
            best_rank = -1
            best_cards = None

            for combo in combinations(all_seven_cards, 5):
                test_hand = Hand(list(combo))
                rank, cards = test_hand.evaluate_strength()
                rank_index = self.hand_rankings.index(rank)

                if rank_index > best_rank or (rank_index == best_rank and cards > best_cards):
                    best_rank = rank_index
                    best_cards = cards

            best_hand_per_player[player] = (best_rank, best_cards)

        return best_hand_per_player

    # Create pots based on any all_ins and return a list of pots
    def create_pots(self, remaining_players):
        pots = []
        last_all_in_amount = 0

        all_in_players = sorted((player for player in remaining_players if player.all_in), key=lambda p: p.current_bet)

        for all_in_player in all_in_players:
            pot_amount = (all_in_player.current_bet - last_all_in_amount) * len(remaining_players)
            pots.append((pot_amount, list(remaining_players)))

            last_all_in_amount = all_in_player.current_bet
            remaining_players.remove(all_in_player)

        main_pot = self.pot.chips - sum(pot[0] for pot in pots)
        # Add the main pot only if there are players left who haven't gone all-in
        if remaining_players and main_pot > 0:
            pots.append((main_pot, remaining_players))

        return pots

    def showdown(self):
        remaining_players = self.get_players_for_showdown()
        for player in remaining_players:
            player.won_round = False

        best_hand_per_player = self.evaluate_player_hands(remaining_players)
        pots = self.create_pots(remaining_players)

        winner_messages = []
        for pot_amount, eligible_players in pots:
            winning_players = self.determine_winner_from_eligible_players(best_hand_per_player, eligible_players)
            num_winners = len(winning_players)

            # Determine winner(s) and handle pot distribution
            if num_winners == 1:
                winner_message = f"{winning_players[0].name} wins {pot_amount} chips with a " \
                                 f"{self.hand_rankings[best_hand_per_player[winning_players[0]][0]]}!"
                winning_player = winning_players[0]
                print(f"{winning_player.name} chips: {winning_player.chips}, pot_amount: {pot_amount}")
                winning_player.chips += pot_amount
                winning_player.won_round = True
                print(f"set {winning_player.name}.won_round to True")
                # Check if the player has won the game
                total_chips_of_connected_players = sum([player.chips for player in self.players if not \
                    player.disconnected])
                print(f"{winning_player.name}: chips: {winning_player.chips}, current_bet: "
                      f"{winning_player.current_bet}, total_chips_of_connected_players: {total_chips_of_connected_players}")
                if winning_player.chips == total_chips_of_connected_players:
                    winning_player.won_game = True
            else:
                winner_message = "It's a tie between " + ", ".join(
                    [player.name for player in winning_players]) + f" for {pot_amount} chips!"
                pot_share = pot_amount // num_winners  # Integer division to get floor value
                extra_chips = pot_amount % num_winners
                for player in winning_players:
                    player.won_round = True
                    print(f"set {player.name}.won_round to True")
                    player.chips += pot_share

                # Give the extra chip to only one of the winners
                winning_players[0].chips += extra_chips

            winner_messages.append(winner_message)

        self.pot.chips = 0
        return "\n".join(winner_messages)

    def get_initial_state(self):
        state = {
            'players': [{'name': p.name, 'user_id': p.user_id, 'chips': p.chips, 'position': p.position} for p in
                        self.players],
            'pot': self.pot.chips,
            'board': [str(card) for card in self.board],
            'player_limit': self.player_limit,
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

    def get_game_state_for_showdown(self):
        state = {
            'players': [{'name': p.name, 'user_id': p.user_id, 'chips': p.chips, 'current_bet': p.current_bet,
                         "blinds": p.blinds, "dealer": p.dealer, "folded": p.folded, "disconnected": p.disconnected,
                         "busted": p.busted, "hand": [str(card) for card in p.hand.cards], "won_round": p.won_round} for
                        p in self.players],
            'pot': self.pot.chips,
            'board': [str(card) for card in self.board],
            'current_player_turn': self.current_player_turn
        }
        print(f"(game_logic.py): returning {state}")
        return state

    def get_game_state_for_completed(self):
        state = {
            'players': [
                {'name': p.name, 'user_id': p.user_id, 'chips': p.chips, "won_game": p.won_game, "folded": p.folded,
                 "disconnected": p.disconnected, "busted": p.busted} for p in
                self.players],
            'pot': self.pot.chips,
            'board': [str(card) for card in self.board]
        }
        print(f"(game_logic.py): returning {state}")
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
            player.won_round = False
            if not player.busted:
                self.deal_cards(2, player)
            if not player.busted and player.chips == 0 and player.all_in:
                player.busted = True
                player.finishing_position = self.next_available_finishing_position - 1
            else:
                player.all_in = False

            if player.disconnected:
                player.folded = True

        if len(self.get_active_players()) == 1:
            print("start_round: get_active_players() == 1")
            # end the game
            self.game_completed = True
            return "game_completed"

        # Reset the list of players who have acted in this round
        self.players_acted = []

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

        if self.players[self.small_blind_position].chips > self.small_blind:
            self.players[self.small_blind_position].chips -= self.small_blind
            self.players[self.small_blind_position].current_bet = self.small_blind
        else:
            self.players[self.small_blind_position].current_bet = self.players[self.small_blind_position].chips
            self.players[self.small_blind_position].chips = 0
            self.players[self.small_blind_position].all_in = True

        if self.players[self.big_blind_position].chips > self.big_blind:
            self.players[self.big_blind_position].chips -= self.big_blind
            self.players[self.big_blind_position].current_bet = self.big_blind
        else:
            self.players[self.big_blind_position].current_bet = self.players[self.big_blind_position].chips
            self.players[self.big_blind_position].chips = 0
            self.players[self.big_blind_position].all_in = True

        self.players[self.small_blind_position].blinds.append("SB")
        self.players[self.big_blind_position].blinds.append("BB")
        self.players[self.dealer_position].dealer = True

        self.pot.add_chips(self.small_blind + self.big_blind)
        self.start_new_round(self.current_round)

    def flop(self):
        # A card is discarded by the dealer before dealing the flop, turn, and river
        self.deck.deal_card()
        # Deal 3 cards
        for i in range(3):
            card = self.deck.deal_card()
            self.board.append(card)

    def turn_river(self):
        # A card is discarded by the dealer before dealing the flop, turn, and river
        self.deck.deal_card()

        card = self.deck.deal_card()
        self.board.append(card)

    def player_fold(self, player):
        message = f"{player.name} folds"

        player.folded = True
        player.amount_of_times_folded += 1
        if player == self.players[self.first_player_to_act]:
            self.first_player_to_act = self.get_next_active_player(self.first_player_to_act, False)
        elif player == self.players[self.last_player_to_act]:
            self.non_active_player = player
            self.last_player_to_act = self.get_previous_active_player(self.last_player_to_act, False)

        return message

    def player_call(self, player):
        bet_amount = self.current_highest_bet - player.current_bet
        if player.chips >= bet_amount:
            player.chips -= bet_amount
            self.pot.add_chips(bet_amount)
            player.current_bet = self.current_highest_bet
        else:
            # if they player does not have enough chips to call, they go all in and side pots are handled later
            player.current_bet += player.chips
            self.pot.add_chips(player.chips)
            player.chips = 0

        if player.chips == 0:
            player.all_in = True
            player.amount_of_times_all_in += 1
            self.non_active_player = player

        if bet_amount == 0:
            player.amount_of_times_checked += 1
        else:
            player.amount_of_times_called += 1

        self.players_acted.append(player)
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
                player.amount_of_times_all_in += 1
                self.non_active_player = player

            player.amount_of_times_raised += 1

            # Reset the players acted list as everyone needs to agree on a new amount to bet on
            self.players_acted = []
            self.players_acted.append(player)
            return {"success": True}

    def process_player_action(self, player, action, raise_amount):
        self.non_active_player = None
        message = ""
        # Check if it's the player's turn
        if player != self.players[self.current_player_turn]:
            return {"success": False, "error": "It's not your turn!"}

        # Defensive programming: if the game hasn't started yet, nobody should be able to act yet.
        if not self.game_started:
            return {"success": False, "error": "The game has not started yet."}

        # IF THERE IS ONLY 1 PLAYER LEFT, EVALUATE THE WIN CONDITION OR ELSE THERE WILL BE AN INFINITE LOOP
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

        player.amount_of_times_acted += 1

        print(f"About to check if only one player active in list of active players: {self.get_players_for_showdown()}")
        # Check if everyone has folded apart from one player
        if self.only_one_player_active():
            # The remaining active player wins the pot
            remaining_player = self.get_active_players()[0]
            remaining_player.chips += self.pot.chips
            self.pot.chips = 0
            message = f"{remaining_player.name} wins the pot as everyone else folded!"
            if self.start_round() == "game_completed":
                print("game completed!")
                return {"success": True, "type": "game_completed"}
        elif self.is_betting_round_over():
            if [player.all_in for player in self.get_players_for_showdown()].count(
                    False) > 1 and self.current_round != "river":
                print(f"{self.current_round} round over!")
                # If the betting round is over, check if all current players are "all in"
                self.progress_to_next_betting_round()
            else:
                print("skipping through Poker rounds")
                self.skip_through_betting_rounds()
                return {"success": True, "type": "skip_round", "showdown": True}
        else:
            # If the betting round is not over, go to next player's turn
            print("betting round not over, so getting next active player turn.")
            next_player_index = self.get_next_active_player(self.current_player_turn, False)
            if next_player_index == 999:
                print("skipping through Poker rounds")
                self.skip_through_betting_rounds()
                return {"success": True, "type": "skip_round", "showdown": True}
            else:
                self.current_player_turn = next_player_index

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

    RANKS = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
             'Jack': 11, 'Queen': 12, 'King': 13, 'Ace': 14}

    @staticmethod
    def is_sequence(lst):
        """Check if the list inputted can form a sequence."""
        return sorted(lst) == list(range(min(lst), max(lst) + 1))

    def evaluate_strength(self):
        # Convert cards to rank numbers and sort
        ranks = sorted([self.RANKS[card.rank] for card in self.cards], reverse=True)
        suits = [card.suit for card in self.cards]

        # Check for flush and straight
        flush = len(set(suits)) == 1
        straight = self.is_sequence(ranks) or (ranks == [14, 5, 4, 3, 2])  # Including A,2,3,4,5 straight

        # Check for four of a kind, three of a kind, pairs
        rank_counts = {rank: ranks.count(rank) for rank in ranks}
        max_count = max(rank_counts.values())

        # Royal Flush
        if flush and ranks[:5] == [14, 13, 12, 11, 10]:
            return "Royal Flush", ranks
        # Straight Flush
        if flush and straight:
            return "Straight Flush", ranks if ranks != [14, 5, 4, 3, 2] else [5, 4, 3, 2, 1]
        # Four of a Kind
        if max_count == 4:
            quad_rank = [rank for rank, count in rank_counts.items() if count == 4][0]
            other_ranks = [rank for rank in ranks if rank != quad_rank]
            return "Four of a Kind", [quad_rank] * 4 + other_ranks[:1]
        # Full House
        if max_count == 3 and len(set(ranks)) == 2:
            trips_rank = [rank for rank, count in rank_counts.items() if count == 3][0]
            other_rank = [rank for rank in ranks if rank != trips_rank][0]
            return "Full House", [trips_rank] * 3 + [other_rank] * 2
        # Flush
        if flush:
            return "Flush", ranks
        # Straight
        if straight:
            # The if statement below adjusts for the special case where the Ace is used as a 1 in the straight
            return "Straight", ranks if ranks != [14, 5, 4, 3, 2] else [5, 4, 3, 2, 1]
        # Three of a Kind
        if max_count == 3:
            trips_rank = [rank for rank, count in rank_counts.items() if count == 3][0]
            other_ranks = [rank for rank in ranks if rank != trips_rank]
            return "Three of a Kind", [trips_rank] * 3 + other_ranks[:2]
        # Two Pair
        if list(rank_counts.values()).count(2) == 2:
            pair_ranks = [rank for rank, count in rank_counts.items() if count == 2]
            other_ranks = [rank for rank in ranks if rank not in pair_ranks]
            return "Two Pair", pair_ranks * 2 + other_ranks[:1]
        # Pair
        if 2 in rank_counts.values():
            pair_rank = [rank for rank, count in rank_counts.items() if count == 2][0]
            other_ranks = [rank for rank in ranks if rank != pair_rank]
            return "Pair", [pair_rank] * 2 + other_ranks[:3]
        # High Card
        return "High Card", ranks

    # This answers questions such as "What are the odds of having at least a pair?"
    def evaluate_rankings_for_odds_calculation(self):
        ranks = sorted([self.RANKS[card.rank] for card in self.cards], reverse=True)
        suits = [card.suit for card in self.cards]

        # Check for flush and straight
        flush = len(set(suits)) == 1
        straight = self.is_sequence(ranks) or (ranks[-4:] == [5, 4, 3, 2] and ranks[0] == 14)  # A,2,3,4,5 straight

        # Count the occurrences of each rank
        rank_counts = Counter(ranks)

        # Check for multiples
        multiples = {count for count in rank_counts.values() if count > 1}
        is_four_of_a_kind = 4 in multiples
        is_three_of_a_kind = 3 in multiples
        is_pair = 2 in multiples
        is_two_pair = list(rank_counts.values()).count(2) >= 2
        is_full_house = is_three_of_a_kind and is_pair

        hand_results = {
            "Royal Flush": flush and ranks[:5] == [14, 13, 12, 11, 10],
            "Straight Flush": flush and straight,
            "Four of a Kind": is_four_of_a_kind,
            "Full House": is_full_house,
            "Flush": flush,
            "Straight": straight,
            "Three of a Kind": is_three_of_a_kind,
            "Two Pair": is_two_pair,
            "Pair": is_pair
        }

        return hand_results

    # This answers questions such as "what are the odds of the best hand being a pair?"
    # def evaluate_odds_for_each_hand(self):
    #     # Convert cards to rank numbers and sort
    #     ranks = sorted([self.RANKS[card.rank] for card in self.cards], reverse=True)
    #     suits = [card.suit for card in self.cards]
    #
    #     # Check for flush and straight
    #     flush = len(set(suits)) == 1
    #     straight = self.is_sequence(ranks) or (ranks[:5] == [14, 5, 4, 3, 2])  # Including A,2,3,4,5 straight
    #
    #     # Check for four of a kind, three of a kind, pairs
    #     rank_counts = {rank: ranks.count(rank) for rank in ranks}
    #     max_count = max(rank_counts.values())
    #
    #     hand_results = {
    #         "Royal Flush": flush and ranks[:5] == [14, 13, 12, 11, 10],
    #         "Straight Flush": flush and straight,
    #         "Four of a Kind": max_count == 4,
    #         "Full House": max_count == 3 and len(set(rank_counts.values())) == 2,
    #         "Flush": flush,
    #         "Straight": straight,
    #         "Three of a Kind": max_count == 3,
    #         "Two Pair": list(rank_counts.values()).count(2) == 2,
    #         "Pair": 2 in rank_counts.values(),
    #         "High Card": max_count == 1  # If no other hand is formed, it's a high card
    #     }
    #
    #     return hand_results
