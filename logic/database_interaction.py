from datetime import datetime
import mysql.connector


class DatabaseInteraction:
    def __init__(self):
        self.config = {
            "user": "root",
            "password": "Password66",
            "host": "127.0.0.1",
            "database": "poker_game"
        }

    def get_username(self, user_id):
        try:
            connection = mysql.connector.connect(**self.config)
            cursor = connection.cursor()

            # Retrieve hashed_password and salt from the database for the given username
            cursor.execute("SELECT username FROM users WHERE user_id = %s", (user_id,))
            username = cursor.fetchone()[0]

            return username
        except Exception as e:
            print(f"Error: {e}")
            return "Invalid"
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def get_all_lobbies(self, status_filter, odds_filter):
        try:
            connection = mysql.connector.connect(**self.config)
            cursor = connection.cursor()

            cursor.execute("SELECT * FROM lobbies WHERE status = %s AND show_odds = %s", (status_filter, odds_filter))
            lobbies = cursor.fetchall()

            # Convert each lobby's datetime objects to string
            lobbies_str = []
            for lobby in lobbies:
                lobby_list = list(lobby)
                for i, item in enumerate(lobby_list):
                    if isinstance(item, datetime):
                        lobby_list[i] = item.strftime('%Y-%m-%d %H:%M:%S')
                lobbies_str.append(lobby_list)

            return lobbies_str
        except Exception as e:
            print(f"Error: {e}")
            return []
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def create_lobby(self, lobby_data):
        try:
            connection = mysql.connector.connect(**self.config)
            cursor = connection.cursor()

            sql = """
            INSERT INTO lobbies (host_user_id, name, status, show_odds)
            VALUES (%s, %s, %s, %s)
            """
            print("inserted")
            cursor.execute(sql, (lobby_data['host_user_id'], lobby_data['name'], 'waiting', lobby_data['show_odds']))

            connection.commit()

        except Exception as e:
            print(f"Error: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
