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
    def __init__(self, name, user_id, chips, position, profile_picture):
        self.client_socket = None
        # Variables required for each player
        self.name = name
        self.user_id = user_id
        self.profile_picture = profile_picture
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
        self.number_of_times_raised = 0
        self.number_of_times_all_in = 0
        self.number_of_times_called = 0
        self.number_of_times_checked = 0
        self.number_of_times_folded = 0
        self.number_of_times_acted = 0
        self.won_round = False
        self.won_game = False
        self.finishing_position = 0
        self.aggressiveness_score = 0
        self.conservativeness_score = 0

    # Add a card to the player's hand
    def add_card(self, card):
        self.hand.cards.append(card)

    # Debug method to set a player's chips
    def debug_set_chips(self, amount):
        self.chips = amount

    # Debug method to set a player's cards
    def debug_set_cards(self, cards):
        self.hand.cards = cards


class Board:
    def __init__(self):
        self.__cards = []

    def get_board(self):
        return self.__cards

    def reset_board(self):
        self.__cards = []

    def add_card_to_board(self, card):
        self.__cards.append(card)


class Game:
    def __init__(self, starting_chips=200, player_limit=6):
        self._debugging_enabled = False
        self.players: List[Player] = []
        self.available_positions = ["top_left", "top_middle", "top_right", "bottom_right", "bottom_middle",
                                    "bottom_left"]
        self.last_position_index = -1
        self.__pot = Pot()
        self.starting_chips = starting_chips
        self.board = Board()  # The community cards are represented by the board
        self.deck = Deck()
        self.__current_player_turn = -1
        self.game_started = False
        self.__small_blind = 5
        self.__big_blind = 10
        self.__dealer_position = -1
        self.__small_blind_position = -1
        self.__big_blind_position = -1
        self.__current_highest_bet = self.__big_blind
        self.current_round = "preflop"
        self.player_limit = player_limit
        # total_pot is how much the winner will win from every player including their own chips
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
        self.winner_message = None
        self.message = ""

    def debug_set_community_cards(self, cards):
        self.board.reset_board()
        for card in cards:
            self.board.add_card_to_board(card)

    def __is_betting_round_over(self):
        active_players = self.__get_players_for_showdown()
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

    def __start_new_round(self, round_type):
        if round_type == "preflop":
            # First player to act: player after the big blind
            # Last player to act: Big blind player
            self.first_player_to_act = self.__get_next_active_player(self.__big_blind_position, False)
            self.last_player_to_act = self.__big_blind_position
        elif round_type == "flop":
            # First player to act: small blind player or first active player after
            # Last player to act: dealer player or first active player before
            self.first_player_to_act = self.__get_next_active_player(self.__dealer_position, False)
            self.last_player_to_act = self.__get_previous_active_player(self.__small_blind_position, False)
            self.__current_player_turn = self.first_player_to_act
        else:
            self.first_player_to_act = self.__get_next_active_player(self.first_player_to_act, True)
            self.last_player_to_act = self.__get_previous_active_player(self.last_player_to_act, True)
            self.__current_player_turn = self.first_player_to_act

        print("-------------- START_NEW_ROUND ----------------")
        print(f"first_player_to_act: {self.first_player_to_act}")
        print(f"last_player_to_act: {self.last_player_to_act}")
        print(f"current_player_turn: {self.__current_player_turn}")
        print(f"has self.first_player_acted: {self.first_player_acted}")
        print("------------------------------")

        self.first_player_acted = False

    def __handle_player_leaving(self, leaving_player):
        # Check if the leaving player is first or last to act and update accordingly
        print(f"player {leaving_player} leaving!")
        print(f"First player to act: {self.first_player_to_act}, Last player to act: {self.last_player_to_act}")
        if leaving_player == self.players[self.__current_player_turn]:
            if self.players[self.first_player_to_act] == leaving_player:
                print("First player to act == leaving player")
                self.first_player_to_act = self.__get_next_active_player(self.first_player_to_act, False)
            elif self.players[self.last_player_to_act] == leaving_player:
                print("Last player to act == leaving player")
                self.non_active_player = leaving_player
                if self.__is_betting_round_over():
                    self.__progress_to_next_betting_round()
                    return
                self.last_player_to_act = self.__get_previous_active_player(self.last_player_to_act, False)

            print("Updating current player turn")
            self.__current_player_turn = self.__get_next_active_player(self.__current_player_turn, False)

    def __get_next_active_player(self, current_position, use_current_player):
        original_player = current_position

        if len(self.__get_players_for_showdown()) == 0:
            # If the server is force terminated, stop it from being in an infinite loop
            print("ERROR ERROR ERROR: NO PLAYERS AVAILABLE FOR GET_NEXT_ACTIVE_PLAYER")
            print(f"{[f'{player.name}: {player.all_in}, {player.busted}, {player.folded}' for player in self.players]}")
            return 0

        if use_current_player:
            if self.__is_player_active(current_position):
                print(f"(get_next_active_player) FINAL: {current_position}")
                return current_position

        # The loop below should check if all the players are looped through, and should return the original player
        # in order to avoid an infinite loop below (there needs to be an exit condition when there are no available
        # players)
        checked_once = False
        while True:
            if checked_once:
                if current_position == original_player:
                    print("Returning 999")
                    return 999

            current_position = (current_position + 1) % len(self.players)
            print(f"(get_next_active_player): {current_position}")
            if self.__is_player_active(current_position):
                return current_position
            checked_once = True

    def __get_previous_active_player(self, current_position, use_current_player):
        original_player = current_position

        if len(self.__get_players_for_showdown()) == 0:
            # If the server is force terminated, stop it from being in an infinite loop
            print("ERROR ERROR ERROR: NO PLAYERS AVAILABLE FOR GET_NEXT_ACTIVE_PLAYER")
            print(f"{[f'{player.name}: {player.all_in}, {player.busted}, {player.folded}' for player in self.players]}")
            return 0

        if use_current_player:
            if self.__is_player_active(current_position):
                print(f"(get_previous_active_player) FINAL: {current_position}")
                return current_position

        checked_once = False
        while True:
            if checked_once:
                if current_position == original_player:
                    print("Returning 999")
                    return 999

            current_position = (current_position - 1) % len(self.players)
            print(f"(get_previous_active_player): {current_position}")
            if self.__is_player_active(current_position):
                return current_position
            checked_once = True

    def __is_player_active(self, current_position):
        return not (self.players[current_position].folded or
                    self.players[current_position].disconnected or
                    self.players[current_position].busted or
                    self.players[current_position].all_in)

    def __is_player_active_showdown(self, current_position):
        return not (self.players[current_position].folded or
                    self.players[current_position].disconnected or
                    self.players[current_position].busted)

    def __get_players_for_showdown(self):
        return [p for index, p in enumerate(self.players) if self.__is_player_active_showdown(index)]

    def __get_active_players(self):
        return [p for index, p in enumerate(self.players) if self.__is_player_active(index)]

    def __is_only_one_player_active(self):
        active_players = self.__get_players_for_showdown()
        print(f"(ONLY_ONE_PLAYER_ACTIVE) active_players: {[player.name for player in active_players]}")
        return len(active_players) == 1

    def __progress_to_next_betting_round(self):
        # Reset the players who have acted this betting round
        self.players_acted = []
        if self.current_round == "preflop":
            self.__flop()
            self.current_round = "flop"
        elif self.current_round == "flop":
            self.__turn_river()
            self.current_round = "turn"
        elif self.current_round == "turn":
            self.__turn_river()
            self.current_round = "river"
        elif self.current_round == "river":
            showdown_data = self.__showdown()

            if self.start_round() == "game_completed":
                print("game completed!")
                return {"success": True, "game_completed": True, "showdown_data": showdown_data}

            return {"success": True, "type": "showdown_data", "showdown_data": showdown_data}

        self.__start_new_round(self.current_round)

    def __skip_through_betting_rounds(self):
        if self.current_round == "preflop":
            self.__flop()
            self.current_round = "flop"
        if self.current_round == "flop":
            self.__turn_river()
            self.current_round = "turn"
        if self.current_round == "turn":
            self.__turn_river()
            self.current_round = "river"
        message = self.__showdown()

        return message

    # This method determines the winner from the eligible players by first comparing player's hand rankings
    # and then comparing their cards individually in case of more complicated situations where required
    def __determine_winner_from_eligible_players(self, best_hands, eligible_players):
        # Filter out the best hands only for eligible players
        eligible_best_hands = {player: hand for player, hand in best_hands.items() if player in eligible_players}
        print(f"eligible_best_hands: {eligible_best_hands}")

        # Determine the maximum hand ranking for these players
        max_rank = max(eligible_best_hands.values(), key=lambda x: x[0])[0]
        print(f"max_rank: {max_rank}")

        # Filter players using the max hand ranking
        max_rank_players = {player: cards for player, (rank, cards) in eligible_best_hands.items() if rank == max_rank}
        print(f"max_rank_players: {max_rank_players}")

        # Sort players based on their hand rank and then by card values if ranks are equal
        sorted_players = sorted(max_rank_players.keys(), key=lambda x: list(sorted(max_rank_players[x], reverse=True)),
                                reverse=True)

        print(f"sorted_players: {sorted_players}")

        # The first player is the one with the best cards
        winners = [sorted_players[0]]
        print(f"winners: {winners}")

        # Check for ties
        for player in sorted_players[1:]:
            if max_rank_players[player] == max_rank_players[winners[0]]:
                winners.append(player)
            else:
                break

        return winners

    # This method finds the best possible player hand and community card combination for each player in a given list
    def __evaluate_player_hands(self, remaining_players):
        best_hand_per_player = {}

        for player in remaining_players:
            # Combine the player's deck and the community cards
            all_seven_cards = player.hand.cards + self.board.get_board()
            best_rank = -1
            best_cards = None

            # Iterate through every combination of 5 out of the 7 total cards
            for combo in combinations(all_seven_cards, 5):
                test_hand = Hand(list(combo))
                rank, cards = test_hand.evaluate_strength()
                rank_index = self.hand_rankings.index(rank)

                # Re-evaluate the strength of the best hand ranking each time if needed
                if rank_index > best_rank or (rank_index == best_rank and cards > best_cards):
                    best_rank = rank_index
                    best_cards = cards

            best_hand_per_player[player] = (best_rank, best_cards)
            print(f"player: {player.name}, best hand: {best_hand_per_player[player]}")

        return best_hand_per_player

    # Create pots based on any all_ins and return a list of pots
    def __create_pots(self, remaining_players):
        pots = []
        last_all_in_amount = 0

        all_in_players = sorted((player for player in remaining_players if player.all_in), key=lambda p: p.current_bet)

        for all_in_player in all_in_players:
            pot_amount = (all_in_player.current_bet - last_all_in_amount) * len(remaining_players)
            if pot_amount > 0:
                pots.append((pot_amount, list(remaining_players)))

            last_all_in_amount = all_in_player.current_bet
            remaining_players.remove(all_in_player)

        main_pot = self.__pot.chips - sum(pot[0] for pot in pots)

        # Add the main pot only if there are players left who haven't gone all-in
        if remaining_players and main_pot > 0:
            pots.append((main_pot, remaining_players))

        return pots

    def __showdown(self):
        remaining_players = self.__get_players_for_showdown()
        for player in remaining_players:
            player.won_round = False

        # Find the best hand for every single player in a list
        best_hand_per_player = self.__evaluate_player_hands(remaining_players)
        pots = self.__create_pots(remaining_players)

        winner_messages = []
        for pot_amount, eligible_players in pots:
            winning_players = self.__determine_winner_from_eligible_players(best_hand_per_player, eligible_players)
            num_winners = len(winning_players)

            # Determine winners and distribute the pot
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
                    winning_player.finishing_position = 1
            else:
                winner_message = "It's a tie between " + ", ".join(
                    [player.name for player in winning_players]) + f" for {pot_amount} chips!"
                pot_share = pot_amount // num_winners
                extra_chips = pot_amount % num_winners
                for player in winning_players:
                    player.won_round = True
                    print(f"set {player.name}.won_round to True")
                    player.chips += pot_share

                # Give the extra chip to only one of the winners
                winning_players[0].chips += extra_chips

            winner_messages.append(winner_message)

        self.winner_message = "\n".join(winner_messages)
        self.__pot.reset_chips()
        return self.winner_message

    # Public method used to get the initial state of the game when first connecting to the lobby
    def get_initial_state(self):
        state = {
            'players': [{'name': p.name, 'user_id': p.user_id, 'chips': p.chips, 'position': p.position,
                         'profile_picture': p.profile_picture} for p in self.players],
            'pot': self.__pot.chips,
            'board': [str(card) for card in self.board.get_board()],
            'player_limit': self.player_limit,
        }
        return state

    def __get_game_state_for_player(self, player):
        # A part of the purpose of this method is to only send each individual player's cards to the corresponding
        # player to prevent any possible cheating where a player could potentially find out another player's cards
        # Below is the state of the game to be sent to a specific player
        state = {
            'players': [{'name': p.name, 'user_id': p.user_id, 'chips': p.chips, 'current_bet': p.current_bet,
                         "blinds": p.blinds, "dealer": p.dealer, "folded": p.folded, "disconnected": p.disconnected,
                         "busted": p.busted} for p in self.players],
            'pot': self.__pot.chips,
            'board': [str(card) for card in self.board.get_board()],
            'current_player_turn': self.__current_player_turn,
            'hand': [str(card) for card in player.hand.cards],
            'message': self.message
        }
        print(f"(game_logic.py): returning {state} to {player}")
        return state

    # Public method used to get the showdown state of the game (including every player's cards)
    def get_game_state_for_showdown(self):
        state = {
            'players': [{'name': p.name, 'user_id': p.user_id, 'chips': p.chips, 'current_bet': p.current_bet,
                         "blinds": p.blinds, "dealer": p.dealer, "folded": p.folded, "disconnected": p.disconnected,
                         "busted": p.busted, "hand": [str(card) for card in p.hand.cards], "won_round": p.won_round} for
                        p in self.players],
            'pot': self.__pot.chips,
            'board': [str(card) for card in self.board.get_board()],
            'current_player_turn': self.__current_player_turn,
            'winner_message': self.winner_message
        }
        print(f"(game_logic.py): returning {state}")
        return state

    # This is the state of the game to send when the poker game is over (there is one winner)
    def get_game_state_for_completed(self):
        state = {
            'players': [
                {'name': p.name, 'user_id': p.user_id, 'chips': p.chips, "won_game": p.won_game, "folded": p.folded,
                 "disconnected": p.disconnected, "busted": p.busted} for p in
                self.players],
            'pot': self.__pot.chips,
            'board': [str(card) for card in self.board.get_board()]
        }
        print(f"(game_logic.py): returning {state}")
        return state

    def get_game_state_for_reconnecting_player(self, player):
        state = {
            'players': [{'name': p.name, 'user_id': p.user_id, 'chips': p.chips, 'current_bet': p.current_bet,
                         "blinds": p.blinds, "dealer": p.dealer, "folded": p.folded, "disconnected": p.disconnected,
                         "busted": p.busted, "position": p.position, "profile_picture": p.profile_picture} for p in
                        self.players],
            'pot': self.__pot.chips,
            'board': [str(card) for card in self.board.get_board()],
            'current_player_turn': self.__current_player_turn,
            'hand': [str(card) for card in player.hand.cards],
            'player_limit': self.player_limit
        }
        print(f"(game_logic.py): returning {state} to {player}")
        return state

    def send_game_state(self):
        # Prepare the game state for each player and return it
        game_states = {}
        for player in self.players:
            game_states[player.user_id] = self.__get_game_state_for_player(player)
        return game_states

    def get_player_left_state(self):
        # The state of a game after a player has left
        state = {
            'players': [{'name': p.name, 'user_id': p.user_id, 'chips': p.chips, 'position': p.position,
                         'profile_picture': p.profile_picture}
                        for p in self.players],
            'pot': self.__pot.chips,
            'board': [str(card) for card in self.board.get_board()],
            'current_player_turn': self.__current_player_turn,
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
                self.__handle_player_leaving(player)

    def __deal_cards(self, num_cards, player):
        if not player.disconnected:
            for i in range(num_cards):
                card = self.deck.deal_card()
                player.add_card(card)

    # This method is used to start a new poker round
    def start_round(self):
        # First it resets all the default attributes needed for a poker round
        self.board.reset_board()
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
                self.__deal_cards(2, player)
            if not player.busted and player.chips == 0 and player.all_in:
                player.busted = True
                self.next_available_finishing_position -= 1
                player.finishing_position = self.next_available_finishing_position
            else:
                player.all_in = False

            if player.disconnected:
                player.folded = True

        # If there is only one active player left in a game, the game is completed
        if len(self.__get_active_players()) == 1:
            print("start_round: get_active_players() == 1")
            # end the game
            self.game_completed = True
            return "game_completed"

        # Reset the list of players who have acted in this round
        self.players_acted = []

        self.__current_highest_bet = self.__big_blind
        self.current_round = "preflop"
        self.first_player_to_act = 0
        self.last_player_to_act = len(self.players) - 1
        self.first_player_acted = False

        # ----- DEBUGGING METHODS -----------

        # The debugging_enabled variable is used to only run the code once at the start of the game so that any
        # subsequent Poker rounds or usage of the start_round() method work as intended
        if self._debugging_enabled:
            debug_player1_chips = 50
            debug_player2_chips = 80
            debug_player3_chips = 100
            debug_player4_chips = 150

            # Royal Flush beats everything else
            debug_community_cards = [Card("Hearts", "10"), Card("Hearts", "Jack"), Card("Hearts", "Queen"),
                                     Card("Spades", "3"), Card("Hearts", "3")]
            debug_player1_cards = [Card("Hearts", "King"), Card("Hearts", "Ace")]  # Royal flush (10 to Ace)
            debug_player2_cards = [Card("Diamonds", "3"), Card("Clubs", "3")]  # Four of a kind
            debug_player3_cards = [Card("Hearts", "8"), Card("Hearts", "9")]  # Straight flush (8 to Queen)
            # Expected outcome: Player1 has a Royal Flush. Nobody else has a Royal Flush, so they win the pot.

            self.debug_set_community_cards(debug_community_cards)
            self.players[0].debug_set_cards(debug_player1_cards)
            self.players[0].debug_set_chips(debug_player1_chips)
            self.players[1].debug_set_cards(debug_player2_cards)
            self.players[1].debug_set_chips(debug_player2_chips)
            self.players[2].debug_set_cards(debug_player3_cards)

            self.current_round = "preflop"
            self._debugging_enabled = False

        # ---- END OF DEBUGGING METHODS ----

        self.__handle_shifting_positions_at_start()
        self.__handle_posting_blinds()

        self.__start_new_round(self.current_round)

    # Method to handle shifting the blinds and dealer button at the start of a round
    def __handle_shifting_positions_at_start(self):
        self.__dealer_position = self.__get_next_active_player(self.__dealer_position, False)
        self.__small_blind_position = self.__get_next_active_player(self.__dealer_position, False)
        self.__big_blind_position = self.__get_next_active_player(self.__small_blind_position, False)
        self.__current_player_turn = self.__get_next_active_player(self.__big_blind_position, False)
        print(f"Current player turn: {self.__current_player_turn}")

    # Method to handle posting the blinds (making every player pay the money they need to pay because of the blinds)
    def __handle_posting_blinds(self):
        if self.players[self.__small_blind_position].chips > self.__small_blind:
            self.players[self.__small_blind_position].chips -= self.__small_blind
            self.players[self.__small_blind_position].current_bet = self.__small_blind
            self.__pot.add_chips(self.__small_blind)
        else:
            self.players[self.__small_blind_position].current_bet = self.players[self.__small_blind_position].chips
            self.players[self.__small_blind_position].chips = 0
            self.players[self.__small_blind_position].all_in = True
            self.__pot.add_chips(self.players[self.__small_blind_position].current_bet)
        if self.players[self.__big_blind_position].chips > self.__big_blind:
            self.players[self.__big_blind_position].chips -= self.__big_blind
            self.players[self.__big_blind_position].current_bet = self.__big_blind
            self.__pot.add_chips(self.__big_blind)
        else:
            self.players[self.__big_blind_position].current_bet = self.players[self.__big_blind_position].chips
            self.players[self.__big_blind_position].chips = 0
            self.players[self.__big_blind_position].all_in = True
            self.__pot.add_chips(self.players[self.__big_blind_position].current_bet)

        self.players[self.__small_blind_position].blinds.append("SB")
        self.players[self.__big_blind_position].blinds.append("BB")
        self.players[self.__dealer_position].dealer = True

    # This method deals the flop
    def __flop(self):
        # A card is discarded by the dealer before dealing the flop, turn, and river (Texas Hold'Em poker tradition)
        self.deck.deal_card()
        # Deal 3 cards
        for i in range(3):
            card = self.deck.deal_card()
            self.board.add_card_to_board(card)

    # This method deals the turn or the river as they have the same functionality
    def __turn_river(self):
        # A card is discarded by the dealer before dealing the flop, turn, and river
        self.deck.deal_card()

        card = self.deck.deal_card()
        self.board.add_card_to_board(card)

    # The logic for when a player folds
    def __player_fold(self, player):
        message = f"{player.name} folds"

        player.folded = True
        player.number_of_times_folded += 1
        if player == self.players[self.first_player_to_act]:
            self.first_player_to_act = self.__get_next_active_player(self.first_player_to_act, False)
        elif player == self.players[self.last_player_to_act]:
            self.non_active_player = player
            self.last_player_to_act = self.__get_previous_active_player(self.last_player_to_act, False)

        return message

    # The logic for when a player calls
    def __player_call(self, player):
        bet_amount = self.__current_highest_bet - player.current_bet
        if player.chips >= bet_amount:
            player.chips -= bet_amount
            self.__pot.add_chips(bet_amount)
            player.current_bet = self.__current_highest_bet
        else:
            # if they player does not have enough chips to call, they go all in and side pots are handled later
            player.current_bet += player.chips
            self.__pot.add_chips(player.chips)
            player.chips = 0

        if player.chips == 0:
            player.all_in = True
            player.number_of_times_all_in += 1
            self.non_active_player = player

        if bet_amount == 0:
            player.number_of_times_checked += 1
        else:
            player.number_of_times_called += 1

        self.players_acted.append(player)
        if bet_amount == 0:
            message = f"{player.name} checks"
        else:
            message = f"{player.name} calls {bet_amount} chips"

        return {"success": True, "message": message}

    # The logic for when a player raises
    def __player_raise(self, player, raise_amount):
        # The player raises over the current highest bet
        total_bet = raise_amount + player.current_bet
        if total_bet <= self.__current_highest_bet or raise_amount <= 0:
            return {"success": False,
                    "error": f"You need to raise by at least {self.__current_highest_bet - player.current_bet}."}
        if raise_amount > player.chips:
            return {"success": False, "error": "You don't have enough chips to raise this amount."}
        else:
            player.chips -= raise_amount
            self.__pot.add_chips(raise_amount)
            player.current_bet = total_bet
            self.__current_highest_bet = total_bet
            message = f"{player.name} raises by {raise_amount} chips to a total of {total_bet} chips"
            print(message)

            if player.chips == 0:
                player.all_in = True
                player.number_of_times_all_in += 1
                self.non_active_player = player

            player.number_of_times_raised += 1

            # Reset the players acted list as everyone needs to agree on a new amount to bet on
            self.players_acted = []
            self.players_acted.append(player)
            return {"success": True, "message": message}

    # The method used to process any player action, making use of the methods above
    def process_player_action(self, player, action, raise_amount):
        self.non_active_player = None
        self.message = ""
        # Check if it's the player's turn
        if player != self.players[self.__current_player_turn]:
            return {"success": False, "error": "It's not your turn!"}

        # Defensive programming: if the game hasn't started yet, nobody should be able to act yet.
        if not self.game_started:
            return {"success": False, "error": "The game has not started yet."}

        # IF THERE IS ONLY 1 PLAYER LEFT, EVALUATE THE WIN CONDITION OR ELSE THERE WILL BE AN INFINITE LOOP
        if player.folded:
            return {"success": False, "error": "This player has folded."}
        if action == 'fold':
            self.message = self.__player_fold(player)
            print(self.message)

        elif action == 'call':
            action_response = self.__player_call(player)
            if not action_response['success']:
                return action_response
            else:
                self.message = action_response['message']

        elif action == 'raise':
            action_response = self.__player_raise(player, raise_amount)
            if not action_response['success']:
                return action_response
            else:
                self.message = action_response['message']

        player.number_of_times_acted += 1

        print(
            f"About to check if only one player active in list of active players: {self.__get_players_for_showdown()}")
        # Check if everyone has folded apart from one player
        if self.__is_only_one_player_active():
            # The remaining active player wins the pot
            remaining_player = self.__get_players_for_showdown()[0]
            # remaining_player = self.get_active_players()[0]
            remaining_player.chips += self.__pot.chips
            self.message = f"{remaining_player.name} wins the pot ({self.__pot.chips} chips) as everyone else folded!"
            self.__pot.reset_chips()
            if self.start_round() == "game_completed":
                print("game completed!")
                return {"success": True, "type": "game_completed"}
        elif self.__is_betting_round_over():
            # If the betting round is over, check if there are still remaining players who are not all in
            if [player.all_in for player in self.__get_players_for_showdown()].count(
                    False) > 1 and self.current_round != "river":
                print(f"{self.current_round} round over!")
                self.__progress_to_next_betting_round()
            else:
                print("skipping through Poker rounds")
                self.__skip_through_betting_rounds()
                return {"success": True, "type": "skip_round", "showdown": True}
        else:
            # If the betting round is not over, go to the next player's turn
            next_player_index = self.__get_next_active_player(self.__current_player_turn, False)
            if next_player_index == 999:
                print("skipping through Poker rounds")
                self.__skip_through_betting_rounds()
                return {"success": True, "type": "skip_round", "showdown": True}
            else:
                self.__current_player_turn = next_player_index

        return {"success": True, "message": self.message}


class Pot:
    def __init__(self):
        self.chips = 0

    def add_chips(self, amount):
        self.chips += amount

    def reset_chips(self):
        self.chips = 0


class Hand:
    def __init__(self, cards):
        self.cards = cards

    # This is a constant as denoted by the name being fully uppercase
    RANKS = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
             'Jack': 11, 'Queen': 12, 'King': 13, 'Ace': 14}

    def __count_ranks_and_suits(self):
        ranks = sorted([self.RANKS[card.rank] for card in self.cards])
        suits = [card.suit for card in self.cards]
        return ranks, suits

    # This method checks if there is a flush in a given deck
    def __check_flush(self, suits):
        suit_counts = Counter(suits)
        return any(count >= 5 for count in suit_counts.values()), suit_counts

    # This method is adapted to work with both of the evaluation methods below
    def __check_straight(self, ranks):
        straight = False
        unique_ranks = sorted(set(ranks))
        for i in range(len(unique_ranks) - 4):
            if unique_ranks[i + 4] - unique_ranks[i] == 4:
                straight = True
                break
        if {14, 2, 3, 4, 5}.issubset(set(ranks)):
            straight = True
        return straight

    def __check_straight_flush(self, suit_counts):
        straight_flush = royal_flush = False
        for suit, count in suit_counts.items():
            if count >= 5:
                flush_ranks = sorted([self.RANKS[card.rank] for card in self.cards if card.suit == suit], reverse=True)
                if self.__check_straight(flush_ranks):
                    straight_flush = True
                    if flush_ranks[:5] == [14, 13, 12, 11, 10]:  # Checking for Ace high straight flush (Royal Flush)
                        royal_flush = True
        return straight_flush, royal_flush

    # This method evaluates the strength of a 5 card Poker hand and returns the highest card ranking
    # Some helper methods can not be used in this method due to the way it returns ranks as well due to this method
    # being used in the context of determining a winner as part of a showdown
    def evaluate_strength(self):
        # Convert cards to rank numbers and sort
        ranks, suits = self.__count_ranks_and_suits()

        # Check for flush and straight
        flush, suit_counts = self.__check_flush(suits)
        straight = self.__check_straight(ranks)

        # Check for four of a kind, three of a kind, pairs
        rank_counts = {rank: ranks.count(rank) for rank in ranks}
        max_count = max(rank_counts.values())

        straight_flush, royal_flush = self.__check_straight_flush(suit_counts)

        # Royal Flush
        if royal_flush:
            return "Royal Flush", ranks
        # Straight Flush
        if straight_flush:
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

    # This method returns a dictionary of all the possible card rankings made with a 7 card deck
    def evaluate_rankings_for_odds_calculation(self):
        ranks, suits = self.__count_ranks_and_suits()

        # Check for flush
        is_flush, suit_counts = self.__check_flush(suits)

        # Check for straight
        is_straight = self.__check_straight(ranks)

        # Count the occurrences of each rank
        rank_counts = Counter(ranks)

        # Check for multiples
        is_four_of_a_kind = 4 in rank_counts.values()
        is_three_of_a_kind = is_four_of_a_kind or 3 in rank_counts.values()

        # Check for pairs (including hands with a three/four of a kind)
        pair_counts = sum(1 for count in rank_counts.values() if count == 2)
        is_pair = pair_counts > 0 or is_three_of_a_kind or is_four_of_a_kind
        is_two_pair = pair_counts > 1 or (pair_counts == 1 and is_three_of_a_kind)

        # Check for full house (three of a kind and at least one pair)
        is_full_house = is_three_of_a_kind and pair_counts > 0

        # For straight flush and royal flush, we need to check if the flush cards form a straight
        is_straight_flush, is_royal_flush = self.__check_straight_flush(suit_counts)

        hand_results = {
            "Royal Flush": is_royal_flush,
            "Straight Flush": is_straight_flush,
            "Four of a Kind": is_four_of_a_kind,
            "Full House": is_full_house,
            "Flush": is_flush,
            "Straight": is_straight,
            "Three of a Kind": is_three_of_a_kind,
            "Two Pair": is_two_pair,
            "Pair": is_pair
        }

        return hand_results