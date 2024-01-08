import socket
import json
import time


class NetworkManager:
    def __init__(self):
        self.client_socket = None
        self.__connect_to_server()
        self.buffer = ""

    # The method for a user to initially connect to a server
    def __connect_to_server(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect(("127.0.0.1", 12345))
            print("Connected to server")
        except ConnectionRefusedError:
            print("Couldn't connect to the server")

    # Send a message to the server and await a response
    def send_message(self, message):
        try:
            print(f"1. {message}")
            self.client_socket.sendall((json.dumps(message) + '\n').encode('utf-8'))
            response = self.__receive_message()
            print(f"2. {response}")
            # THIS MAY CAUSE ISSUES. IF THERE ARE SERVER ISSUES, CHANGE TO "if response:"
            if response is not None:
                return response
        except BrokenPipeError:
            print("Connection to the server is broken")
            # Possibly attempt to reconnect to the server
        except Exception as e:
            print(f"Other exception: {e}")
            print(f"Data causing the error: {self.buffer}")

    # Method to send a signal to the server without expecting a response
    def send_signal(self, signal):
        print(f"Signal 1. {signal}")
        try:
            self.client_socket.sendall((json.dumps(signal) + '\n').encode('utf-8'))
        except BrokenPipeError:
            print("Connection to the server is broken")
        except Exception as e:
            print(f"Other exception: {e}")
            print(f"Data causing the error: {self.buffer}")

    # Receive a message from the server
    def __receive_message(self):
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
                # Handle non-blocking socket mode.
                pass
            except Exception as e:
                print(f"Unexpected error: {e}")
                break

    # Send the start_game message to the server
    def send_start_game_message(self, lobby_id):
        start_game_message = {"type": "start_game", "lobby_id": lobby_id}
        start_game_response = self.send_message(start_game_message)
        print(f"(network_manager): start_game_response: {start_game_response}")
        return start_game_response

    # The code for sending a request to join a lobby and awaiting a response
    def join_lobby(self, user_id, lobby_id):
        print("starting to join lobby")
        message = {"type": "join_lobby", "user_id": user_id, "lobby_id": lobby_id}
        response_data = self.send_message(message)
        print(f"(network_manager): {response_data}")
        return response_data

    def __close_connection(self):
        self.client_socket.close()

    # Reset the connection after leaving a game if necessary
    def reset_connection(self):
        print("Resetting connection...")
        self.__close_connection()
        time.sleep(0.5)  # Wait to ensure the socket is properly closed
        self.__connect_to_server()
