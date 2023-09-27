import threading
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageDraw, ImageTk
from logic.database_interaction import DatabaseInteraction
import socket

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

        self.network_thread = threading.Thread(target=self.network_loop)
        self.network_thread.daemon = True  # Daemonize thread to exit when main program exits
        self.network_thread.start()

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

        self.game_canvas = tk.Canvas(self.game_area, bg="#228B22", highlightthickness=0)
        self.game_canvas.pack(fill="both", expand=True)

        # Draw Poker Table
        table_x, table_y, table_radius = 420, 360, 170  # adjust the position, size as needed
        self.game_canvas.create_oval(table_x - table_radius * 1.5, table_y - table_radius * 0.95, table_x + table_radius * 1.5,
                                     table_y + table_radius * 0.95, fill="#006400", outline="#8B4513",
                                     width=2)  # Green oval for the table

        # Arrange Players
        self.place_player(420, 190, "Top Middle Player", "top")  # adjust the positions as needed
        self.place_player(650, 200, "Top Right Player", "right")
        self.place_player(190, 200, "Top Left Player", "left")
        self.place_player(420, 530, "Bottom Middle Player", "bottom")
        self.place_player(710, 440, "Bottom Right Player", "bottom")
        self.place_player(130, 440, "Bottom Left Player", "bottom")

        # Define the buttons
        buttons = [
            tk.Button(self.game_area, text="Call/Check", command=lambda: self.send_player_action("call"), bg="#555555", fg="#FFFFFF",
                      font=("Cambria", 12), relief="flat", height=2, width=10),
            tk.Button(self.game_area, text="Raise", command=lambda: self.send_player_action("raise"), bg="#555555", fg="#FFFFFF",
                      font=("Cambria", 12), relief="flat", height=2, width=10),
            tk.Button(self.game_area, text="Fold", command=lambda: self.send_player_action("fold"), bg="#555555", fg="#FFFFFF",
                      font=("Cambria", 12), relief="flat", height=2, width=10),
        ]

        for i, button in enumerate(buttons):
            button.place(relx=0.9, rely=0.2 * (2 * i + 5) / len(buttons), anchor='center')


    def network_loop(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('localhost', 12345))  # Connect to the server
            while True:
                data = s.recv(1024)
                if not data:
                    break  # Server has closed the connection
                self.process_server_message(data)

    def process_server_message(self, data):
        # Update game state and GUI based on the message received from the server
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

    def place_player(self, x, y, name, position):
        # Create a frame to hold the player components
        player_frame = tk.Frame(self.game_canvas, bg="#228B22")

        # Add profile picture
        profile_photo = Image.open("Images/default.png")
        profile_photo = profile_photo.resize((50, 50))
        profile_photo = ImageTk.PhotoImage(profile_photo)
        profile_label = tk.Label(player_frame, image=profile_photo, bg="#228B22")
        profile_label.photo = profile_photo  # keep a reference to avoid garbage collection
        profile_label.pack()

        # Add name label
        name_label = tk.Label(player_frame, text=name, bg="#228B22", fg="#FFFFFF")
        name_label.pack()

        # Add card images
        card1_photo = Image.open("Images/Cards/black_joker.png")
        card1_photo = card1_photo.resize((60, 90))
        card1_photo = ImageTk.PhotoImage(card1_photo)
        card1_label = tk.Label(player_frame, image=card1_photo, bg="#228B22")
        card1_label.photo = card1_photo  # keep a reference to avoid garbage collection
        card1_label.pack(side="left", padx=2)

        card2_photo = Image.open("Images/Cards/black_joker.png")
        card2_photo = card2_photo.resize((60, 90))
        card2_photo = ImageTk.PhotoImage(card2_photo)
        card2_label = tk.Label(player_frame, image=card2_photo, bg="#228B22")
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


if __name__ == "__main__":
    app = GameGUI(None, 2, None)
    app.mainloop()
