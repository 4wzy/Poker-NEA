import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageDraw, ImageTk
from logic.database_interaction import DatabaseInteraction


class GameGUI(tk.Tk):
    def __init__(self, controller, user_id, lobby_name):
        super().__init__()
        self.geometry("1280x720")
        self.configure(bg="#333333")
        self.controller = controller
        self.database_interaction = DatabaseInteraction()
        self.user_id = user_id
        self.username = self.database_interaction.get_username(self.user_id)
        self.lobby_name = lobby_name
        self.chat_messages = []

        self.title("Poker Game")

        main_pane = tk.PanedWindow(self, orient="horizontal", bg="#333333", bd=0)
        main_pane.pack(fill="both", expand=1)

        self.sidebar = tk.Frame(main_pane, bg="#333333", width=int(self.winfo_screenwidth() * 0.2))
        main_pane.add(self.sidebar)

        logo_frame = tk.Frame(self.sidebar, bg="#444444")
        logo_frame.pack(pady=5, fill="x")

        self.logo = Image.open("Images/logo.png") # update to gui/Images when running from main.py
        self.logo = self.logo.resize((50, 50))
        self.logo = ImageTk.PhotoImage(self.logo)

        logo_image_label = tk.Label(logo_frame, image=self.logo, bg="#444444")
        logo_image_label.pack(side='left', padx=5)

        logo_text_label = tk.Label(logo_frame, text="AceAware Poker", bg="#444444", fg="#FFFFFF",
                                   font=("Cambria", 14, "bold"))
        logo_text_label.pack(side='left', padx=5)



        # Toggle Buttons
        toggle_frame = tk.Frame(self.sidebar, bg="#333333")
        toggle_frame.pack(pady=10)

        chat_button = tk.Button(toggle_frame, text="Chat", command=self.show_chat, bg="#555555", fg="#FFFFFF", font=("Cambria", 12), relief="flat", padx=10, pady=5)
        chat_button.pack(side="left", padx=5)

        odds_button = tk.Button(toggle_frame, text="Odds", command=self.show_odds, bg="#555555", fg="#FFFFFF", font=("Cambria", 12), relief="flat", padx=10, pady=5)
        odds_button.pack(side="left", padx=5)

        # Chat/Odds Display
        self.display_frame = tk.Frame(self.sidebar, bg="#444444")
        self.display_frame.pack(fill="both", expand=True, pady=10, padx=10)

        # Settings and Main Menu Buttons
        settings_button = tk.Button(self.sidebar, text="Settings", command=self.open_settings, bg="#555555", fg="#FFFFFF", font=("Cambria", 12), relief="flat", padx=10, pady=10)
        settings_button.pack(side="bottom", fill="x", pady=5, padx=10)

        main_menu_button = tk.Button(self.sidebar, text="Main Menu", command=self.open_main_menu, bg="#555555", fg="#FFFFFF", font=("Cambria", 12), relief="flat", padx=10, pady=10)
        main_menu_button.pack(side="bottom", fill="x", pady=5, padx=10)

        # Game Area
        self.game_area = tk.Frame(main_pane, bg="#228B22")
        main_pane.add(self.game_area)

        self.sidebar_max_width = int(0.2 * 1280)
        self.sidebar.pack_propagate(False)
        self.sidebar.config(width=self.sidebar_max_width)

        # Initialize default view
        self.show_chat()
        self.initialise_game_area()

    def show_chat(self):
        for widget in self.display_frame.winfo_children():
            widget.destroy()

        chat_frame = tk.Frame(self.display_frame, bg="#444444")
        chat_frame.pack(fill="both", expand=True)

        # Chatbox
        chatbox = tk.Text(chat_frame, bg="#555555", fg="#FFFFFF", state="disabled", wrap="word", height=10, width=20, font=("Cambria", 10))
        chatbox.grid(row=0, column=0, sticky="nsew")

        # Scrollbar
        scrollbar = tk.Scrollbar(chat_frame, command=chatbox.yview, bg="#555555", troughcolor="#444444")
        scrollbar.grid(row=0, column=1, sticky="ns")
        chatbox.config(yscrollcommand=scrollbar.set)

        # Message Entry
        message_entry = tk.Entry(chat_frame, bg="#555555", fg="#FFFFFF", width=20, font=("Cambria", 10), insertbackground="white")
        message_entry.grid(row=1, column=0, sticky="ew")
        message_entry.bind("<Return>", lambda event: self.send_message(chatbox, message_entry))

        # Send Button
        send_button = tk.Button(chat_frame, text="Send", command=lambda: self.send_message(chatbox, message_entry), bg="#555555", fg="#FFFFFF", font=("Cambria", 10), relief="flat", padx=5, pady=5)
        send_button.grid(row=1, column=1, sticky="e")

        # Configure grid
        chat_frame.grid_rowconfigure(0, weight=1)
        chat_frame.grid_columnconfigure(0, weight=1)

        # Re-populate chatbox with previous messages
        chatbox.config(state="normal")
        for message in self.chat_messages:
            chatbox.insert("end", message + "\n")
        chatbox.config(state="disabled")
        chatbox.yview_moveto(1.0)  # Scroll to the end of the chatbox

    def send_message(self, chatbox, message_entry):
        message = message_entry.get()
        if message.strip() != "":
            message = f"{self.username}: {message}"
            self.chat_messages.append(message)  # Store the message
            chatbox.config(state="normal")
            chatbox.insert("end", message + "\n")
            chatbox.config(state="disabled")
            chatbox.yview_moveto(1.0)  # Scroll to the end of the chatbox
            message_entry.delete(0, "end")

    def show_odds(self):
        for widget in self.display_frame.winfo_children():
            widget.destroy()
        odds_label = tk.Label(self.display_frame, text="Odds will be displayed here.", bg="#444444", fg="#FFFFFF", font=("Cambria", 12))
        odds_label.pack(fill="both", expand=True)

    def open_settings(self):
        print("Open settings window")

    def open_main_menu(self):
        print("Go back to the main menu")

    def initialise_game_area(self):
        # Player Areas
        for i in range(6):  # 6 players
            player_frame = tk.Frame(self.game_area, bg="#228B22", bd=2, relief="ridge")
            if i < 3:
                player_frame.pack(side="top", padx=10, pady=10)
            else:
                player_frame.pack(side="bottom", padx=10, pady=10)

            # Placeholder for Player Name
            player_name_label = tk.Label(player_frame, text=f"Player {i + 1}", bg="#228B22", fg="#FFFFFF")
            player_name_label.pack()

            # Placeholder for Cards and Chips
            card1_label = tk.Label(player_frame, text="Card 1", bg="#FFFFFF", width=10, height=5)
            card1_label.pack(side="left", padx=5)
            card2_label = tk.Label(player_frame, text="Card 2", bg="#FFFFFF", width=10, height=5)
            card2_label.pack(side="left", padx=5)
            chips_label = tk.Label(player_frame, text="Chips", bg="#FFFF00", width=10, height=5)
            chips_label.pack(side="left", padx=5)

        # Community Card Area
        community_frame = tk.Frame(self.game_area, bg="#228B22")
        community_frame.pack(side="top", pady=20)

        # Placeholder for Community Cards and Pot
        for i in range(5):  # 5 community cards
            community_card_label = tk.Label(community_frame, text=f"Card {i + 1}", bg="#FFFFFF", width=10, height=5)
            community_card_label.pack(side="left", padx=5)
        pot_label = tk.Label(community_frame, text="Pot", bg="#FFFF00", width=10, height=5)
        pot_label.pack(side="left", padx=5)

        # Button Area
        button_frame = tk.Frame(self.game_area, bg="#228B22")
        button_frame.pack(side="bottom", pady=20)

        # Game Action Buttons
        fold_button = tk.Button(button_frame, text="Fold", bg="#FF0000", fg="#FFFFFF", command=self.fold_action)
        fold_button.pack(side="left", padx=10)
        raise_button = tk.Button(button_frame, text="Raise", bg="#00FF00", fg="#FFFFFF", command=self.raise_action)
        raise_button.pack(side="left", padx=10)
        call_check_button = tk.Button(button_frame, text="Call/Check", bg="#0000FF", fg="#FFFFFF",
                                      command=self.call_check_action)
        call_check_button.pack(side="left", padx=10)

    # Placeholder command methods
    def fold_action(self):
        pass

    def raise_action(self):
        pass

    def call_check_action(self):
        pass


if __name__ == "__main__":
    app = GameGUI(None, 2, None)
    app.mainloop()
