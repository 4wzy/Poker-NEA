import socket
import json
import time


class NetworkManager:
    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect_to_server()
        self.buffer = ""

    def connect_to_server(self):
        try:
            self.client_socket.connect(("localhost", 12345))
            print("Connected to server")
        except ConnectionRefusedError:
            print("Couldn't connect to the server")

    def send_message(self, message):
        try:
            print(f"1. {message}")
            self.client_socket.sendall((json.dumps(message) + '\n').encode('utf-8'))
            response = self.receive_message()
            if response:
                return response
        except BrokenPipeError:
            print("Connection to the server is broken")
            # Possibly attempt to reconnect to the server
        except Exception as e:
            print(f"Other exception: {e}")
            print(f"Data causing the error: {self.buffer}")

    def receive_message(self):
        while True:
            try:
                data = self.client_socket.recv(16384).decode('utf-8')
                if not data:
                    print("Connection closed by server")
                    break

                self.buffer += data
                if '\n' in self.buffer:
                    message, self.buffer = self.buffer.split('\n', 1)
                    return json.loads(message)
            except json.JSONDecodeError as e:
                print(f"JSON Decode Error: {e}")
                print(f"Data causing the error: {self.buffer}")
                self.buffer = ""
            except BlockingIOError:
                # Handle non-blocking socket mode. If you are not using non-blocking sockets,
                # you can remove this exception handling block.
                pass
            except Exception as e:
                print(f"Unexpected error: {e}")
                break

    def send_start_game_message(self, lobby_name):
        start_game_message = {"type": "start_game", "lobby_name": lobby_name}
        start_game_response = self.send_message(start_game_message)
        print(f"(network_manager): start_game_response: {start_game_response}")
        return start_game_response

    def join_lobby(self, user_id, lobby_name):
        print("starting to join lobby")
        message = {"type": "join_lobby", "user_id": user_id, "lobby_name": lobby_name}
        response_data = self.send_message(message)
        print(f"(network_manager): {response_data}")
        return response_data

    def close_connection(self):
        self.client_socket.close()
