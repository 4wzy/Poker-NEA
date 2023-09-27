import string
import tkinter as tk
from tkinter import font as tkfont
from logic.database_interaction import DatabaseInteraction
from tkinter import messagebox
import json
from datetime import datetime

# To do:
# Handle joining and creating lobbies properly
# The join command should take in a user_id, and a lobby_name, and should open a new GUI for the player joining

class LobbyBrowser(tk.Tk):
    def __init__(self, controller, user_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.controller = controller
        self.user_id = user_id
        self.database_interaction = DatabaseInteraction()
        self.username = self.database_interaction.get_username(self.user_id)

        # For the checkboxes to filter lobbies based on game options
        self.status_var = tk.StringVar(value="waiting")
        self.odds_var = tk.BooleanVar(value=True)

        self.title("Lobby Browser - AceAware Poker")
        self.configure(bg="#333333")

        container = tk.Frame(self, bg="#333333", bd=5)
        container.pack(side="top", fill="both", expand=True)
        container.config(highlightbackground="red", highlightthickness=2)

        title_label = tk.Label(container, text="Lobby Browser", font=tkfont.Font(family="Cambria", size=18),
                               fg="#FFD700", bg="#333333", padx=20)
        title_label.grid(row=0, column=0, columnspan=2, sticky="w")

        # Checkbuttons for filters
        filter_frame = tk.Frame(container, bg="#333333")
        filter_frame.grid(row=1, column=0, columnspan=2, sticky="ew")

        status_checkbutton = tk.Checkbutton(filter_frame, text="Show Lobbies In Progress", variable=self.status_var,
                                            onvalue="in_progress", offvalue="waiting", bg="#333333",
                                            selectcolor="grey", fg="white", command=self.refresh_lobby_list)
        status_checkbutton.pack(side="left")

        odds_checkbutton = tk.Checkbutton(filter_frame, text="Show Odds", variable=self.odds_var, bg="#333333",
                                          selectcolor="grey", fg="white", command=self.refresh_lobby_list)
        odds_checkbutton.pack(side="left")

        # Setting up a place for each lobby card to go
        self.lobby_container_canvas = tk.Canvas(container, bg="#555555")
        self.lobby_container_canvas.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        self.lobby_container_frame = tk.Frame(self.lobby_container_canvas, bg="#555555")
        self.lobby_container_canvas.create_window((0, 0), window=self.lobby_container_frame, anchor="nw")

        scrollbar = tk.Scrollbar(container, orient="vertical", command=self.lobby_container_canvas.yview)
        scrollbar.grid(row=2, column=1, sticky="ns")
        self.lobby_container_canvas.config(yscrollcommand=scrollbar.set)
        self.lobby_container_canvas.yview_moveto(0)

        self.lobby_container_frame.bind("<Configure>", lambda e: self.lobby_container_canvas.configure(
            scrollregion=self.lobby_container_canvas.bbox("all")))

        button_frame = tk.Frame(container, bg="#333333")
        button_frame.grid(row=3, column=0, columnspan=2, sticky="ew")

        create_lobby_button = tk.Button(button_frame, text="Create Lobby", font=tkfont.Font(family="Cambria", size=16),
                                        fg="#FFFFFF", bg="#444444", bd=0, padx=20, pady=10, borderwidth=1,
                                        command=self.open_create_lobby_window)

        create_lobby_button.pack(side="left", fill="x", expand=True)

        refresh_button = tk.Button(button_frame, text="Refresh", font=tkfont.Font(family="Cambria", size=16),
                                   fg="#FFFFFF", bg="#444444", bd=0, padx=20, pady=10, borderwidth=1,
                                   command=self.refresh_lobby_list)
        refresh_button.pack(side="left", fill="x", expand=True)

        back_button = tk.Button(container, text="Back", font=tkfont.Font(family="Cambria", size=16), fg="#FFFFFF",
                                bg="#444444", bd=0, padx=20, pady=10, command=lambda: self.controller.open_main_menu(
                self.user_id))
        back_button.grid(row=4, column=0, columnspan=2, sticky="ew", pady=10, padx=10)

        self.lobby_container_frame.grid_columnconfigure(0, minsize=130)
        self.lobby_container_frame.grid_columnconfigure(1, minsize=130)
        self.lobby_container_frame.grid_columnconfigure(2, minsize=130)

        self.refresh_lobby_list()

    def open_create_lobby_window(self):
        CreateLobbyWindow(self.controller, self.user_id)

    def populate_lobby_list(self):
        print("Populating lobby list...")
        status_filter = self.status_var.get()
        odds_filter = self.odds_var.get()

        try:
            self.controller.network_manager.client_socket.sendall(
                json.dumps({"type": "get_all_lobbies", "status": status_filter, "odds": odds_filter}).encode('utf-8'))
            response = self.controller.network_manager.client_socket.recv(16384)
            # In case of an "expecting value" error, increase the number of bits being received
            # as the entire list of lobbies is not being received
            if not response:
                print("No response from server")
                return
            lobbies = json.loads(response.decode('utf-8'))
        except Exception as e:
            print(f"Error while populating lobby list: {e}")
            return

        print(f"Received lobbies: {lobbies}")

        row = 0
        col = 0
        for lobby in lobbies:
            lobby_card = LobbyCard(container=self.lobby_container_frame, lobby_info=lobby,
                                   join_command=lambda lobby=lobby: self.join_selected_lobby(lobby))

            lobby_card.grid(row=row, column=col, padx=10, pady=5, sticky="nsew")

            col += 1
            if col > 2:  # Move to the next row after every 3 cards
                col = 0
                row += 1

    def refresh_lobby_list(self):
        for widget in self.lobby_container_frame.winfo_children():
            widget.destroy()

        self.populate_lobby_list()
        self.lobby_container_canvas.yview_moveto(0)

    def join_selected_lobby(self, lobby_info):
        response_data = self.controller.join_lobby(self.user_id, lobby_info['name'])


class LobbyCard(tk.Frame):
    def __init__(self, container, lobby_info, join_command, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.join_command = join_command

        self.configure(bg="#444444", bd=2, relief="groove")

        # You can replace the labels with images or other widgets as needed
        lobby_name_label = tk.Label(self, text=lobby_info['name'], font=tkfont.Font(family="Cambria", size=12),
                                    fg="#FFFFFF", bg="#444444", wraplength=80)
        lobby_name_label.pack(side="top", fill="x", padx=5, pady=2)

        status_label = tk.Label(self, text=lobby_info['status'], font=tkfont.Font(family="Cambria", size=10),
                                fg="#FFFFFF", bg="#444444")
        status_label.pack(side="top", fill="x", padx=5, pady=2)

        player_count_label = tk.Label(self, text=f"{lobby_info['player_count']} players",
                                      font=tkfont.Font(family="Cambria", size=10), fg="#FFFFFF", bg="#444444")
        player_count_label.pack(side="top", fill="x", padx=5, pady=2)

        join_button = tk.Button(self, text="Join", command=self.join_command)
        join_button.pack(side="bottom", padx=5, pady=5)


class CreateLobbyWindow(tk.Toplevel):
    def __init__(self, controller, user_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.controller = controller
        self.user_id = user_id
        self.title("Create a Lobby - AceAware Poker")
        self.configure(bg="#333333")

        container = tk.Frame(self, bg="#333333", bd=5)
        container.pack(side="top", fill="both", expand=True)
        container.config(highlightbackground="red", highlightthickness=2)

        title_label = tk.Label(container, text="Create a Lobby", font=tkfont.Font(family="Cambria", size=18),
                               fg="#FFD700", bg="#333333", padx=20)
        title_label.grid(row=0, column=0, columnspan=2, sticky="w")

        # Lobby Name
        lobby_name_label = tk.Label(container, text="Lobby Name:", font=tkfont.Font(family="Cambria", size=16),
                                    fg="#FFFFFF", bg="#333333")
        lobby_name_label.grid(row=1, column=0, sticky="e")

        self.lobby_name_entry = tk.Entry(container, font=tkfont.Font(family="Cambria", size=16), width=32,
                                         fg="#FFFFFF", bg="#555555", insertbackground='white')
        self.lobby_name_entry.grid(row=1, column=1, sticky="w")

        # Show Odds
        self.show_odds_var = tk.BooleanVar(value=True)
        show_odds_checkbutton = tk.Checkbutton(container, text="Show Odds", variable=self.show_odds_var,
                                               font=tkfont.Font(family="Cambria", size=16), fg="#FFFFFF",
                                               bg="#333333", selectcolor="#444444")
        show_odds_checkbutton.grid(row=2, column=0, columnspan=2, sticky="w")

        # Buttons
        create_button = tk.Button(container, text="Create", font=tkfont.Font(family="Cambria", size=16),
                                  fg="#FFFFFF", bg="#444444", bd=0, padx=20, pady=10, command=self.create_lobby)
        create_button.grid(row=3, column=0, sticky="ew", pady=10, padx=10)

        cancel_button = tk.Button(container, text="Cancel", font=tkfont.Font(family="Cambria", size=16),
                                  fg="#FFFFFF", bg="#444444", bd=0, padx=20, pady=10, command=self.destroy)
        cancel_button.grid(row=3, column=1, sticky="ew", pady=10, padx=10)

    def create_lobby(self):
        lobby_name = self.lobby_name_entry.get()
        show_odds = self.show_odds_var.get()

        if not lobby_name or len(lobby_name) > 16:
            messagebox.showinfo("Error", "Please enter a valid lobby name (1-16 characters)")
            return

        lobby_data = {
            "type": "create_lobby",
            "host_user_id": self.user_id,
            "name": lobby_name,
            "show_odds": show_odds
        }

        try:
            response_data = self.controller.network_manager.send_message(lobby_data)
            if not response_data:
                messagebox.showinfo("Error", "No response from server")
                return

            # Checks for errors when creating a lobby and make sure that lobbies with duplicate names can not be created
            if 'error' in response_data and not response_data['success']:
                messagebox.showinfo("Error", response_data['error'])
                return
            self.controller.join_lobby(self.user_id, lobby_name)

        except Exception as e:
            print(f"Error while creating lobby: {e}")
            messagebox.showinfo("Error", "An error occurred while creating the lobby")

