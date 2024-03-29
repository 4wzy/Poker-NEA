from helpers.database_base import DatabaseBase
import hashlib
import secrets
import mysql.connector
import re


class UserAuth(DatabaseBase):
    def __init__(self):
        super().__init__()
        self.password_hash_iterations = 2048

    def login_user(self, username: str, password: str):
        with self._db_cursor() as cursor:
            # Retrieve hashed_password and salt from the database for the given username
            cursor.execute("SELECT hashed_password, salt FROM users WHERE username = %s", (username,))
            row = cursor.fetchone()

            if row is None:
                return {"success": False, "message": "Invalid username or password"}
                # This message is used to not let a potential hacker know if they are dealing with a valid username
                # it could prevent third party applications hacking into accounts

            stored_hashed_password, salt = row
            # Hash the provided password with the salt
            hashed_password = password + salt
            for i in range(self.password_hash_iterations):
                hashed_password = hashlib.sha256(hashed_password.encode()).hexdigest()

            # Compare the computed hash with the stored hash
            if hashed_password == stored_hashed_password:
                print("User authenticated successfully!")
                cursor.execute("SELECT user_id FROM users WHERE username = %s", (username,))
                user_id = cursor.fetchone()[0]
                return {"success": True, "user_id": user_id, "message": "User authenticated successfully!"}
            else:
                print("Invalid password")
                return {"success": False, "message": "Invalid username or password"}

    def register_user(self, username: str, password: str, email: str):
        if not self.__validate_username(username):
            return {"success": False, "message": "Username does not meet the requirements"}
        if not self.__validate_password(password):
            return {"success": False, "message": "Password does not meet the requirements"}
        if not self.__validate_email(email):
            return {"success": False, "message": "Invalid email provided"}

        hashed_password, salt = self.__hash_password(password)

        with self._db_cursor() as cursor:
            try:
                cursor.execute(
                    "INSERT INTO users (username, hashed_password, salt, email) VALUES (%s, %s, %s, %s)",
                    (username, hashed_password, salt, email)
                )

                user_id = cursor.lastrowid  # Get the user_id of the user that just registered

                # Insert default values into corresponding tables

                cursor.execute(
                    "INSERT INTO user_statistics (user_id) VALUES (%s)",
                    (user_id,)
                )

                cursor.execute(
                    "INSERT INTO user_game_limits (user_id, daily_game_limit, last_logged_in, games_played_today) VALUES (%s, 10, NOW(), 0)",
                    (user_id,)
                )

                return {"success": True, "message": "User registered successfully!"}
            except mysql.connector.IntegrityError:
                return {"success": False, "message": "Username or Email already exists"}

    def __validate_password(self, password: str) -> bool:
        # Use regular expressions to validate password, including checking if one or more types of characters are present
        if len(password) < 12 or len(password) > 255:
            return False
        if not re.search("[A-Z]", password):
            return False
        if not re.search("[a-z]", password):
            return False
        if not re.search("[0-9]", password):
            return False
        if not re.search("[!?,.()@<>#$%&*^\":{}|]", password):
            return False
        return True

    def __validate_email(self, email: str) -> bool:
        if "@" not in email:
            return False
        return True

    def __validate_username(self, username: str) -> bool:
        if len(username) < 3 or len(username) > 20:
            return False
        return True

    def __hash_password(self, password: str) -> tuple:
        salt = secrets.token_hex(16)
        salted_password = password + salt

        for i in range(self.password_hash_iterations):
            salted_password = hashlib.sha256(salted_password.encode()).hexdigest()
        return salted_password, salt
