import tkinter as tk
from tkinter import font as tkfont
from PIL import Image, ImageTk
from logic.database_interaction import DatabaseInteraction

class LobbyBrowser(tk.Tk):
    def __init__(self, controller, user_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.controller = controller
        self.user_id = user_id
        self.database_interaction = DatabaseInteraction()
        self.username = self.database_interaction.get_username(self.user_id)

        self.title("Lobby Browser - AceAware Poker")
        self.configure(bg="#333333")

        container = tk.Frame(self, bg="#333333", bd=5)
        container.pack(side="top", fill="both", expand=True)
        container.config(highlightbackground="red", highlightthickness=2)

        title_label = tk.Label(container, text="Lobby Browser", font=tkfont.Font(family="Cambria", size=18),
                               fg="#FFD700", bg="#333333", padx=20)
        title_label.grid(row=0, column=0, columnspan=2, sticky="w")

        lobby_listbox = tk.Listbox(container, bg="#555555", fg="#FFFFFF", font=tkfont.Font(family="Cambria", size=12),
                                   selectbackground="#444444")
        lobby_listbox.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        scrollbar = tk.Scrollbar(container, orient="vertical", command=lobby_listbox.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        lobby_listbox.config(yscrollcommand=scrollbar.set)

        button_frame = tk.Frame(container, bg="#333333")
        button_frame.grid(row=2, column=0, columnspan=2, sticky="ew")

        create_lobby_button = tk.Button(button_frame, text="Create Lobby", font=tkfont.Font(family="Cambria", size=16),
                                        fg="#FFFFFF", bg="#444444", bd=0, padx=20, pady=10, borderwidth=1)
        create_lobby_button.pack(side="left", fill="x", expand=True)

        join_lobby_button = tk.Button(button_frame, text="Join Lobby", font=tkfont.Font(family="Cambria", size=16),
                                      fg="#FFFFFF", bg="#444444", bd=0, padx=20, pady=10, borderwidth=1)
        join_lobby_button.pack(side="left", fill="x", expand=True)

        back_button = tk.Button(container, text="Back", font=tkfont.Font(family="Cambria", size=16), fg="#FFFFFF",
                                bg="#444444", bd=0, padx=20, pady=10, command=lambda: self.controller.open_main_menu(
                self.user_id))
        back_button.grid(row=3, column=0, columnspan=2, sticky="ew", pady=10, padx=10)
