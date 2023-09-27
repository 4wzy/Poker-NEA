import socket
import threading
import json
from logic.database_interaction import DatabaseInteraction
from logic.game_logic import Game, Player


class LobbyServer:
    def __init__(self, host='localhost', port=12345):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.server_socket.listen(5)

        self.database_interaction = DatabaseInteraction()
        self.lobbies = {}

    def start(self):
        print("Server started...")
        while True:
            client_socket, addr = self.server_socket.accept()
            client_handler = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_handler.start()

    def handle_client(self, client_socket):
        while True:
            data = client_socket.recv(1024)
            if not data:
                break

            request = json.loads(data.decode('utf-8'))

            if request["type"] == "get_all_lobbies":
                response = self.get_all_lobbies(request)
            elif request["type"] == "create_lobby":
                response = self.create_lobby(request)
            elif request["type"] == "join lobby":
                response = self.join_lobby(request)

            client_socket.sendall(json.dumps(response).encode('utf-8'))

        client_socket.close()

    def join_lobby(self, request):
        user_id = request["user_id"]
        lobby_name = request["lobby_name"]
        user_name = self.database_interaction.get_username(user_id)

        # Assuming self.lobbies is a dict with lobby_name as key and Lobby object as value
        if lobby_name in self.lobbies:
            game = self.lobbies[lobby_name]
            player = Player(user_name, user_id, chips=100)
            game.add_player(player)
            success = True
            error_message = ""
        else:
            success = False
            error_message = "Lobby not found"

        return {"success": success, "error": error_message}

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
            self.lobbies[lobby_name] = Game([])
        return response


if __name__ == "__main__":
    server = LobbyServer()
    server.start()
