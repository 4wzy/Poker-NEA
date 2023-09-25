# Find a way to separate these classes into modules
import re
import tkinter as tk
import hashlib
import secrets
import mysql.connector

class LoginMenu(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Login Menu")
        self.geometry("800x600")
        self.configure(bg="#181F1C")
        self.user_id = -1

        # Create and configure widgets
        # self.label = tk.Label(self, text="Login Menu")
        # self.label.grid(row=0, column=0, padx=10, pady=10)

        self.logo_image = tk.PhotoImage(file="gui/Images/logo.png")
        self.logo_image = self.logo_image.subsample(4, 4)
        self.logo_label1 = tk.Label(self, image=self.logo_image, bg="black")
        self.logo_label1.grid(row=0, column=0, sticky="nw", padx=5, pady=5)
        self.logo_label2 = tk.Label(self, image=self.logo_image, bg="black")
        self.logo_label2.grid(row=0, column=2, sticky="ne", padx=5, pady=5)

        self.login_label = tk.Label(self, text="Login", font=("Arial", 60), bg="#181F1C", fg="white")
        self.login_label.grid(row=0, column=0, columnspan=4, pady=20)

        self.username_label = tk.Label(self, text="Username:", font=("Arial bold", 12), bg="#181F1C", fg="white")
        self.username_label.grid(row=1, column=0, pady=5, sticky="e")
        self.username_entry = tk.Entry(self, font=("Arial", 12), bg="#DC851F")
        self.username_entry.grid(row=1, column=1, pady=5, padx=10, sticky="w")

        self.password_label = tk.Label(self, text="Password:", font=("Arial bold", 12), bg="#181F1C", fg="white")
        self.password_label.grid(row=2, column=0, pady=5, sticky="e")
        self.password_entry = tk.Entry(self, font=("Arial", 12), show="*", bg="#DC851F")
        self.password_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        self.login_button = tk.Button(self, text="Login", font=("Arial", 12), bg="#BF1A1A", fg="white", width=20,
                                      borderwidth=3, command=lambda: self.login_user(
                username=self.username_entry.get(), password=self.password_entry.get()))
        self.login_button.grid(row=4, column=1, padx=10, pady=10, sticky="e")

        self.register_button_label = tk.Label(self, text="Don't have an account yet?", font=("Arial bold", 12),
                                           bg="#181F1C", fg="white")
        self.register_button_label.grid(row=6, column=0, pady=5, sticky="e")
        self.register_button = tk.Button(self, text="Register", command=self.open_register_menu, font=("Arial", 12),
                                         bg="#4f1111", fg="white", width=20)
        self.register_button.grid(row=6, column=1, padx=10, pady=5, sticky="e")

        self.help_label = tk.Label(self, text="", font=("Arial", 12), bg="#191F1C", fg="white")
        self.help_label.grid(row=7, column=0, padx=10, pady=10)

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_rowconfigure(4, weight=1)
        self.grid_rowconfigure(5, weight=1)
        self.grid_rowconfigure(6, weight=1)
        self.grid_rowconfigure(7, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

    def open_register_menu(self):
        self.destroy()  # Close the current window
        register_menu = RegisterMenu()
        register_menu.mainloop()

    def login_user(self, username: str, password: str):
        config = {
            "user": "root",
            "password": "Password66",
            "host": "127.0.0.1",
            "database": "poker_game"
        }

        try:
            connection = mysql.connector.connect(**config)
            cursor = connection.cursor()

            # Retrieve hashed_password and salt from the database for the given username
            cursor.execute("SELECT hashed_password, salt FROM users WHERE username = %s", (username,))
            row = cursor.fetchone()

            if row is None:
                print("Invalid username")
                self.help_label.config(text="Invalid username")
                return False

            stored_hashed_password, salt = row

            # Hash the provided password with the retrieved salt
            hashed_password = password + salt
            for i in range(10):
                hashed_password = hashlib.sha256(hashed_password.encode()).hexdigest()

            # Compare the computed hash with the stored hash
            if hashed_password == stored_hashed_password:
                print("User authenticated successfully!")
                self.help_label.config(text="User authenticated successfully!")
                cursor.execute("SELECT user_id FROM users WHERE username = %s", (username,))
                self.user_id = cursor.fetchone()[0]
                print(self.user_id)
                return True
            else:
                print("Invalid password")
                self.help_label.config(text="Invalid password")
                return False
        except Exception as e:
            print(f"Error: {e}")
            return False
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

class RegisterMenu(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Login Menu")
        self.geometry("800x600")
        self.configure(bg="#181F1C")

        # Create and configure widgets
        # self.label = tk.Label(self, text="Login Menu")
        # self.label.grid(row=0, column=0, padx=10, pady=10)

        self.logo_image = tk.PhotoImage(file="gui/Images/logo.png")
        self.logo_image = self.logo_image.subsample(4, 4)
        self.logo_label1 = tk.Label(self, image=self.logo_image, bg="black")
        self.logo_label1.grid(row=0, column=0, sticky="nw", padx=5, pady=5)
        self.logo_label2 = tk.Label(self, image=self.logo_image, bg="black")
        self.logo_label2.grid(row=0, column=2, sticky="ne", padx=5, pady=5)

        self.register_label = tk.Label(self, text="Register", font=("Arial", 60), bg="#181F1C", fg="white")
        self.register_label.grid(row=0, column=0, columnspan=4, pady=20)

        self.username_label = tk.Label(self, text="Username:", font=("Arial bold", 12), bg="#181F1C", fg="white")
        self.username_label.grid(row=1, column=0, pady=10, sticky="e")
        self.username_entry = tk.Entry(self, font=("Arial", 12), bg="#DC851F")
        self.username_entry.grid(row=1, column=1, pady=10, padx=10, sticky="w")

        self.email_label = tk.Label(self, text="Email:", font=("Arial bold", 12), bg="#181F1C", fg="white")
        self.email_label.grid(row=2, column=0, pady=10, sticky="e")
        self.email_entry = tk.Entry(self, font=("Arial", 12), bg="#DC851F")
        self.email_entry.grid(row=2, column=1, pady=10, padx=10, sticky="w")

        self.password_label = tk.Label(self, text="Password:", font=("Arial bold", 12), bg="#181F1C", fg="white")
        self.password_label.grid(row=3, column=0, pady=10, sticky="e")
        self.password_entry = tk.Entry(self, font=("Arial", 12), show="*", bg="#DC851F")
        self.password_entry.grid(row=3, column=1, padx=10, pady=10, sticky="w")

        self.register_button = tk.Button(self, text="Register", command=lambda: self.register_user(
            username=self.username_entry.get(), password=self.password_entry.get(), email=self.email_entry.get()),
                                         font=("Arial", 12), bg="#BF1A1A", fg="white", width=20)
        self.register_button.grid(row=4, column=1, padx=10, pady=10, sticky="e")

        self.login_button_label = tk.Label(self, text="Already have an account?", font=("Arial bold", 12),
                                              bg="#181F1C", fg="white")
        self.login_button_label.grid(row=6, column=0, pady=5, sticky="e")
        self.login_button = tk.Button(self, text="Login", command=self.open_login_menu, font=("Arial", 12),
                                      bg="#4f1111", fg="white", width=20)
        self.login_button.grid(row=6, column=1, padx=10, pady=10, sticky="e")

        self.help_label = tk.Label(self, text="", font=("Arial", 12), bg="#191F1C", fg="white")
        self.help_label.grid(row=7, column=0, padx=10, pady=10)

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_rowconfigure(4, weight=1)
        self.grid_rowconfigure(5, weight=1)
        self.grid_rowconfigure(6, weight=1)
        self.grid_rowconfigure(7, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

    def open_login_menu(self):
        self.destroy()  # Close the current window
        login_menu = LoginMenu()
        login_menu.mainloop()

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

    def register_user(self, username: str, password: str, email: str):
        if not self.validate_password(password):
            self.help_label.config(text="Password does not meet the requirements")
            print("Password does not meet the requirements")
            return
        if not self.validate_username(username):
            print("Username does not meet the requirements")
            self.help_label.config(text="Username does not meet the requirements")
            return
        if not self.validate_email(email):
            print("Invalid email provided")
            self.help_label.config(text="Invalid email provided")
            return

        hashed_password, salt = self.hash_password(password)

        config = {
            "user": "root",
            "password": "Password66",
            "host": "127.0.0.1",
            "database": "poker_game"
        }

        try:
            connection = mysql.connector.connect(**config)
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO users (username, hashed_password, salt, email) VALUES (%s, %s, %s, %s)",
                (username, hashed_password, salt, email)
            )
            connection.commit()
            print("User registered successfully!")
            self.help_label.config(text="User registered successfully!")
            return
        except mysql.connector.IntegrityError:
            print("Username or Email already exists")
            self.help_label.config(text="Username or Email already exists")
            return
        except Exception as e:
            print(f"Error: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()