import json
import threading
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageDraw, ImageTk
from logic.database_interaction import DatabaseInteraction
import socket


class GameGUI(tk.Tk):
    def __init__(self, controller, user_id, lobby_name, initial_state):
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

        self.logo = Image.open("gui/Images/logo.png")
        self.logo = self.logo.resize((50, 50))
        self.logo = ImageTk.PhotoImage(self.logo)

        logo_image_label = tk.Label(logo_frame, image=self.logo, bg="#444444")
        logo_image_label.pack(side='left', padx=5)

        logo_text_label = tk.Label(logo_frame, text="AceAware Poker", bg="#444444", fg="#FFFFFF",
                                   font=("Cambria", 14, "bold"))
        logo_text_label.pack(side='left', padx=5)

        toggle_frame = tk.Frame(self.sidebar, bg="#333333")
        toggle_frame.pack(pady=10)

        chat_button = tk.Button(toggle_frame, text="Chat", command=self.show_chat, bg="#555555", fg="#FFFFFF",
                                font=("Cambria", 12), relief="flat", padx=10, pady=5)
        chat_button.pack(side="left", padx=5)

        odds_button = tk.Button(toggle_frame, text="Odds", command=self.show_odds, bg="#555555", fg="#FFFFFF",
                                font=("Cambria", 12), relief="flat", padx=10, pady=5)
        odds_button.pack(side="left", padx=5)

        # Chat/Odds Display
        self.display_frame = tk.Frame(self.sidebar, bg="#444444")
        self.display_frame.pack(fill="both", expand=True, pady=10, padx=10)

        settings_button = tk.Button(self.sidebar, text="Settings", command=self.open_settings, bg="#555555",
                                    fg="#FFFFFF", font=("Cambria", 12), relief="flat", padx=10, pady=10)
        settings_button.pack(side="bottom", fill="x", pady=5, padx=10)

        leave_button = tk.Button(self.sidebar, text="Leave", command=self.leave_game, bg="#555555",
                                     fg="#FFFFFF", font=("Cambria", 12), relief="flat", padx=10, pady=10)
        leave_button.pack(side="bottom", fill="x", pady=5, padx=10)

        self.game_area = tk.Frame(main_pane, bg="#302525")
        main_pane.add(self.game_area)

        self.sidebar_max_width = int(0.2 * 1280)
        self.sidebar.pack_propagate(False)
        self.sidebar.config(width=self.sidebar_max_width)

        self.show_chat()

        self.game_canvas = tk.Canvas(self.game_area, bg="#302525", highlightthickness=0)
        self.game_canvas.pack(fill="both", expand=True)

        # Draw Poker Table
        table_x, table_y, table_radius = 420, 360, 170
        self.game_canvas.create_oval(table_x - table_radius * 1.5, table_y - table_radius * 0.95,
                                     table_x + table_radius * 1.5,
                                     table_y + table_radius * 0.95, fill="#006400", outline="#8B4513",
                                     width=2)

        # Define the buttons
        buttons = [
            tk.Button(self.game_area, text="Call/Check", command=lambda: self.send_player_action("call"), bg="#555555",
                      fg="#FFFFFF",
                      font=("Cambria", 12), relief="flat", height=2, width=10),
            tk.Button(self.game_area, text="Raise", command=lambda: self.send_player_action("raise"), bg="#555555",
                      fg="#FFFFFF",
                      font=("Cambria", 12), relief="flat", height=2, width=10),
            tk.Button(self.game_area, text="Fold", command=lambda: self.send_player_action("fold"), bg="#555555",
                      fg="#FFFFFF",
                      font=("Cambria", 12), relief="flat", height=2, width=10),
        ]

        for i, button in enumerate(buttons):
            button.place(relx=0.9, rely=0.2 * (2 * i + 5) / len(buttons), anchor='center')

        self.controller.network_manager.client_socket.setblocking(0)
        self.network_loop()

        self.process_initial_state(initial_state)

    def network_loop(self):
        s = self.controller.network_manager.client_socket
        try:
            # Try to receive data from the server
            data = s.recv(4096)

            # If data is received, process it
            if data:
                self.process_server_message(data)
        except BlockingIOError:
            # If no data is received, continue without blocking
            pass

        # Schedule the next call to the network_loop method
        self.after(100, self.network_loop)

    def process_initial_state(self, initial_state):
        print("processing initial state")
        for player_info in initial_state['players']:
            x, y = self.get_coordinates_for_position(player_info['position'])
            self.after(0, self.place_player, x, y, player_info['name'], player_info['position'])

    def get_coordinates_for_position(self, position):
        positions = {
            'top_left': (190, 200),
            'top_middle': (420, 190),
            'top_right': (650, 200),
            'bottom_left': (130, 440),
            'bottom_middle': (420, 530),
            'bottom_right': (710, 440),
        }
        return positions.get(position, (0, 0))

    def process_server_message(self, data):
        message = json.loads(data.decode('utf-8'))
        print(f"server_message: {message}")
        if message['type'] == 'initial_state':
            print(f"Initial state message TYPE: {message}")
            self.after(0, self.process_initial_state, message['game_state'])
        elif message['type'] == 'update_game_state':
            self.after(0, self.update_game_state, message['game_state'])

    def update_game_state(self, game_state):
        # Update the game GUI based on the received game_state
        # For example, update player positions, chips, cards, etc.
        pass

    def send_player_action(self, action):
        # Send a player action (fold, call, raise) to the server
        pass

    def show_chat(self):
        for widget in self.display_frame.winfo_children():
            widget.destroy()

        chat_frame = tk.Frame(self.display_frame, bg="#444444")
        chat_frame.pack(fill="both", expand=True)

        # Chatbox
        chatbox = tk.Text(chat_frame, bg="#555555", fg="#FFFFFF", state="disabled", wrap="word", height=10, width=20,
                          font=("Cambria", 10))
        chatbox.grid(row=0, column=0, sticky="nsew")

        # Scrollbar
        scrollbar = tk.Scrollbar(chat_frame, command=chatbox.yview, bg="#555555", troughcolor="#444444")
        scrollbar.grid(row=0, column=1, sticky="ns")
        chatbox.config(yscrollcommand=scrollbar.set)

        # Message Entry
        message_entry = tk.Entry(chat_frame, bg="#555555", fg="#FFFFFF", width=20, font=("Cambria", 10),
                                 insertbackground="white")
        message_entry.grid(row=1, column=0, sticky="ew")
        message_entry.bind("<Return>", lambda event: self.send_message(chatbox, message_entry))

        # Send Button
        send_button = tk.Button(chat_frame, text="Send", command=lambda: self.send_message(chatbox, message_entry),
                                bg="#555555", fg="#FFFFFF", font=("Cambria", 10), relief="flat", padx=5, pady=5)
        send_button.grid(row=1, column=1, sticky="e")

        # Configure grid
        chat_frame.grid_rowconfigure(0, weight=1)
        chat_frame.grid_columnconfigure(0, weight=1)

        # Add the previous messages to the chatbox
        chatbox.config(state="normal")
        for message in self.chat_messages:
            chatbox.insert("end", message + "\n")
        chatbox.config(state="disabled")
        chatbox.yview_moveto(1.0)

    def send_message(self, chatbox, message_entry):
        message = message_entry.get()
        if message.strip() != "":
            message = f"{self.username}: {message}"
            # The chat_messages array is used to store all messages sent
            self.chat_messages.append(message)
            chatbox.config(state="normal")
            chatbox.insert("end", message + "\n")
            chatbox.config(state="disabled")
            chatbox.yview_moveto(1.0)
            message_entry.delete(0, "end")

    def show_odds(self):
        for widget in self.display_frame.winfo_children():
            widget.destroy()
        odds_label = tk.Label(self.display_frame, text="Odds will be displayed here.", bg="#444444", fg="#FFFFFF",
                              font=("Cambria", 12))
        odds_label.pack(fill="both", expand=True)

    def open_settings(self):
        print("Open settings window")

    def leave_game(self):
        self.controller.network_manager.send_message({
            'type': 'leave_lobby',
            'user_id': self.user_id,
            'lobby_name': self.lobby_name
        })
        self.controller.open_main_menu(self.user_id)

    def place_player(self, x, y, name, position):
        # Create a frame to hold the player components
        player_frame = tk.Frame(self.game_canvas, bg="#302525")

        profile_photo = Image.open("gui/Images/Pfps/default.png")
        profile_photo = profile_photo.resize((50, 50))

        # Create a mask
        mask = Image.new('L', profile_photo.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + profile_photo.size, fill=255)

        # Apply the mask to the image
        profile_photo.putalpha(mask)
        profile_photo = ImageTk.PhotoImage(profile_photo)

        profile_label = tk.Label(player_frame, image=profile_photo, bg="#302525")
        profile_label.photo = profile_photo  # keep a reference to avoid garbage collection
        profile_label.pack()

        # Add name label
        name_label = tk.Label(player_frame, text=name, bg="#302525", fg="#FFFFFF")
        name_label.pack()

        # Add card images
        if self.username == name:
            card1_photo = Image.open("gui/Images/Cards/black_joker.png")
            card2_photo = Image.open("gui/Images/Cards/black_joker.png")
        else:
            card1_photo = Image.open("gui/Images/Cards/back.png")
            card2_photo = Image.open("gui/Images/Cards/back.png")

        card1_photo = card1_photo.resize((60, 90))
        card1_photo = ImageTk.PhotoImage(card1_photo)
        card1_label = tk.Label(player_frame, image=card1_photo, bg="#302525")
        card1_label.photo = card1_photo  # keep a reference to avoid garbage collection
        card1_label.pack(side="left", padx=2)


        card2_photo = card2_photo.resize((60, 90))
        card2_photo = ImageTk.PhotoImage(card2_photo)
        card2_label = tk.Label(player_frame, image=card2_photo, bg="#302525")
        card2_label.photo = card2_photo  # keep a reference to avoid garbage collection
        card2_label.pack(side="left", padx=2)

        # Positioning the player frame on the canvas
        anchor_point = "center"
        if position == "top":
            anchor_point = "s"
        elif position == "bottom":
            anchor_point = "n"
        elif position == "left":
            anchor_point = "e"
        elif position == "right":
            anchor_point = "w"

        self.game_canvas.create_window(x, y, window=player_frame, anchor=anchor_point)

    def fold_action(self):
        pass

    def raise_action(self):
        pass

    def call_check_action(self):
        pass


# if __name__ == "__main__":
#     app = GameGUI(None, 2, None)
#     app.mainloop()
