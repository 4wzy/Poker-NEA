from datetime import datetime
import mysql.connector
from contextlib import contextmanager


class DatabaseInteraction:
    def __init__(self):
        self.config = {
            "user": "root",
            "password": "Password66",
            "host": "127.0.0.1",
            "database": "poker_game"
        }

    @contextmanager
    def db_cursor(self):
        """Context manager to handle database connection and cursor."""
        connection = mysql.connector.connect(**self.config)
        cursor = connection.cursor()
        try:
            yield cursor
            connection.commit()
        except mysql.connector.Error as e:
            print(f"Database error: {e}")
            connection.rollback()
            raise
        finally:
            cursor.close()
            connection.close()

    def get_username(self, user_id):
        with self.db_cursor() as cursor:
            # Retrieve hashed_password and salt from the database for the given username
            cursor.execute("SELECT username FROM users WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()
            return result[0] if result else "Invalid"

    def get_all_lobbies(self, status_filter, odds_filter):
        try:
            with self.db_cursor() as cursor:

                cursor.execute("""
                    SELECT l.lobby_id, l.name, l.status, COUNT(pl.user_id), l.created_at, l.show_odds, l.player_limit
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
                    'created_at': lobby[4].strftime('%Y-%m-%d %H:%M:%S'),
                    'show_odds': lobby[5],
                    'player_limit': lobby[6]
                } for lobby in lobbies]
        except Exception as e:
            print(f"Error: {e}")
            return []

    def create_lobby(self, lobby_data):
        response = {"success": True, "error": None, "lobby_id": None}
        with self.db_cursor() as cursor:
            # Check if a lobby with the same name and the status "waiting" or "in_progress" already exists
            # use the following later on instead:
            # SELECT COUNT(*) FROM lobbies WHERE name = %s AND (status = 'waiting' OR status = 'in_progress')
            check_sql = """
            SELECT COUNT(*) FROM lobbies WHERE name = %s AND (status = 'waiting')
            """
            cursor.execute(check_sql, (lobby_data['name'],))
            existing_lobby_count = cursor.fetchone()[0]

            if existing_lobby_count > 0:
                response["success"] = False
                response["error"] = "A lobby with this name already exists and is currently active"
                return response

            # If no such lobby exists, proceed with the insert

            if lobby_data["player_limit"] < 3 or lobby_data["player_limit"] > 6:
                response["success"] = False
                response["error"] = "Player limit can only be 3 to 6"
                return response

            sql = """
            INSERT INTO lobbies (host_user_id, name, status, show_odds, player_limit)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (lobby_data['host_user_id'], lobby_data['name'], 'waiting', lobby_data['show_odds'], lobby_data['player_limit']))

            # Get the last inserted ID
            lobby_id = cursor.lastrowid
            response["lobby_id"] = lobby_id

        return response

    def set_lobby_status(self, lobby_id, lobby_status):
        response = {"success": True, "error": None}
        with self.db_cursor() as cursor:
            try:
                sql = """
                UPDATE lobbies 
                SET status = %s 
                WHERE lobby_id = %s
                """
                cursor.execute(sql, (lobby_status, lobby_id))
            except Exception as e:
                response["success"] = False
                response["error"] = f"Error: {e}"

        print(f"set lobby status to {lobby_status}")
        return response

    def join_lobby(self, user_id, lobby_id):
        print("(database interaction): joining lobby")
        response = {"success": True, "error": None}

        try:
            with self.db_cursor() as cursor:
                # Update the lobby to include the new player
                sql = """
                INSERT INTO player_lobbies (user_id, lobby_id) 
                VALUES (%s, (SELECT lobby_id FROM lobbies WHERE lobby_id = %s AND status = 'waiting'))
                """
                cursor.execute(sql, (user_id, lobby_id))

        except Exception as e:
            response["success"] = False
            response["error"] = f"Error: {e}"

        return response["success"], response["error"]

    def remove_player_from_lobby(self, user_id, lobby_id):
        try:
            connection = mysql.connector.connect(**self.config)
            cursor = connection.cursor()

            query = "DELETE FROM player_lobbies WHERE user_id = %s AND lobby_id = %s"
            cursor.execute(query, (user_id, lobby_id))
            connection.commit()

        except Exception as e:
            print(f"Error removing player from lobby database: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
