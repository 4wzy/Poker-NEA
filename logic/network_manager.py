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
            # Handle the error, e.g., by showing an error message in the GUI
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
            # Handle the error, e.g., by attempting to reconnect to the server
            print("Connection to the server is broken")

    def join_lobby(self, user_id, lobby_name):
        print("starting to join lobby")
        message = {"type": "join_lobby", "user_id": user_id, "lobby_name": lobby_name}
        response_data = self.send_message(message)
        print(f"2. {response_data}")
        return response_data

    def close_connection(self):
        self.client_socket.close()
