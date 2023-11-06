import datetime
import socket
import threading
import json
from logic.database_interaction import DatabaseInteraction
from logic.game_logic import Game, Player
from typing import Dict
import time


class LobbyServer:
    def __init__(self, host='127.0.0.1', port=12345):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.server_socket.listen(0)

        self.database_interaction = DatabaseInteraction()
        self.lobbies: Dict[str, Game] = {}  # I have explicitly used type hinting for easier development

    def start(self):
        print("Server started...")
        while True:
            client_socket, addr = self.server_socket.accept()
            client_handler = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_handler.start()

    def handle_client(self, client_socket):
        buffer = ""
        while True:
            try:
                data = client_socket.recv(16384)
                if not data:
                    print("No data from client socket, searching for disconnected player")
                    user_id, lobby_id = self.find_disconnected_player(client_socket)
                    print(f"User_id: {user_id}, Lobby_id: {lobby_id})")
                    if user_id and lobby_id:
                        if not self.find_player_from_user_id(user_id, self.lobbies[lobby_id]).disconnected:
                            self.leave_lobby(user_id, lobby_id, client_socket)
                    break
            except ConnectionResetError:
                print("Connection was reset by client.")
                user_id, lobby_id = self.find_disconnected_player(client_socket)
                if user_id and lobby_id:
                    self.leave_lobby(user_id, lobby_id, client_socket)
                break

            # Decoding the received bytes to a string before appending to the buffer
            buffer += data.decode('utf-8')

            # Processing each message in the buffer
            while '\n' in buffer:
                message, buffer = buffer.split('\n', 1)
                try:
                    # Parsing the message instead of the whole data
                    request = json.loads(message)
                    print(f"Request: {request}")
                    print(f"Client socket: {client_socket}")

                    response = None
                    if request['type'] == 'get_all_lobbies':
                        print("getting lobbies")
                        response = self.get_all_lobbies(request)
                    elif request['type'] == 'create_lobby':
                        print("creating lobby")
                        response = self.create_lobby(request)
                    elif request['type'] == 'join_lobby':
                        print("joining lobby")
                        response = self.join_lobby(request, client_socket)
                    elif request['type'] == 'leave_lobby':
                        print(f"PLAYER LEAVING LOBBY: {client_socket}")
                        response = self.leave_lobby(request['user_id'], request['lobby_id'], client_socket)
                    elif request["type"] == "start_game":
                        self.handle_start_game(request["lobby_id"])
                        continue
                    elif request["type"] == "bet":
                        response = self.process_player_action(request, client_socket)
                    elif request["type"] == "send_chat":
                        try:
                            lobby_id = request['lobby_id']
                            chat_message = request['message']
                            self.broadcast_send_message(lobby_id, chat_message, client_socket)
                            response = {"success": True}
                        except Exception as e:
                            response = {"success": False, "error": e}
                    elif request["type"] == "start_next_round":
                        self.start_next_round(request)
                    elif request["type"] == "broadcast_showdown":
                        self.broadcast_showdown_game_state(request["lobby_id"])
                    elif request["type"] == "broadcast_new_game_state":
                        self.broadcast_game_state(request["lobby_id"], None, True)
                    elif request["type"] == 'broadcast_completed_game_state':
                        self.broadcast_completed_game_state(request['lobby_id'])
                    elif request["type"] == 'get_data_for_odds':
                        response = self.get_data_for_odds(request['user_id'], request['lobby_id'])
                    elif request["type"] == 'request_user_chips':
                        response = self.database_interaction.get_chip_balance_for_user(request['user_id'])
                    elif request["type"] == 'add_to_chip_balance_for_user':
                        response = self.database_interaction.add_to_chip_balance_for_user(request['user_id'],
                                                                                          request['amount'])
                    elif request['type'] == 'update_chip_balance_for_user':
                        response = self.database_interaction.update_chip_balance_for_user(request['user_id'],
                                                                                          request['amount'])
                    elif request['type'] == 'update_daily_game_limit':
                        response = self.database_interaction.update_daily_game_limit(request['user_id'],
                                                                                     request['new_limit'])
                    elif request['type'] == 'get_daily_game_limit':
                        response = self.database_interaction.get_daily_game_limit(request['user_id'])
                    elif request['type'] == 'update_daily_game_limit':
                        response = self.database_interaction.update_daily_game_limit(request['user_id'],
                                                                                  request['new_limit'])
                    elif request['type'] == 'get_and_check_to_reset_daily_games_played':
                        response = self.database_interaction.get_and_check_to_reset_daily_games_played(
                            request['user_id'])
                    elif request['type'] == 'update_rg_score':
                        response = self.database_interaction.update_rg_score(request['user_id'])
                    elif request['type'] == 'update_game_limit_after_completion':
                        response = ['type'] == self.database_interaction.update_game_limit_after_completion(
                            request['user_id'])
                    elif request['type'] == 'get_username':
                        response = self.database_interaction.get_username(request['user_id'])
                    elif request['type'] == 'get_top_players_by_attribute':
                        response = self.database_interaction.get_top_players_by_attribute(request['attribute'],
                                                                                          request['limit'])
                    elif request['type'] == 'get_top_players_by_chips':
                        response = self.database_interaction.get_top_players_by_chips(request['limit'])
                    elif request['type'] == 'add_to_attribute_for_user':
                        response = self.database_interaction.add_to_attribute_for_user(request['user_id'],
                                                                                       request['attribute'],
                                                                                       request['amount'])

                    if response is not None:
                        client_socket.sendall((json.dumps(response) + '\n').encode('utf-8'))
                        print(f"(handle client): Response: {response}")
                        print(f"Sent response to {client_socket}")

                except json.JSONDecodeError as e:
                    print(f"JSON Decode Error: {e}")
                    print(f"Data causing the error: {message}")
                    buffer = ""  # Clear the buffer to avoid parsing the same invalid data again

        client_socket.close()

    def start_next_round(self, request):
        print("STARTING NEXT ROUND!!")
        lobby_id = request.get("lobby_id")
        print("got lobby")
        game = self.lobbies[lobby_id]
        print("got game")
        start_round_response = game.start_round()
        print(f"start_round_response: {start_round_response}")
        if start_round_response == "game_completed":
            print("(server.py): game completed")
            # Add the chips that the player has won to their balance
            print(f"winning_player: {[player for player in game.players if player.won_game]}")
            winning_player = [player for player in game.players if player.won_game][0]
            print(f"Adding {game.total_pot} chips to {winning_player.name}")
            self.database_interaction.add_to_chip_balance_for_user(winning_player.user_id, game.total_pot)
            self.database_interaction.add_to_attribute_for_user(winning_player.user_id, "games_won", 1)
            game_id = self.database_interaction.get_game_id_from_lobby_id(lobby_id)
            self.database_interaction.end_game(game_id)
            game_duration = self.database_interaction.get_game_duration(game_id)

            for player in game.players:
                # Handle the relevant statistics for each player
                if player.amount_of_times_acted != 0:
                    # Avoid division by zero error in case the player left before acting
                    player.aggressiveness_score = round((player.amount_of_times_raised / player.amount_of_times_acted) *
                                                     100, 2)
                    player.conservativeness_score = round(((player.amount_of_times_folded +
                                                            player.amount_of_times_checked)
                                                           / player.amount_of_times_acted) * 100, 2)

                self.database_interaction.add_to_attribute_for_user(player.user_id, "games_played", 1)
                self.database_interaction.update_game_limit_after_completion(player.user_id)
                self.database_interaction.add_to_attribute_for_user(player.user_id, "total_play_time", game_duration)

                if player.won_game:
                    self.database_interaction.insert_game_results(game_id, player.user_id, player.finishing_position,
                                                                  game.total_pot, player.aggressiveness_score,
                                                                  player.conservativeness_score)
                    self.database_interaction.add_to_attribute_for_user(player.user_id, "games_won", 1)
                else:
                    self.database_interaction.insert_game_results(game_id, player.user_id, player.finishing_position,
                                                                  0, player.aggressiveness_score,
                                                                  player.conservativeness_score)

                self.database_interaction.update_average_scores(player.user_id, player.aggressiveness_score,
                                                                player.conservativeness_score)

            # BROADCAST GAME COMPLETED STATE
            self.broadcast_completed_game_state(lobby_id)
        else:
            self.broadcast_game_state(lobby_id, None, False)
        print("started new round")

    def find_disconnected_player(self, disconnected_socket):
        for lobby_id, game in self.lobbies.items():
            for player in game.players:
                if player.client_socket == disconnected_socket:
                    return player.user_id, lobby_id
        return None, None

    def find_player_from_user_id(self, user_id, game):
        return next((player for player in game.players if player.user_id == user_id), None)

    def get_data_for_odds(self, user_id, lobby_id):
        game = self.lobbies[lobby_id]
        player_cards = [[card.rank, card.suit] for card in [player for player in game.players if
                                                                   player.user_id == user_id][0].hand.cards]
        print(f"player_cards: {player_cards}")
        community_cards = [[card.rank, card.suit] for card in game.board]
        print(f"community_cards: {community_cards}")

        return player_cards, community_cards

    def process_player_action(self, request, client_socket):
        user_id = request['user_id']
        action = request['action']
        lobby_id = request['lobby_id']
        game = self.lobbies[lobby_id]
        player = self.find_player_from_user_id(user_id, game)
        raise_amount = request.get('amount', 0)

        action_response = game.process_player_action(player, action, raise_amount)

        print(f"action_resonse: {action_response}")

        return action_response

    def leave_lobby(self, user_id, lobby_id, client_socket):
        print("player leaving")
        if lobby_id not in self.lobbies:
            return {"success": False, "error": "Could not find lobby to remove player from"}

        game = self.lobbies[lobby_id]
        player = self.find_player_from_user_id(user_id, game)
        self.database_interaction.remove_player_from_lobby(player.user_id, lobby_id)

        # If there is only one player left
        if len(self.get_connected_players(game)) == 1:
            print("only one player left")
            self._handle_last_player_leaving(lobby_id)
            return {'success': True}

        if not game.game_started:
            game.remove_player(user_id, completely_remove=True)
            print(f"New player list: {game.players}")

            self._update_lobby_after_player_left(game, player, lobby_id, client_socket)
            print("broadcasted player left game state")
        else:
            game.remove_player(user_id, completely_remove=False)
            self.broadcast_game_state(lobby_id, client_socket, False)

        return {'success': True}

    def _update_lobby_after_player_left(self, game, player, lobby_id, client_socket):
        all_positions = ["top_left", "top_middle", "top_right", "bottom_right", "bottom_middle", "bottom_left"]

        leaving_player_position_index = all_positions.index(player.position)

        # Loop through the players after the leaving player and update their position as necessary
        print("========================================")
        print(f"Old positions: {game.available_positions}")
        for player in game.players:
            player_position_index = all_positions.index(player.position)
            print(f"Old position for {player.name}: {player.position}")
            if player_position_index > leaving_player_position_index:
                # Shift position one step to the left
                player.position = all_positions[player_position_index - 1]
                print(f"New position for {player.name}: {player.position}")
        # Modify the list of positions to include the last position again
        game.available_positions.insert(0, all_positions[game.last_position_index])
        game.last_position_index -= 1
        print(f"New positions: {game.available_positions}")
        print(f"All positions: {all_positions}")
        print(f"Leaving player position index: {leaving_player_position_index}")
        self.broadcast_player_left_game_state(lobby_id, client_socket)

    def _handle_last_player_leaving(self, lobby_id):
        print(f"Handling last player leaving lobby: {lobby_id}")
        # If the game has not yet started (not enough players connected), it is an abandoned lobby
        if self.lobbies[lobby_id].game_completed:
            self.database_interaction.set_lobby_status(lobby_id, "completed")
            for player in self.lobbies[lobby_id].players:
                print("-----------")
                print(f"Player {player.name}:")
                print(f"Amount of times acted: {player.amount_of_times_acted}")
                print(f"Amount of times called: {player.amount_of_times_called}")
                print(f"Amount of times checked: {player.amount_of_times_checked}")
                print(f"Amount of times folded: {player.amount_of_times_folded}")
                print(f"Amount of times raised: {player.amount_of_times_raised}")
                print(f"Amount of times gone all in: {player.amount_of_times_all_in}")
                print("-----------")

            # Handle game statistics and stuff
        else:
            self.database_interaction.set_lobby_status(lobby_id, "abandoned")
        del self.lobbies[lobby_id]

    def join_lobby(self, request, client_socket):
        print(f"JOINING LOBBY REQUEST: {request}")
        user_id = request["user_id"]
        lobby_id = request["lobby_id"]
        user_name = self.database_interaction.get_username(user_id)

        if lobby_id not in self.lobbies:
            print("could not return data. error: Lobby not found")
            return {"success": False, "error": "Lobby not found"}

        game = self.lobbies[lobby_id]

        # Handle what happens if the player is attempting to reconnect
        if game.game_started:
            player_to_reconnect = self.find_player_from_user_id(user_id, game)
            if player_to_reconnect is None:
                # Avoid an AttributeError by only checking if the player is disconnected if player_to_reconnect
                # is not None
                error_message = "Reconnecting player is not in player list"
            else:
                if player_to_reconnect.disconnected:
                    game.reconnect_player(user_id, client_socket)
                    self.database_interaction.join_lobby(user_id, lobby_id)

                    reconnecting_state = self.get_state_for_reconnecting_player(lobby_id, player_to_reconnect)
                    self.broadcast_game_state(lobby_id, client_socket, False)

                    return {"success": True, "type": "reconnecting", "user_id": user_id, "game_state":
                        reconnecting_state}

        # Defensive programming - don't allow a player to join if the lobby is full
        if len(game.players) == game.player_limit:
            return {"success": False, "error": "The lobby is already full!"}

        if not game.game_started:
            player = Player(user_name, user_id, chips=game.starting_chips, position=game.available_positions.pop(0))
            game.last_position_index += 1
            game.add_player(player, client_socket)

            self.database_interaction.join_lobby(user_id, lobby_id)

            initial_state = self.get_initial_state(lobby_id)
            print(f"INITIAL STATE: {initial_state}")
            self.broadcast_initial_game_state(lobby_id, client_socket)
            print(f"(server.py): broadcasted initial game state to everyone apart from {client_socket}")
            data_type = "initial_state"
            if len(game.players) == game.player_limit:
                game.start_round()
                data_type = "game_starting"
                game.game_started = True
                self.database_interaction.set_lobby_status(lobby_id, "in_progress")
                print("(server.py): set game._game_started to True so that the round can start")

            data_to_return = {"success": True, "type": data_type, "game_state": initial_state}
            print(data_to_return)
            return data_to_return

        return {"success": False, "error": error_message}

    def get_connected_players(self, game):
        return [player for player in game.players if not player.disconnected]

    def broadcast_game_state(self, lobby_id, current_client, broadcast_to_everyone):
        print("BROADCASTING GAME STATE TO EVERYONE")
        data_to_return_to_client = None
        if lobby_id in self.lobbies:
            game = self.lobbies[lobby_id]
            game_states = game.send_game_state()
            if broadcast_to_everyone:
                for player in self.get_connected_players(game):
                    user_id = player.user_id
                    player.client_socket.sendall((json.dumps({"type": "update_game_state", "user_id": user_id,
                                                              "game_state": game_states[user_id]}) + '\n').encode(
                        'utf-8'))
                    print(f"sent game states {game_states[user_id]} to user {user_id}")
            else:
                print(f"broadcasting game state to connected players: {self.get_connected_players(game)}")
                for player in self.get_connected_players(game):
                    print(f"Connected player: {player}: {player.disconnected}")
                    user_id = player.user_id
                    if current_client != player.client_socket:
                        player.client_socket.sendall((json.dumps({"type": "update_game_state", "user_id": user_id,
                                                                  "game_state": game_states[user_id]}) + '\n').encode(
                            'utf-8'))
                        print(f"sent game states {game_states[user_id]} to user {user_id}")
                    else:
                        data_to_return_to_client = {"type": "update_game_state", "user_id": user_id,
                                                    "game_state": game_states[user_id]}

            print("sent game state..")
            print(f"(broadcast_game_state) returning {data_to_return_to_client}")
            return data_to_return_to_client

    def broadcast_send_message(self, lobby_id, message, current_client):
        print("BROADCASTING chat message TO EVERYONE")
        if lobby_id in self.lobbies:
            game = self.lobbies[lobby_id]
            for player in self.get_connected_players(game):
                if player.client_socket != current_client:
                    user_id = player.user_id
                    player.client_socket.sendall(
                        (json.dumps({"type": "receive_message", "chat_message": message}) + '\n').encode(
                            'utf-8'))
                    print(f"sent message {message} to user {user_id}")

    def broadcast_showdown_game_state(self, lobby_id):
        print("BROADCASTING showdown GAME STATE TO EVERYONE")
        if lobby_id in self.lobbies:
            game = self.lobbies[lobby_id]
            game_state = game.get_game_state_for_showdown()
            for player in self.get_connected_players(game):
                user_id = player.user_id
                player.client_socket.sendall(
                    (json.dumps({"type": "update_showdown_state", "game_state": game_state}) + '\n').encode(
                        'utf-8'))
                print(f"sent game states {game_state} to user {user_id}")

            print("sent game state..")

    def broadcast_completed_game_state(self, lobby_id):
        print("BROADCASTING completed GAME STATE TO EVERYONE")
        if lobby_id in self.lobbies:
            game = self.lobbies[lobby_id]
            game_state = game.get_game_state_for_completed()
            for player in self.get_connected_players(game):
                user_id = player.user_id
                player.client_socket.sendall((json.dumps({"type": "update_completed_state", "game_state":
                    game_state}) + '\n').encode('utf-8'))
                print(f"sent completed game states {game_state} to user {user_id}")

            print("sent game state..")

    def broadcast_initial_game_state(self, lobby_id, current_client):
        print("BROADCASTING INITIAL GAME STATE NOT TO EVERYONE")
        game_state = self.get_initial_state(lobby_id)
        print(f"Initial game state to broadcast: {game_state}")
        for client_socket in self.get_clients_in_lobby(lobby_id):
            if client_socket != current_client:
                client_socket.sendall(
                    (json.dumps({"type": "initial_state", "game_state": game_state}) + '\n').encode('utf-8'))
                print(f"sent initial game state data to f{client_socket}")

    def broadcast_player_left_game_state(self, lobby_id, current_client):
        # BROADCAST INITIAL GAME STATE THEN GAME STATE (NOT TO CURRENT CLIENT THOUGH!)
        print("BROADCASTING PLAYER LEFT GAME STATE NOT TO EVERYONE")
        game_state = self.get_player_left_state(lobby_id)
        print(f"Initial game state to broadcast: {game_state}")
        for client_socket in self.get_clients_in_lobby(lobby_id):
            if client_socket != current_client:
                client_socket.sendall(
                    (json.dumps({"type": "player_left_game_state", "game_state": game_state}) + '\n').encode('utf-8'))
                print(f"sent initial game state data to f{client_socket}")

    def get_state_for_reconnecting_player(self, lobby_id, player):
        return self.lobbies[lobby_id].get_game_state_for_reconnecting_player(player)

    def get_player_left_state(self, lobby_id):
        return self.lobbies[lobby_id].get_player_left_state()

    def get_initial_state(self, lobby_id):
        return self.lobbies[lobby_id].get_initial_state()

    def handle_start_game(self, lobby_id):
        print("running handle_start_game")
        game = self.lobbies[lobby_id]
        if game.game_started:  # Check if the game is ready to start
            self.database_interaction.insert_game(lobby_id)  # Add the game to the games table
            self.broadcast_game_state(lobby_id, None, False)

    def get_all_lobbies(self, request):
        status_filter = request["status"]
        odds_filter = request["odds"]
        lobbies = []
        user_id = request["user_id"]
        reconnect_lobby = None

        if "in_progress" in status_filter:
            lobbies += self.database_interaction.get_all_lobbies("in_progress", odds_filter)
        lobbies += self.database_interaction.get_all_lobbies("waiting", odds_filter)
        # The code below checks if a player is already in the list of players in order to allow the player to reconnect
        for lobby in lobbies:
            lobby_id = lobby['lobby_id']
            if lobby_id in self.lobbies:
                if any(player.user_id == user_id and player.disconnected for player in self.lobbies[lobby_id].players):
                    lobby["allow_reconnect"] = True
                    reconnect_lobby = lobby
                    break

        if reconnect_lobby:
            lobbies.remove(reconnect_lobby)
            lobbies.insert(0, reconnect_lobby)

        return lobbies

    def create_lobby(self, request):
        response = self.database_interaction.create_lobby(request)
        if response["success"]:
            lobby_id = response["lobby_id"]
            self.lobbies[lobby_id] = Game(starting_chips=request["buy_in"], player_limit=request['player_limit'])
        return response

    def get_clients_in_lobby(self, lobby_id):
        client_sockets = []
        game = self.lobbies[lobby_id]
        for player in self.get_connected_players(game):
            client_sockets.append(player.client_socket)
        return client_sockets


if __name__ == "__main__":
    server = LobbyServer()
    server.start()
