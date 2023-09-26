import socket
import threading
from logic.database_interaction import DatabaseInteraction
import json
#a
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("localhost", 12345))
server_socket.listen(5)
database_interaction = DatabaseInteraction()

def handle_client(client_socket):
    while True:
        data = client_socket.recv(1024)
        if not data:
            break

        request = json.loads(data.decode('utf-8'))

        if request["type"] == 'get_all_lobbies':
            status_filter = request["status"]
            odds_filter = request["odds"]
            lobbies = database_interaction.get_all_lobbies("waiting", odds_filter)
            if "in_progress" in status_filter:
                lobbies += database_interaction.get_all_lobbies("in_progress", odds_filter)

            client_socket.sendall(json.dumps(lobbies).encode('utf-8'))
        elif request["type"] == 'create_lobby':
            database_interaction.create_lobby(request)

    client_socket.close()


while True:
    client_socket, addr = server_socket.accept()
    client_handler = threading.Thread(target=handle_client, args=(client_socket,))
    client_handler.start()
