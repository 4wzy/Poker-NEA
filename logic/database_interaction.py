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

    def get_all_lobbies(self):
        pass
