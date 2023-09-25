import tkinter as tk
from logic.database_interaction import DatabaseInteraction

class MainMenu(tk.Tk):
    def __init__(self, controller, user_id):
        super().__init__()
        self.controller = controller
        self.title("Main Menu")
        self.geometry("800x600")
        self.configure(bg="#181F1C")
        self.database_interaction = DatabaseInteraction()
        self.user_id = user_id
        self.username = self.database_interaction.get_username(self.user_id)

        self.lbl_poker = tk.Label(self, text="AceAware Poker", font=("Cambria", 48), bg="#181F1C", fg="white")
        self.lbl_poker.grid(row=0, rowspan=2, columnspan=8, column=0, padx=20, pady=20, sticky="w")

        self.username_frame = tk.Frame(self, bg="#181F1C")
        self.username_frame.grid(row=0, column=9, columnspan=3, rowspan=3, pady=25, sticky="nswe")

        self.banner_canvas = tk.Canvas(self.username_frame, bg="#181F1C", highlightthickness=0, width=200, height=60)
        self.banner_canvas.place(x=0, y=0)

        self.banner_canvas.create_polygon(
            20, 0,
            200, 0,
            200, 60,
            20, 60,
            0, 30,
            fill="red",
            outline=""
        )

        self.username_label = tk.Label(self.username_frame, text=f"{self.username}", font=("Cambria bold", 20),
                                       bg="red", fg="white")
        self.username_label.place(x=60, y=10)  # x and y are relative to the Frame

        self.btn_play = tk.Button(self, text="Play", font=("Cambria", 24), bg="#d5592a", fg="white", width=30,
                                  borderwidth=3, command=lambda: self.open_lobby_browser(user_id=user_id))
        self.btn_play.grid(row=2, column=0, columnspan=8, padx=10, pady=2, sticky="we")

        self.logo_image = tk.PhotoImage(file="gui/Images/logo.png")
        self.logo_image = self.logo_image.subsample(2, 2)
        self.logo_label = tk.Label(self, image=self.logo_image, bg="black")
        self.logo_label.grid(row=2, column=8, columnspan=6, rowspan=5, sticky="nsew", padx=0, pady=0)

        self.btn_hall_of_fame = tk.Button(self, text="Hall of Fame", command=self.open_settings_menu,
                                          font=("Cambria", 24), bg="#d5592a", fg="white", width=30)
        self.btn_hall_of_fame.grid(row=3, column=0, columnspan=8, padx=10, pady=2, sticky="we")

        self.btn_settings = tk.Button(self, text="Settings", command=self.open_settings_menu, font=("Cambria", 24),
                                         bg="#d5592a", fg="white", width=30)
        self.btn_settings.grid(row=4, column=0, columnspan=8, padx=10, pady=2, sticky="we")

        self.btn_how_to_play = tk.Button(self, text="How to Play", command=self.open_responsible_gaming_menu,
                                                  font=("Cambria", 24), bg="#A61B1B", fg="white", width=30)
        self.btn_how_to_play.grid(row=7, column=0, columnspan=12, padx=30, pady=2, sticky="we")

        self.btn_responsible_gambling = tk.Button(self, text="Responsible Gambling",
                                                  command=self.open_responsible_gaming_menu, font=("Cambria", 24),
                                                  bg="#A61B1B", fg="white", width=20)
        self.btn_responsible_gambling.grid(row=8, column=0, columnspan=12, padx=30, pady=2, sticky="we")

        self.lbl_responsible_gambling = tk.Label(self, text="This game has been created to encourage users to gamble "
                                                            "responsibly. Please check out the Responsible Gambling "
                                                            "section to learn more!", font=("Cambria, 16"),
                                                 bg="#251313", fg="white", wraplength=800, justify=tk.CENTER)
        self.lbl_responsible_gambling.grid(row=9, rowspan=2, column=0, columnspan=12, pady=10)

        self.btn_quit = tk.Button(self, text="Quit", font=("Cambria", 24), bg="#191F1C", fg="white", width=10)
        self.btn_quit.grid(row=11, column=10, columnspan=2, padx=10, pady=10, sticky="se")

        for i in range(12):
            self.grid_rowconfigure(i, weight=1, uniform="a")
            self.grid_columnconfigure(i, weight=1, uniform="a")

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

