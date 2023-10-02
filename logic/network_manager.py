import socket
import json

class NetworkManager:
    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect_to_server()

    def connect_to_server(self):
        try:
            self.client_socket.connect(("localhost", 12345))
            print("Connected to server")
        except ConnectionRefusedError:
            print("Couldn't connect to the server")

    def send_message(self, message):
        try:
            print(f"1. {message}")
            self.client_socket.sendall(json.dumps(message).encode('utf-8'))
            response = False
            try:
                response = self.client_socket.recv(16384)
            except BlockingIOError:
                print(f"(network_manager): Player has left the game - stopped receiving game state updates (or "
                      f"BlockingIOError has occured)")
                pass
            if response:
                print(f"2. {response}")
                return json.loads(response.decode('utf-8'))
        except BrokenPipeError:
            print("Connection to the server is broken")
            # Possibly attempt to reconnect to the server
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error: {e}")
            print(f"Data causing the error: {response}")
        except Exception as e:
            print(f"Other exception: {e}")
            print(f"Data causing the error: {response}")

    def join_lobby(self, user_id, lobby_name):
        print("starting to join lobby")
        message = {"type": "join_lobby", "user_id": user_id, "lobby_name": lobby_name}
        response_data = self.send_message(message)
        print(f"(network_manager): {response_data}")
        if response_data['type'] == "game_starting":
            start_game_message = {"type": "start_game", "lobby_name": lobby_name}
            start_game_response = self.send_message(start_game_message)
            print(f"(network_manager): start_game_response: {start_game_response}")
        print(f"2. {response_data}")
        return response_data

    def close_connection(self):
        self.client_socket.close()
