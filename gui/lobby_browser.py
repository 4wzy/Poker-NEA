import tkinter as tk
from logic.database_interaction import DatabaseInteraction


class LobbyBrowser(tk.Tk):
    def __init__(self, controller, user_id):
        super().__init__()
        self.controller = controller
        self.title("Lobby Browser")
        self.geometry("800x600")
        self.configure(bg="#181F1C")
        self.database_interaction = DatabaseInteraction()
        self.user_id = user_id
        self.username = self.database_interaction.get_username(self.user_id)

        self.login_label = tk.Label(self, text="AceAware Poker", font=("Cambria", 72), bg="#181F1C", fg="white")
        self.login_label.grid(row=0, column=0, columnspan=2, pady=20, sticky="w")

        self.username_label = tk.Label(self, text=f"{self.username}", font=("Cambria bold", 12),
                                       bg="#181F1C",
                                       fg="white")
        self.username_label.grid(row=0, column=2, pady=5, sticky="e")

        self.logo_image = tk.PhotoImage(file="gui/Images/logo.png")
        self.logo_image = self.logo_image.subsample(3, 3)
        self.logo_label = tk.Label(self, image=self.logo_image, bg="black")
        self.logo_label.grid(row=1, column=2, sticky="e", padx=5, pady=5)

        self.btn_play = tk.Button(self, text="Play", font=("Cambria", 20), bg="#BF1A1A", fg="white", width=40,
                                      borderwidth=3, command=lambda: self.open_lobby_browser(user_id=user_id))
        self.btn_play.grid(row=2, column=0, padx=10, pady=10, sticky="w")

        self.btn_settings = tk.Button(self, text="Settings", command=self.open_settings_menu, font=("Cambria", 12),
                                         bg="#4f1111", fg="white", width=20)
        self.btn_settings.grid(row=3, column=0, padx=10, pady=5, sticky="w")

        self.btn_responsible_gambling = tk.Button(self, text="Settings", command=self.open_responsible_gaming_menu,
                                                font=("Cambria", 12),
                                         bg="#4f1111", fg="white", width=20)
        self.btn_responsible_gambling.grid(row=3, column=0, padx=10, pady=5, sticky="w")

        self.lbl_help = tk.Label(self, text="", font=("Cambria", 12), bg="#191F1C", fg="white")
        self.lbl_help.grid(row=7, column=0, padx=10, pady=10, columnspan=4)

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

    # def login_user(self, username: str, password: str):
    #     result = self.user_auth.login_user(username, password)
    #
    #     self.lbl_help.config(text=result["message"])
    #
    #     if result["success"]:
    #         self.user_id = result["user_id"]
    #         print(self.user_id)

    def open_profile(self):
        self.controller.open_register_menu()

    def open_settings_menu(self):
        self.controller.open_register_menu()

    def open_lobby_browser(self, user_id):
        self.controller.open_lobby_browser(user_id)

    def open_hall_of_fame(self):
        self.controller.open_register_menu()

    def open_responsible_gaming_menu(self):
        self.controller.open_register_menu()
