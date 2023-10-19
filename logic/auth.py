from logic.database_base import DatabaseBase
import hashlib
import secrets
import mysql.connector
import re


class UserAuth(DatabaseBase):
    def login_user(self, username: str, password: str):
        with self.db_cursor() as cursor:
            # Retrieve hashed_password and salt from the database for the given username
            cursor.execute("SELECT hashed_password, salt FROM users WHERE username = %s", (username,))
            row = cursor.fetchone()

            if row is None:
                print("Invalid username")
                return {"success": False, "message": "Invalid username"}

            stored_hashed_password, salt = row
            # Hash the provided password with the retrieved salt
            hashed_password = password + salt
            for i in range(10):
                hashed_password = hashlib.sha256(hashed_password.encode()).hexdigest()

            # Compare the computed hash with the stored hash
            if hashed_password == stored_hashed_password:
                print("User authenticated successfully!")
                cursor.execute("SELECT user_id FROM users WHERE username = %s", (username,))
                user_id = cursor.fetchone()[0]
                return {"success": True, "user_id": user_id, "message": "User authenticated successfully!"}
            else:
                print("Invalid password")
                return {"success": False, "message": "Invalid password"}

    def register_user(self, username: str, password: str, email: str):
        if not self.validate_password(password):
            return {"success": False, "message": "Password does not meet the requirements"}
        if not self.validate_username(username):
            return {"success": False, "message": "Username does not meet the requirements"}
        if not self.validate_email(email):
            return {"success": False, "message": "Invalid email provided"}

        hashed_password, salt = self.hash_password(password)

        with self.db_cursor() as cursor:
            try:
                cursor.execute(
                    "INSERT INTO users (username, hashed_password, salt, email) VALUES (%s, %s, %s, %s)",
                    (username, hashed_password, salt, email)
                )

                user_id = cursor.lastrowid  # Get the user_id of the user that just registered
                cursor.execute(
                    "INSERT INTO user_chips (user_id, chips_balance) VALUES (%s, DEFAULT)",
                    (user_id,)
                )
                return {"success": True, "message": "User registered successfully!"}
            except mysql.connector.IntegrityError:
                return {"success": False, "message": "Username or Email already exists"}

    def validate_password(self, password: str) -> bool:
        # Use regular expressions to validate password, including checking if one or more types of characters are present
        if len(password) < 12:
            return False
        if not re.search("[A-Z]", password):
            return False
        if not re.search("[a-z]", password):
            return False
        if not re.search("[!?,.()@<>#$%&*^\":{}|]", password):
            return False
        return True

    def validate_email(self, email: str) -> bool:
        if "@" not in email:
            return False
        return True

    def validate_username(self, username: str) -> bool:
        if len(username) < 3:
            return False
        return True

    def hash_password(self, password: str) -> tuple:
        salt = secrets.token_hex(16)
        salted_password = password + salt

        for i in range(10):
            salted_password = hashlib.sha256(salted_password.encode()).hexdigest()
        return salted_password, salt
