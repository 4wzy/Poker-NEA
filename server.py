import socket
import threading
import json
from logic.database_interaction import DatabaseInteraction
from logic.game_logic import Game, Player
from typing import Dict


class LobbyServer:
    def __init__(self, host='localhost', port=12345):
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
            data = client_socket.recv(16384)
            if not data:
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
                    if request["type"] == "get_all_lobbies":
                        print("getting lobbies")
                        response = self.get_all_lobbies(request)
                    elif request["type"] == "create_lobby":
                        print("creating lobby")
                        response = self.create_lobby(request)
                    elif request["type"] == "join_lobby":
                        print("joining lobby")
                        response = self.join_lobby(request, client_socket)
                    elif request["type"] == 'leave_lobby':
                        print(f"PLAYER LEAVING LOBBY: {client_socket}")
                        response = self.leave_lobby(request['user_id'], request['lobby_name'], client_socket)
                    elif request["type"] == "start_game":
                        self.handle_start_game(request["lobby_name"])
                        continue

                    if response is not None:
                        client_socket.sendall((json.dumps(response) + '\n').encode('utf-8'))
                        print(f"(handle client): Response: {response}")
                        print(f"Sent response to {client_socket}")

                except json.JSONDecodeError as e:
                    print(f"JSON Decode Error: {e}")
                    print(f"Data causing the error: {message}")
                    buffer = ""  # Clear the buffer to avoid parsing the same invalid data again

        client_socket.close()

    def process_player_action(self, player_id, action, lobby_name):
        # Process a player action (fold, call, raise) and update the game state

        # (any logic to process the action and update game state)

        self.broadcast_game_state(lobby_name)

    def leave_lobby(self, user_id, lobby_name, client_socket):
        if lobby_name in self.lobbies:
            game = self.lobbies[lobby_name]
            print("Got game")
            game.remove_player(user_id, client_socket)
            print("removed player")

            print(f"New player list: {game.players}")

            self.database_interaction.remove_player_from_lobby(user_id, lobby_name)
            print("Database interaction - removing player from lobby")

            player_left_game_state = self.get_player_left_state(lobby_name)
            self.broadcast_player_left_game_state(lobby_name, client_socket)
            print("broadcasted player left game state")
            return {"success": True, "type": "player_left_game_state", "game_state": player_left_game_state}
        else:
            return {"success": False, "error": "Could not find lobby to remove player from"}

    def broadcast_game_state(self, lobby_name):
        print("BROADCASTING GAME STATE TO EVERYONE")
        if lobby_name in self.lobbies:
            game = self.lobbies[lobby_name]
            game_states = game.send_game_state()
            for player, client_socket in zip(game.players, game.client_sockets):
                user_id = player.user_id
                client_socket.sendall((json.dumps({"type": "update_game_state", "user_id": user_id, "game_state": game_states[user_id]}) + '\n').encode('utf-8'))
                print(f"sent game states {game_states[user_id]} to user {user_id}")
            print("sent game state..")

    def broadcast_initial_game_state(self, lobby_name, current_client):
        print("BROADCASTING INITIAL GAME STATE NOT TO EVERYONE")
        game_state = self.get_initial_state(lobby_name)
        print(f"Initial game state to broadcast: {game_state}")
        for client_socket in self.get_clients_in_lobby(lobby_name):
            if client_socket != current_client:
                client_socket.sendall((json.dumps({"type": "initial_state", "game_state": game_state}) + '\n').encode('utf-8'))
                print(f"sent initial game state data to f{client_socket}")

    def broadcast_player_left_game_state(self, lobby_name, current_client):
        print("BROADCASTING PLAYER LEFT GAME STATE NOT TO EVERYONE")
        game_state = self.get_player_left_state(lobby_name)
        print(f"Initial game state to broadcast: {game_state}")
        for client_socket in self.get_clients_in_lobby(lobby_name):
            if client_socket != current_client:
                client_socket.sendall((json.dumps({"type": "player_left_game_state", "game_state": game_state}) + '\n').encode('utf-8'))
                print(f"sent initial game state data to f{client_socket}")

    def get_game_state(self, lobby_name):
        return self.lobbies[lobby_name].get_game_state()

    def get_player_left_state(self, lobby_name):
        return self.lobbies[lobby_name].get_player_left_state()

    def get_initial_state(self, lobby_name):
        return self.lobbies[lobby_name].get_initial_state()

    def join_lobby(self, request, client_socket):
        print(f"JOINING LOBBY REQUEST: {request}")
        user_id = request["user_id"]
        lobby_name = request["lobby_name"]
        user_name = self.database_interaction.get_username(user_id)

        if lobby_name in self.lobbies:
            game = self.lobbies[lobby_name]
            player = Player(user_name, user_id, chips=100, position=game.available_positions.pop(0))
            game.add_player(player, client_socket)
            initial_state = self.get_initial_state(lobby_name)
            print(f"INITIAL STATE: {initial_state}")
            self.broadcast_initial_game_state(lobby_name, client_socket)
            print(f"(server.py): broadcasted initial game state to everyone apart from {client_socket}")
            data_type = "initial_state"
            if len(game.players) == 6:
                game.start_round()
                data_type = "game_starting"  # Inform the client that the game is starting
                game.is_game_starting = True  # Set a flag to denote that the game is ready to start
                print("(server.py): set game._is_game_starting to True so that the round can start")

            data_to_return = {"success": True, "type": data_type, "game_state": initial_state}
            print(data_to_return)
            return data_to_return
        else:
            error_message = "Lobby not found"

        print(f"could not return data. error: {error_message}")
        return {"success": False, "error": error_message}

    def handle_start_game(self, lobby_name):
        print("running handle_start_game")
        game = self.lobbies[lobby_name]
        if game.is_game_starting:  # Check if the game is ready to start
            self.broadcast_game_state(lobby_name)

    def get_all_lobbies(self, request):
        status_filter = request["status"]
        odds_filter = request["odds"]
        lobbies = self.database_interaction.get_all_lobbies("waiting", odds_filter)
        if "in_progress" in status_filter:
            lobbies += self.database_interaction.get_all_lobbies("in_progress", odds_filter)

        return lobbies

    def create_lobby(self, request):
        response = self.database_interaction.create_lobby(request)
        if response["success"]:
            lobby_name = request["name"]
            self.lobbies[lobby_name] = Game()
        return response

    def get_clients_in_lobby(self, lobby_name):
        return self.lobbies[lobby_name].client_sockets


if __name__ == "__main__":
    server = LobbyServer()
    server.start()
