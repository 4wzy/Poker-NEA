import tkinter as tk
from tkinter import messagebox

class LoginMenu(tk.Tk):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.title("Login Menu")
        self.geometry("800x600")
        self.configure(bg="#181F1C")
        self.user_id = -1

        self.logo_image = tk.PhotoImage(file="gui/Images/logo.png")
        self.logo_image = self.logo_image.subsample(4, 4)
        self.logo_label1 = tk.Label(self, image=self.logo_image, bg="black")
        self.logo_label1.grid(row=0, column=0, sticky="nw", padx=5, pady=5)
        self.logo_label2 = tk.Label(self, image=self.logo_image, bg="black")
        self.logo_label2.grid(row=0, column=2, sticky="ne", padx=5, pady=5)

        self.login_label = tk.Label(self, text="Login", font=("Cambria", 60), bg="#181F1C", fg="white")
        self.login_label.grid(row=0, column=0, columnspan=4, pady=20)

        self.username_label = tk.Label(self, text="Username:", font=("Cambria bold", 12), bg="#181F1C", fg="white")
        self.username_label.grid(row=1, column=0, pady=5, sticky="e")
        self.username_entry = tk.Entry(self, font=("Arial", 12), bg="#DC851F")
        self.username_entry.grid(row=1, column=1, pady=5, padx=10, sticky="w")

        self.password_label = tk.Label(self, text="Password:", font=("Cambria bold", 12), bg="#181F1C", fg="white")
        self.password_label.grid(row=2, column=0, pady=5, sticky="e")
        self.password_entry = tk.Entry(self, font=("Arial", 12), show="*", bg="#DC851F")
        self.password_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        self.login_button = tk.Button(self, text="Login", font=("Cambria", 12), bg="#BF1A1A", fg="white", width=20,
                                      borderwidth=3, command=lambda: self.login_user(
                username=self.username_entry.get(), password=self.password_entry.get()))
        self.login_button.grid(row=4, column=1, padx=10, pady=10, sticky="e")

        self.register_button_label = tk.Label(self, text="Don't have an account yet?", font=("Cambria bold", 12),
                                              bg="#181F1C", fg="white")
        self.register_button_label.grid(row=6, column=0, pady=5, sticky="e")
        self.register_button = tk.Button(self, text="Register", command=self.open_register_menu, font=("Cambria", 12),
                                         bg="#4f1111", fg="white", width=20)
        self.register_button.grid(row=6, column=1, padx=10, pady=5, sticky="e")

        self.help_label = tk.Label(self, text="", font=("Cambria", 12), bg="#191F1C", fg="white")
        self.help_label.grid(row=7, column=0, padx=10, pady=10, columnspan=4)

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

    def login_user(self, username: str, password: str):
        result = self.controller.network_manager.send_message({"type": "login_user", "username": username, "password": password})

        self.help_label.config(text=result["message"])

        if result["success"]:
            self.user_id = result["user_id"]
            print(self.user_id)
            self.controller.open_main_menu(self.user_id)
        else:
            messagebox.showerror("Error", f"{result['message']}")

    def open_register_menu(self):
        self.controller.open_register_menu()
