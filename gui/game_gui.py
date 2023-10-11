import json
import time
import tkinter as tk
from tkinter import simpledialog, messagebox

from PIL import Image, ImageDraw, ImageTk
from logic.database_interaction import DatabaseInteraction


class GameGUI(tk.Tk):
    def __init__(self, controller, user_id, lobby_id, initial_state, player_starts_game):
        super().__init__()
        self.last_highlighted_player_id = None
        self.geometry("1280x720")
        self.configure(bg="#333333")
        self.controller = controller
        self.database_interaction = DatabaseInteraction()
        self.user_id = user_id
        self.username = self.database_interaction.get_username(self.user_id)
        self.lobby_id = lobby_id
        self.chat_messages = []
        self.canvas_items = []
        self.is_leaving_game = False
        self.scheduled_tasks = []
        self.should_be_destroyed = False
        self.player_components = {}
        self.player_starts_game = player_starts_game
        self.community_card_items = []

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

        self.pot_label = tk.Label(self.game_canvas, text="Pot: 0", bg="#006400", fg="#FFFFFF",
                                  font=("Cambria", 12, "bold"))
        self.pot_label.place(x=420, y=430, anchor="center")

        # Define the buttons
        self.buttons = [
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

        for i, button in enumerate(self.buttons):
            button.place(relx=0.9, rely=0.2 * (2 * i + 5) / len(self.buttons), anchor='center')
            # Disable the buttons by default so that the user can not act before a game has started
            button.config(state=tk.DISABLED)

        self.controller.network_manager.client_socket.setblocking(0)
        self.network_loop()
        print(self.controller.network_manager.client_socket)

        print(f"Processing initial state with data: {initial_state}")
        self.process_initial_state(initial_state)

    def network_loop(self):
        if self.should_be_destroyed:
            print(f"Stopping network_loop on {self} as it should be destroyed.")
            return
        s = self.controller.network_manager.client_socket
        try:
            # Try to receive data from the server
            data = s.recv(16384)
            print(f"received data: {data}")

            # If data is received, process it
            if data:
                self.process_server_message(data)
        except BlockingIOError:
            # If no data is received, continue without blocking
            pass

        # Schedule the next call to the network_loop method
        task_id = self.after(20, self.network_loop)
        self.scheduled_tasks.append(task_id)

    def destroy(self) -> None:
        print(f"Destroying {self}")
        self.should_be_destroyed = True
        for task_id in self.scheduled_tasks:
            print(f"Cancelling task {task_id}")
            self.after_cancel(task_id)
        super().destroy()

    def place_players(self, game_state):
        print(f"Placing players from {game_state}")
        for player_info in game_state['players']:
            x, y = self.get_coordinates_for_position(player_info['position'])
            task_id = self.after(0, self.place_player, x, y, player_info['name'], player_info['position'],
                                 player_info['user_id'], player_info['chips'])
            self.scheduled_tasks.append(task_id)

    def process_initial_state(self, initial_state):
        print("(game_gui): processing initial state")
        self.place_players(initial_state)
        if len(initial_state['players']) == initial_state['player_limit']:
            print("(game_gui): START GAME!!")
            # self.send_acknowledgment()
            if self.player_starts_game:
                print("updating game state")
                # The following call to self.after() is necessary so that the players are placed first before the
                # game attempts to update game components which don't exist yet
                self.after(20, self.start_game_update)

    # Could be made as a private method
    def start_game_update(self):
        print("starting game update")
        self.update_game_state(self.controller.network_manager.send_start_game_message(self.lobby_id))
        self.player_starts_game = False

    def process_player_left_game_state(self, player_left_state):
        print("game_gui.py: PROCESSING PLAYER LEFT STATE")
        # Delete old items from the canvas
        for item_id in self.canvas_items:
            self.game_canvas.delete(item_id)
        self.canvas_items.clear()  # Clear the list of stored IDs
        print("game_gui.py: CANVAS CLEARED")

        # Now place the new players
        self.place_players(player_left_state)
        print("game_gui.py: PLAYERS PLACED AGAIN")
        # Update the rest of the game state
        # self.update_game_state(player_left_state)

    def get_coordinates_for_position(self, position):
        positions = {
            'top_left': (190, 200),
            'top_middle': (420, 190),
            'top_right': (650, 200),
            'bottom_left': (130, 440),
            'bottom_middle': (420, 550),
            'bottom_right': (710, 440),
        }
        return positions.get(position, (0, 0))

    def process_server_message(self, data):
        print(f"process_server_message called on {self}")
        if self.should_be_destroyed:
            print(f"process_server_message called on a destroyed instance {self}")
            return

        data_str = data.decode('utf-8')
        messages = data_str.strip().split('\n')  # split by newline and strip to handle trailing newlines

        for message_str in messages:
            try:
                message = json.loads(message_str)
                print(f"server_message: {message}")
                if isinstance(message, dict):
                    message_type = message.get('type')
                    if message_type == 'initial_state':
                        print(f"(game gui): Initial state message TYPE: {message}")
                        task_id = self.after(0, self.process_initial_state, message['game_state'])
                        self.scheduled_tasks.append(task_id)
                    elif message_type in ['update_game_state', 'game_starting']:
                        print(f"(game_gui): UPDATING GAME STATE or GAME STARTING")
                        task_id = self.after(1, self.update_game_state, message)
                        self.scheduled_tasks.append(task_id)
                    elif message_type == "player_left_game_state":
                        task_id = self.after(0, self.process_player_left_game_state, message['game_state'])
                        self.scheduled_tasks.append(task_id)
                elif isinstance(message, list):
                    self.controller.process_received_message('lobby_list', message)
            except json.JSONDecodeError as e:
                print(f"JSON Decode Error: {e}")
                print(f"Data causing the error: {message_str}")

    def process_lobby_list(self):
        pass

    def get_card_image_path(self, card: str):
        parts = card.split(' ')
        rank = parts[0]
        suit = parts[1]

        # Construct the file name
        if rank == "Ace":
            rank = "ace"
        elif rank == "Jack":
            rank = "jack"
        elif rank == "Queen":
            rank = "queen"
        elif rank == "King":
            rank = "king"
        else:
            rank = rank.lower()

        suit = suit.lower()

        file_name = f"gui/Images/Cards/{rank}_of_{suit}.png"
        return file_name

    def update_game_state(self, game_state):
        print(f"Trying to get user_id in game_state: {game_state}")
        user_id = game_state['user_id']
        print(f"(game_gui.py): updating game state for {user_id}")

        print(f"old game_state: {game_state}")
        game_state = game_state["game_state"]
        print(f"(game_gui): new game_state: {game_state}")

        # Get the components for each player, and update accordingly
        for player_data in game_state["players"]:
            print(f"using player data: {player_data}")
            components = self.player_components.get(player_data["user_id"])
            if not components:
                print(f"No components found for user_id {user_id}")
                print(f"components: {components}")
                return
            if player_data:
                roles = []
                if "SB" in player_data['blinds']:
                    roles.append("Small Blind")
                if "BB" in player_data['blinds']:
                    roles.append("Big Blind")
                if player_data['dealer']:
                    roles.append("Dealer")
                if player_data['folded']:
                    roles.append("Folded")

                role_text = ", ".join(roles)

                bet = player_data['current_bet']
                components['bet_label'].config(text=f"Bet: {bet}")

                time.sleep(0.05)
                components['name_label'].config(text=f"{player_data['name']}: {player_data['chips']} chips")
                components['role_label'].config(text=role_text)
                print(f"Updated role label {components['role_label']} with text: {role_text}")
            else:
                print(f"No player data found for user_id {user_id}")

        pot_amount = game_state.get('pot', 0)
        print(f"Pot amount: {pot_amount}")
        self.pot_label.config(text=f"Pot: {pot_amount}")
        print(f"pot_label: {self.process_lobby_list()}")

        self.indicate_active_players(game_state)
        self.show_current_player(game_state)
        self.indicate_folded_players(game_state)

        # Update card images if they are in the game_state
        # ONLY UPDATE THIS ONCE IN A GAME, WHEN ALL THE PLAYERS HAVE JOINED IF THIS IS THE "START GAME STATE"
        print(f"hand: {game_state.get('hand')}")
        components = self.player_components.get(user_id)
        if not components:
            print(f"No components found for user_id {user_id}")
            print(f"components: {components}")
            return
        for idx, card_str in enumerate(game_state.get('hand', [])):
            print(f"(game_gui): DEBUG idx: {idx} card_str: {card_str}")
            card_image_path = self.get_card_image_path(card_str)
            print(f"(game_gui): card_image_path: {card_image_path}")
            card_photo = Image.open(card_image_path)
            card_photo = card_photo.resize((60, 90))
            card_photo = ImageTk.PhotoImage(card_photo)
            card_label = components[f'card{idx + 1}_label']
            print(f"(game_gui): card_label before change: {card_label}")
            card_label.config(image=card_photo)
            card_label.photo = card_photo  # keep a reference to avoid garbage collection
            print(f"(game_gui): card_label after change: {card_label}")

        print(f"BOARD: {game_state['board']}")
        self.clear_community_cards()
        if len(game_state["board"]) > 0:
            self.place_community_cards(game_state["board"])

    def show_current_player(self, game_state):
        print("Showing current player")
        current_turn_player_id = game_state["players"][game_state['current_player_turn']]['user_id']
        print(f"Finding current player {[game_state['current_player_turn']]} from {game_state['players']}")
        print(f"Current player ID turn: {current_turn_player_id}")

        # Unhighlight the last player's frame
        if self.last_highlighted_player_id:
            last_player_components = self.player_components.get(self.last_highlighted_player_id)
            if last_player_components:
                last_player_frame = last_player_components[
                    'profile_label'].master
                last_player_frame.config(bg="#302525")  # Resetting to original background colour.
                print(f"Last highlighted player id {self.last_highlighted_player_id} frame changed to grey colour")

        # Highlight the current player's frame
        current_player_components = self.player_components.get(current_turn_player_id)
        if current_player_components:
            current_player_frame = current_player_components['profile_label'].master
            current_player_frame.config(bg="#FFD700")  # Highlighting with a gold colour.
            self.last_highlighted_player_id = current_turn_player_id
            print(f"Current highlighted player id {current_turn_player_id} frame changed to gold colour")

        # Enable/Disable action buttons based on whose turn it is
        if current_turn_player_id == self.user_id:
            print(f"YES Current turn id == user id : {current_turn_player_id} = {self.user_id}")
            # Enable the buttons
            for button in self.buttons:
                button.config(state=tk.NORMAL)
        else:
            print(f"NO Current turn id != user id : {current_turn_player_id} != {self.user_id}")
            # Disable the buttons
            for button in self.buttons:
                button.config(state=tk.DISABLED)

    def indicate_folded_players(self, game_state):
        # print(f"game_state of players: {game_state['players']}")
        folded_players = [p for p in game_state["players"] if p["folded"]]
        for player in folded_players:
            current_player_components = self.player_components.get(player["user_id"])
            if current_player_components:
                current_player_frame = current_player_components['profile_label'].master
                current_player_frame.config(bg="#5A4E4B")  # Highlighting with a grey color.

    def indicate_active_players(self, game_state):
        # print(f"game_state of players: {game_state['players']}")
        active_players = [p for p in game_state["players"] if not p["folded"]]
        for player in active_players:
            # print(player)
            current_player_components = self.player_components.get(player["user_id"])
            if current_player_components:
                current_player_frame = current_player_components['profile_label'].master
                current_player_frame.config(bg="#302525")

    def raise_action(self):
        pass

    def send_player_action(self, action):
        if action == "raise":
            raise_amount = simpledialog.askinteger(f"Raise Amount", "Enter the amount you want to raise):",
                                                   parent=self)
            while not raise_amount:
                raise_amount = simpledialog.askinteger("Raise Amount", "Enter the amount you want to raise:",
                                                       parent=self)
            if raise_amount:
                message = {"type": "bet", "action": action, "amount": raise_amount, "user_id": self.user_id,
                           "lobby_id": \
                               self.lobby_id}
        else:
            message = {"type": "bet", "action": action, "user_id": self.user_id, "lobby_id": self.lobby_id}

        response = self.controller.network_manager.send_message(message)
        if response.get("success") or response.get("type") == "update_game_state":
            self.update_game_state(response)
        else:
            error_message = response.get("error", "An unknown error occurred.")
            messagebox.showerror("Error", error_message)
        print(f"send_player_action response: {response}")

    def clear_community_cards(self):
        for item_id in self.community_card_items:
            self.game_canvas.delete(item_id)
        self.community_card_items = []

    def place_community_cards(self, cards):
        card_x, card_y = 420, 360  # Center of the screen
        gap = 20  # Gap between cards

        for idx, card_str in enumerate(cards):
            card_image_path = self.get_card_image_path(card_str)
            card_photo = Image.open(card_image_path)
            card_photo = card_photo.resize((60, 90))
            card_photo = ImageTk.PhotoImage(card_photo)

            card_label = tk.Label(self.game_canvas, image=card_photo, bg="#302525")
            card_label.photo = card_photo  # keep a reference to avoid garbage collection

            card_x_offset = (idx - 2) * (60 + gap)  # -2 to center the cards
            item_id = self.game_canvas.create_window(card_x + card_x_offset, card_y, window=card_label)
            self.community_card_items.append(item_id)
            self.canvas_items.append(item_id)

    def show_chat(self):
        for widget in self.display_frame.winfo_children():
            widget.destroy()

        chat_frame = tk.Frame(self.display_frame, bg="#444444")
        chat_frame.pack(fill="both", expand=True)

        chatbox = tk.Text(chat_frame, bg="#555555", fg="#FFFFFF", state="disabled", wrap="word", height=10, width=20,
                          font=("Cambria", 10))
        chatbox.grid(row=0, column=0, sticky="nsew")

        scrollbar = tk.Scrollbar(chat_frame, command=chatbox.yview, bg="#555555", troughcolor="#444444")
        scrollbar.grid(row=0, column=1, sticky="ns")
        chatbox.config(yscrollcommand=scrollbar.set)

        message_entry = tk.Entry(chat_frame, bg="#555555", fg="#FFFFFF", width=20, font=("Cambria", 10),
                                 insertbackground="white")
        message_entry.grid(row=1, column=0, sticky="ew")
        message_entry.bind("<Return>", lambda event: self.send_message(chatbox, message_entry))

        send_button = tk.Button(chat_frame, text="Send", command=lambda: self.send_message(chatbox, message_entry),
                                bg="#555555", fg="#FFFFFF", font=("Cambria", 10), relief="flat", padx=5, pady=5)
        send_button.grid(row=1, column=1, sticky="e")

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
        player_left = self.controller.network_manager.send_message({
            'type': 'leave_lobby',
            'user_id': self.user_id,
            'lobby_id': self.lobby_id
        })
        self.is_leaving_game = True
        print(f"(leave game from game_gui): {player_left}")
        self.controller.open_main_menu(self.user_id)

    def place_player(self, x, y, name, position, user_id, chips):
        # print(f"placing player: {name}")
        try:
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
            name_label = tk.Label(player_frame, text=f"{name}: {chips} chips", bg="#302525", fg="#FFFFFF")
            name_label.pack()

            # Role label (for blinds/dealer)
            role_label = tk.Label(player_frame, text="", bg="#302525", fg="#FFFFFF")
            role_label.pack()

            # Current bet label
            bet_label = tk.Label(player_frame, text=f"Bet: 0", bg="#302525", fg="#FFFFFF")
            bet_label.pack()

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

            self.player_components[user_id] = {
                'profile_label': profile_label,
                'name_label': name_label,
                'card1_label': card1_label,
                'card2_label': card2_label,
                'role_label': role_label,
                'bet_label': bet_label
            }
            # print(f"PLAYER COMPONENTS: {self.player_components}")

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

            item_id = self.game_canvas.create_window(x, y, window=player_frame, anchor=anchor_point)
            self.canvas_items.append(item_id)
        except Exception as e:
            print(f"PLACING PLAYER EXCEPTION: {e}")

    def fold_action(self):
        pass

    def call_check_action(self):
        print("Player checked locally")

# if __name__ == "__main__":
#     app = GameGUI(None, 2, None)
#     app.mainloop()
