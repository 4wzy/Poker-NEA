import mysql.connector
from contextlib import contextmanager


class DatabaseBase:
    def __init__(self):
        self.config = {
            "user": "root",
            "password": "Password66",
            "host": "127.0.0.1",
            "database": "poker_game"
        }

    @contextmanager
    def db_cursor(self):
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
