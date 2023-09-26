import tkinter as tk
from tkinter import font as tkfont
from logic.database_interaction import DatabaseInteraction
from tkinter import messagebox
import json
from datetime import datetime


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
                                            selectcolor="grey", fg="white")
        status_checkbutton.pack(side="left")

        odds_checkbutton = tk.Checkbutton(filter_frame, text="Show Odds", variable=self.odds_var, bg="#333333",
                                          selectcolor="grey", fg="white")
        odds_checkbutton.pack(side="left")

        # Set up the listbox which displays the available lobbies
        self.lobby_listbox = tk.Listbox(container, bg="#555555", fg="#FFFFFF", font=tkfont.Font(family="Cambria", size=12),
                                   selectbackground="#444444")
        self.lobby_listbox.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        scrollbar = tk.Scrollbar(container, orient="vertical", command=self.lobby_listbox.yview)
        scrollbar.grid(row=2, column=1, sticky="ns")
        self.lobby_listbox.config(yscrollcommand=scrollbar.set)

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

        join_lobby_button = tk.Button(button_frame, text="Join Lobby", font=tkfont.Font(family="Cambria", size=16),
                                      fg="#FFFFFF", bg="#444444", bd=0, padx=20, pady=10, borderwidth=1,
                                      command=self.join_selected_lobby)
        join_lobby_button.pack(side="left", fill="x", expand=True)

        back_button = tk.Button(container, text="Back", font=tkfont.Font(family="Cambria", size=16), fg="#FFFFFF",
                                bg="#444444", bd=0, padx=20, pady=10, command=lambda: self.controller.open_main_menu(
                self.user_id))
        back_button.grid(row=4, column=0, columnspan=2, sticky="ew", pady=10, padx=10)

        self.refresh_lobby_list()

    def open_create_lobby_window(self):
        CreateLobbyWindow(self.controller, self.user_id)

    def populate_lobby_list(self):
        print("Populating lobby list...")
        status_filter = self.status_var.get()
        odds_filter = self.odds_var.get()

        try:
            self.controller.client_socket.sendall(
                json.dumps({"type": "get_all_lobbies", "status": status_filter, "odds": odds_filter}).encode('utf-8'))
            response = self.controller.client_socket.recv(1024)
            if not response:
                print("No response from server")
                return
            lobbies = json.loads(response.decode('utf-8'))
        except Exception as e:
            print(f"Error while populating lobby list: {e}")
            return

        print(f"Received lobbies: {lobbies}")

        for lobby in lobbies:
            i = 4
            lobby[i] = datetime.strptime(lobby[i], '%Y-%m-%d %H:%M:%S')

            # Or leave them as strings and insert into the listbox
            self.lobby_listbox.insert(tk.END, lobby)

    def refresh_lobby_list(self):
        self.lobby_listbox.delete(0, tk.END)
        self.populate_lobby_list()

    def join_selected_lobby(self):
        selected_index = self.lobby_listbox.curselection()
        if not selected_index:
            messagebox.showinfo("Error", "Please select a lobby to join")
            return
        selected_lobby = self.lobby_listbox.get(selected_index)
        self.controller.join_lobby(self.user_id, selected_lobby)


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

        if not lobby_name or len(lobby_name) > 32:
            messagebox.showinfo("Error", "Please enter a valid lobby name (1-32 characters)")
            return

        lobby_data = {
            "type": "create_lobby",
            "host_user_id": self.user_id,
            "name": lobby_name,
            "show_odds": show_odds
        }

        self.controller.client_socket.sendall(json.dumps(lobby_data).encode('utf-8'))

        self.destroy()

