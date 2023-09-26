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

            # Modify the SQL query to also get the count of players in each lobby
            cursor.execute("""
                SELECT l.lobby_id, l.name, l.status, COUNT(pl.user_id), l.created_at, l.show_odds
                FROM lobbies l
                LEFT JOIN player_lobbies pl ON l.lobby_id = pl.lobby_id
                WHERE l.status = %s AND l.show_odds = %s
                GROUP BY l.lobby_id
            """, (status_filter, odds_filter))

            lobbies = cursor.fetchall()

            return [{
                'lobby_id': lobby[0],
                'name': lobby[1],
                'status': lobby[2],
                'player_count': lobby[3],
                'created_at': lobby[4].strftime('%Y-%m-%d %H:%M:%S'),  # Convert datetime to string
                'show_odds': lobby[5]
            } for lobby in lobbies]

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
