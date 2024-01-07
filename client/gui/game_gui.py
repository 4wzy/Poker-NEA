import base64
import json
import time
import tkinter as tk
from tkinter import simpledialog, messagebox

from PIL import Image, ImageDraw, ImageTk
from helpers.odds_logic import monte_carlo_hand_odds
from gui.user_profile import ProfilePictureManager

class GameGUI(tk.Tk):
    def __init__(self, controller, user_id, lobby_id, initial_state, player_starts_game, reconnecting, allow_odds):
        super().__init__()
        self.allow_odds = allow_odds
        self.is_chatbox_shown = False
        self.last_highlighted_player_id = None
        self.geometry("1280x720")
        self.configure(bg="#333333")
        self.controller = controller
        self.profile_picture_manager = ProfilePictureManager(self.controller)
        self.user_id = user_id
        self.username = self.controller.network_manager.send_message({"type": "get_username", "user_id": self.user_id})
        self.lobby_id = lobby_id
        self.chat_messages = []
        self.canvas_items = []
        self.is_leaving_game = False
        self.scheduled_tasks = []
        self.should_be_destroyed = False
        self.player_components = {}
        self.player_starts_game = player_starts_game
        self.community_card_items = []
        self.reconnecting = reconnecting
        self.odds_iterations = 2000

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
        if not allow_odds:
            odds_button.config(state="disabled")

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

        self.game_messages_label = tk.Label(self.game_canvas, text="Message: ", bg="#006400", fg="#FFFFFF",
                                            font=("Cambria", 12, "bold"))
        self.game_messages_label.place(x=420, y=670, anchor="center")

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
        task_id = self.after(10, self.network_loop)
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
                                 player_info['user_id'], player_info['chips'], player_info['profile_picture'])
            self.scheduled_tasks.append(task_id)

    def process_initial_state(self, initial_state):
        game_state = initial_state['game_state']
        print("(game_gui): processing initial state")
        self.place_players(game_state)
        if len(game_state['players']) == game_state['player_limit']:
            print("(game_gui): START GAME!!")
            # self.send_acknowledgment()
            if self.player_starts_game:
                print("updating game state")
                # The following call to self.after() is necessary so that the players are placed first before the
                # game attempts to update game components which don't exist yet
                self.after(10, self.start_game_update)
        if self.reconnecting:
            print("(game_gui): attempting to reconnect...")
            self.after(10, self.update_game_state, initial_state)

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

    def open_settings(self):
        # Create a new top-level window for settings
        settings_window = tk.Toplevel(self)
        settings_window.title("Settings")
        settings_window.geometry("500x300")
        settings_window.configure(bg="#333333")

        # Label for iterations input
        iterations_label = tk.Label(settings_window, text="Set Odds Iterations (10 - 100000):", bg="#333333",
                                    fg="#FFFFFF")
        iterations_label.pack(pady=10)

        # Entry for iterations input
        self.iterations_entry = tk.Entry(settings_window)
        self.iterations_entry.pack()

        extra_info_label = tk.Label(settings_window, text="The higher the number you choose the longer it will take to "
                                                          "simulate the odds.\nNumbers that end in 0 will often be "
                                                          "more resource efficient!", bg="#333333", fg="#FFFFFF")
        extra_info_label.pack(pady=10)

        # Button to apply settings
        apply_button = tk.Button(settings_window, text="Apply", command=self.apply_settings, bg="#555555", fg="#FFFFFF")
        apply_button.pack(pady=10)

    def apply_settings(self):
        # Get the value from the entry and validate it
        try:
            new_iterations = int(self.iterations_entry.get())
            if 10 <= new_iterations <= 100000:
                self.odds_iterations = new_iterations
                print(f"New iterations set to: {self.odds_iterations}")
            else:
                raise ValueError("The number of iterations must be between 10 and 100000.")
        except ValueError as e:
            tk.messagebox.showerror("Invalid Input, enter a valid number!", str(e))
        except TypeError as e:
            tk.messagebox.showerror("Invalid Input, please enter a number!", str(e))
        except Exception as e:
            tk.messagebox.showerror("Invalid Input, unknown exception:", str(e))

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
                    if message_type == 'receive_message':
                        print(f"Received message: {message}")
                        self.receive_message(message.get('chat_message'))
                    elif message_type == 'initial_state':
                        print(f"(game gui): Initial state message TYPE: {message}")
                        task_id = self.after(0, self.process_initial_state, message)
                        self.scheduled_tasks.append(task_id)
                    elif message_type in ['update_game_state', 'game_starting']:
                        print(f"(game_gui): UPDATING GAME STATE or GAME STARTING")
                        task_id = self.after(0, self.update_game_state, message)
                        self.scheduled_tasks.append(task_id)
                    elif message_type == "player_left_game_state":
                        task_id = self.after(0, self.process_player_left_game_state, message['game_state'])
                        self.scheduled_tasks.append(task_id)
                    elif message_type == 'update_showdown_state':
                        print("message type == update showdown state")
                        task_id = self.after(0, self.update_showdown_state, message)
                        self.scheduled_tasks.append(task_id)
                    elif message_type == 'update_completed_state':
                        print("updating completed state...")
                        task_id = self.after(0, self.update_completed_state, message)
                        self.scheduled_tasks.append(task_id)
                elif isinstance(message, list):
                    self.controller.process_received_message('lobby_list', message)
            except json.JSONDecodeError as e:
                print(f"JSON Decode Error: {e}")
                print(f"Data causing the error: {message_str}")
            except Exception as e:
                print(f"Unknown exception: {e}")

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

    def update_game_messages_label(self, text_to_update_with):
        self.game_messages_label.config(text=text_to_update_with)

    def update_completed_state(self, game_state):
        print("updating showdown state")
        print(f"(game_gui.py): updating game state for user")

        print(f"(game_gui.py): old game_state: {game_state}")
        game_state = game_state["game_state"]
        print(f"(game_gui): new game_state: {game_state}")

        self.indicate_active_players(game_state)
        self.indicate_folded_and_busted_and_disconnected_players(game_state)
        winning_player = [player for player in game_state["players"] if player["won_game"]][0]
        print(f"all winning players: {[player for player in game_state['players'] if player['won_game']]}")
        print(f"winning player: {winning_player}")
        self.indicate_game_winner(winning_player)

        self.update_game_messages_label(f"{winning_player['name']} wins the Poker game!")

    def update_game_state(self, game_state):
        self.hide_everyones_cards(game_state)
        print("updating game state")
        print(f"Trying to get user_id in game_state: {game_state}")
        user_id = game_state['user_id']
        print(f"(game_gui.py): updating game state for {user_id}")

        print(f"old game_state: {game_state}")
        game_state = game_state["game_state"]
        print(f"(game_gui): new game_state: {game_state}")

        if game_state.get("message"):
            self.update_game_messages_label(game_state.get("message"))

        self.update_roles(game_state)
        self.update_pot(game_state)

        self.indicate_active_players(game_state)
        self.show_current_player(game_state)
        self.indicate_folded_and_busted_and_disconnected_players(game_state)

        # Update card images if they are in the game_state
        # ONLY UPDATE THIS ONCE IN A GAME, WHEN ALL THE PLAYERS HAVE JOINED IF THIS IS THE "START GAME STATE"
        print(f"hand: {game_state.get('hand')}")
        self.show_local_cards(game_state, user_id)

        print(f"BOARD: {game_state['board']}")
        self.clear_community_cards()
        if len(game_state["board"]) > 0:
            self.place_community_cards(game_state["board"])

    def update_showdown_state(self, game_state):
        print("updating showdown state")
        print(f"(game_gui.py): updating game state for user")

        print(f"(game_gui.py): old game_state: {game_state}")
        game_state = game_state["game_state"]
        print(f"(game_gui): new game_state: {game_state}")

        # Disable the users action buttons, so they can't act during the showdown (which could lead to bugs)
        for button in self.buttons:
            button.config(state=tk.DISABLED)
        self.update_roles(game_state)
        self.update_pot(game_state)

        self.indicate_active_players(game_state)
        self.indicate_folded_and_busted_and_disconnected_players(game_state)
        self.indicate_winning_players(game_state)

        winner_message = game_state.get('winner_message')

        self.update_game_messages_label(winner_message)

        self.show_everyones_cards(game_state)

        print(f"BOARD: {game_state['board']}")
        self.clear_community_cards()
        if len(game_state["board"]) > 0:
            self.place_community_cards(game_state["board"])

    def update_pot(self, game_state):
        pot_amount = game_state.get('pot', 0)
        print(f"Pot amount: {pot_amount}")
        self.pot_label.config(text=f"Pot: {pot_amount}")
        print(f"pot_label: {self.process_lobby_list()}")

    def update_roles(self, game_state):
        # Get the components for each player, and update accordingly
        for player_data in game_state["players"]:
            # print(f"using player data: {player_data}")
            components = self.player_components.get(player_data["user_id"])
            if not components:
                # print(f"components: {components}")
                return
            if player_data:
                roles = []
                if "SB" in player_data['blinds']:
                    roles.append("Small Blind")
                if "BB" in player_data['blinds']:
                    roles.append("Big Blind")
                if player_data['dealer']:
                    roles.append("Dealer")
                if player_data['disconnected']:
                    roles.append("Disconnected")
                # elif used on purpose as disconnected players are not in the round by default
                elif player_data['busted']:
                    roles.append("Busted")
                elif player_data['folded']:
                    roles.append("Folded")
                elif player_data.get("won"):
                    roles.append("Winner")

                role_text = ", ".join(roles)

                bet = player_data['current_bet']
                components['bet_label'].config(text=f"Bet: {bet}")

                time.sleep(0.05)
                components['name_label'].config(text=f"{player_data['name']}: {player_data['chips']} chips")
                components['role_label'].config(text=role_text)
                print(f"Updated role label {components['role_label']} with text: {role_text}")
            else:
                print(f"No player data found..")

        pot_amount = game_state.get('pot', 0)
        print(f"Pot amount: {pot_amount}")
        self.pot_label.config(text=f"Pot: {pot_amount}")
        print(f"pot_label: {self.process_lobby_list()}")

    def show_local_cards(self, game_state, user_id):
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

    def show_everyones_cards(self, game_state):
        print("SHOWING EVERYONES CARDS!")
        for player in game_state['players']:
            user_id = player.get('user_id')
            components = self.player_components.get(user_id)
            if not components:
                print(f"No components found for user_id {user_id}")
                print(f"components: {components}")
                return
            for idx, card_str in enumerate(player.get('hand', [])):
                print(f"(game_gui): DEBUG idx: {idx} card_str: {card_str}")
                card_image_path = self.get_card_image_path(card_str)
                # print(f"(game_gui): card_image_path: {card_image_path}")
                card_photo = Image.open(card_image_path)
                card_photo = card_photo.resize((60, 90))
                card_photo = ImageTk.PhotoImage(card_photo)
                card_label = components[f'card{idx + 1}_label']
                # print(f"(game_gui): card_label before change: {card_label}")
                card_label.config(image=card_photo)
                card_label.photo = card_photo  # keep a reference to avoid garbage collection
                # print(f"(game_gui): card_label after change: {card_label}")

    def hide_everyones_cards(self, game_state):
        game_state = game_state['game_state']
        print("HIDING EVERYONES CARDS!")
        for player in game_state['players']:
            user_id = player.get('user_id')
            components = self.player_components.get(user_id)
            if not components:
                print(f"No components found for user_id {user_id}")
                print(f"components: {components}")
                return

            card_photo = Image.open("gui/Images/Cards/back.png")
            card_photo = card_photo.resize((60, 90))
            card_photo = ImageTk.PhotoImage(card_photo)
            card_label1 = components[f'card1_label']
            card_label2 = components[f'card2_label']
            card_label1.config(image=card_photo)
            card_label1.photo = card_photo
            card_label2.config(image=card_photo)
            card_label2.photo = card_photo

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

    def change_players_frame(self, players, colour):
        for player in players:
            current_player_components = self.player_components.get(player["user_id"])
            if current_player_components:
                current_player_frame = current_player_components['profile_label'].master
                current_player_frame.config(bg=colour)  # Highlight player frame with a colour

    def indicate_folded_and_busted_and_disconnected_players(self, game_state):
        folded_players = [player for player in game_state["players"] if player["folded"]]
        self.change_players_frame(folded_players, "#5A4E4B")

        disconnected_players = [player for player in game_state["players"] if player["disconnected"]]
        self.change_players_frame(disconnected_players, "#450e00")

        busted_players = [player for player in game_state["players"] if player["busted"]]
        self.change_players_frame(busted_players, "#090245")

    def indicate_game_winner(self, winning_player):
        # Change players frame takes in a list of players of frames to change, hence the code below
        self.change_players_frame([winning_player], "#03ebfc")

    def indicate_winning_players(self, game_state):
        # First make every player's profile have a standard grey background
        losing_players = [player for player in game_state["players"] if not player["won_round"]]
        self.change_players_frame(losing_players, "#302525")

        winning_players = [player for player in game_state["players"] if player["won_round"]]
        self.change_players_frame(winning_players, "#03ebfc")

    def indicate_active_players(self, game_state):
        active_players = [p for p in game_state["players"] if not p["folded"]]
        self.change_players_frame(active_players, "#302525")

    def send_player_action(self, action):
        if action == "raise":
            raise_amount = simpledialog.askinteger(f"Raise Amount", "Enter the amount you want to raise):",
                                                   parent=self)
            if raise_amount:
                message = {"type": "bet", "action": action, "amount": raise_amount, "user_id": self.user_id,
                           "lobby_id": \
                               self.lobby_id}
            elif raise_amount == 0:
                messagebox.showerror("Error", "You need to raise by a valid amount! (not 0)")
        else:
            message = {"type": "bet", "action": action, "user_id": self.user_id, "lobby_id": self.lobby_id}

        action_response = self.controller.network_manager.send_message(message)
        print(f"action_response: {action_response}")

        if action_response.get("success"):
            if action_response.get("game_completed"):
                print("about to send broadcast_completed_game_state signal")
                signal_message = {"type": "broadcast_completed_game_state", "lobby_id": self.lobby_id}
                self.controller.network_manager.send_signal(signal_message)
            elif action_response.get("showdown"):
                # send signal to broadcast showdown state
                signal_message = {"type": "broadcast_showdown", "lobby_id": self.lobby_id}
                print("about to send broadcast_showdown signal")
                task_id = self.after(0, self.controller.network_manager.send_signal, signal_message)
                self.scheduled_tasks.append(task_id)
                # then wait 8 seconds and send signal to broadcast update game state

                signal_message = {"type": "start_next_round", "lobby_id": self.lobby_id}
                print("about to send start_next_round signal")
                task_id = self.after(9000, self.controller.network_manager.send_signal, signal_message)
                self.scheduled_tasks.append(task_id)
            else:
                # send signal to broadcast update game state
                print("about to send broadcast_new_game_state signal")
                signal_message = {"type": "broadcast_new_game_state", "lobby_id": self.lobby_id}
                self.controller.network_manager.send_signal(signal_message)
        else:
            error_message = action_response.get("error", "An unknown error occurred.")
            messagebox.showerror("Error", error_message)

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

        self.is_chatbox_shown = True

        chat_frame = tk.Frame(self.display_frame, bg="#444444")
        chat_frame.pack(fill="both", expand=True)

        self.chatbox = tk.Text(chat_frame, bg="#555555", fg="#FFFFFF", state="disabled", wrap="word", height=10,
                               width=20,
                               font=("Cambria", 10))
        self.chatbox.grid(row=0, column=0, sticky="nsew")

        scrollbar = tk.Scrollbar(chat_frame, command=self.chatbox.yview, bg="#555555", troughcolor="#444444")
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.chatbox.config(yscrollcommand=scrollbar.set)

        message_entry = tk.Entry(chat_frame, bg="#555555", fg="#FFFFFF", width=20, font=("Cambria", 10),
                                 insertbackground="white")
        message_entry.grid(row=1, column=0, sticky="ew")
        message_entry.bind("<Return>", lambda event: self.send_message(message_entry))

        send_button = tk.Button(chat_frame, text="Send", command=lambda: self.send_message(message_entry),
                                bg="#555555", fg="#FFFFFF", font=("Cambria", 10), relief="flat", padx=5, pady=5)
        send_button.grid(row=1, column=1, sticky="e")

        chat_frame.grid_rowconfigure(0, weight=1)
        chat_frame.grid_columnconfigure(0, weight=1)

        # Add the previous messages to the chatbox
        self.chatbox.config(state="normal")
        for message in self.chat_messages:
            self.chatbox.insert("end", message + "\n")
        self.chatbox.config(state="disabled")
        self.chatbox.yview_moveto(1.0)

    def send_message(self, message_entry):
        raw_message = message_entry.get()
        # The code below stops users from sending empty messages and prevents users from maliciously impersonating
        # other users
        message = raw_message.lstrip()

        if message:
            formatted_message = f"{self.username}: {message}"
            message_to_send = {
                'type': 'send_chat',
                'lobby_id': self.lobby_id,
                'message': formatted_message
            }

            # Send the message to the server
            response = self.controller.network_manager.send_message(message_to_send)
            if response.get('success'):
                self.receive_message(formatted_message)
            else:
                messagebox.showerror("Error", f"Unable to send message. Exception: {response.get('exception')}")

            # Clear the message entry box
            message_entry.delete(0, "end")

    def receive_message(self, message):
        # The chat_messages array is used to store all messages sent
        self.chat_messages.append(message)
        if self.is_chatbox_shown:
            self.chatbox.config(state="normal")
            self.chatbox.insert("end", message + "\n")
            self.chatbox.config(state="disabled")
            self.chatbox.yview_moveto(1.0)

    def show_odds(self):
        self.is_chatbox_shown = False

        for widget in self.display_frame.winfo_children():
            widget.destroy()
        odds_label = tk.Label(self.display_frame, text="Odds will be displayed here.", bg="#444444", fg="#FFFFFF",
                              font=("Cambria", 12))
        odds_label.pack(fill="both", expand=True)

        game_data = self.controller.network_manager.send_message({
            'type': 'get_data_for_odds',
            'user_id': self.user_id,
            'lobby_id': self.lobby_id
        })

        print(f"GAME DATA: {game_data}")
        odds = monte_carlo_hand_odds(game_data[0], game_data[1], self.odds_iterations)

        if not odds:
            odds_text = "No odds yet.\nWait for your cards to be dealt!"
        else:
            odds_text = "Odds of each hand ranking:\n"
            for hand_type, probability in odds.items():
                odds_text += f"{hand_type}: {probability:.2%}\n"

        odds_label.config(text=odds_text)

    def leave_game(self):
        player_left = self.controller.network_manager.send_message({
            'type': 'leave_lobby',
            'user_id': self.user_id,
            'lobby_id': self.lobby_id
        })
        self.is_leaving_game = True
        print(f"(leave game from game_gui): {player_left}")
        self.controller.open_main_menu(self.user_id)

    def fetch_and_store_profile_picture(self, user_id, profile_picture_filename):
        response = self.controller.network_manager.send_message({
            "type": "get_profile_picture",
            "user_id": user_id
        })
        encoded_image_data = response['image_data']
        image_data = base64.b64decode(encoded_image_data)
        with open(f"gui/Images/Pfps/{profile_picture_filename}", "wb") as file:
            file.write(image_data)

    def place_player(self, x, y, name, position, user_id, chips, profile_picture_filename):
        try:
            # Create a frame to hold the player components
            player_frame = tk.Frame(self.game_canvas, bg="#302525")

            local_pfp_path = self.profile_picture_manager.check_and_fetch_profile_picture(user_id)
            if not local_pfp_path:
                local_pfp_path = f"gui/Images/Pfps/default.png"

            profile_photo = Image.open(local_pfp_path)
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

            profile_label.bind("<Button-1>", lambda event: self.controller.open_user_profile(profile_user_id=user_id, own_user_id=self.user_id, update_previous_menu=False))

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
