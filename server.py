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
        self.server_socket.listen(5)

        self.database_interaction = DatabaseInteraction()
        self.lobbies: Dict[str, Game] = {}  # I have explicitly used type hinting for easier development

    def start(self):
        print("Server started...")
        while True:
            client_socket, addr = self.server_socket.accept()
            client_handler = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_handler.start()

    def handle_client(self, client_socket):
        while True:
            data = client_socket.recv(4096)
            if not data:
                break

            request = json.loads(data.decode('utf-8'))
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
            elif request['type'] == 'leave_lobby':
                print("leaving lobby")
                self.leave_lobby(request['user_id'], request['lobby_name'])

            print(f"Response: {response}")
            client_socket.sendall(json.dumps(response).encode('utf-8'))

        client_socket.close()

    def leave_lobby(self, user_id, lobby_name):
        if lobby_name in self.lobbies:
            game = self.lobbies[lobby_name]
            game.remove_player(user_id)

            self.database_interaction.remove_player_from_lobby(user_id, lobby_name)

            self.broadcast_game_state(lobby_name)

    def broadcast_game_state(self, lobby_name):
        print("BROADCASTING GAME STATE")
        game_state = self.get_game_state(lobby_name)
        for client_socket in self.get_clients_in_lobby(lobby_name):
            client_socket.sendall(json.dumps({"type": "update_game_state", "game_state": game_state}).encode('utf-8'))

    def broadcast_initial_game_state(self, lobby_name):
        print("BROADCASTING INITIAL GAME STATE")
        game_state = self.get_initial_state(lobby_name)
        print(f"initial game state: {game_state}")
        for client_socket in self.get_clients_in_lobby(lobby_name):
            client_socket.sendall(json.dumps({"type": "initial_state", "game_state": game_state}).encode('utf-8'))
            print(f"sent initial game state data to f{client_socket}")

    def get_game_state(self, lobby_name):
        return self.lobbies[lobby_name].get_game_state()

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
            self.broadcast_initial_game_state(lobby_name)
            return {"success": True, "type": "initial_state", "game_state": initial_state}
        else:
            error_message = "Lobby not found"

        return {"success": False, "error": error_message}

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
