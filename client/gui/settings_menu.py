import tkinter as tk
from tkinter import font as tkfont
from tkinter import messagebox
import json
from tkinter import ttk


class SettingsMenu(tk.Tk):
    def __init__(self, controller, user_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.controller = controller
        self.user_id = user_id
        print(f"USING LOBBY BROWSER WITH USER_ID: {self.user_id}")
        # Get any required data from the server
        self.username = self.controller.network_manager.send_message({"type": "get_username", "user_id": self.user_id})
        self.user_chips = self.controller.network_manager.send_message({"type": "request_user_chips", "user_id":
            self.user_id})

        self.title("Settings - AceAware Poker")
        self.configure(bg="#333333")

        # Set up the GUI widgets
        container = tk.Frame(self, bg="#333333", bd=5)
        container.pack(side="top", fill="both", expand=True)
        container.config(highlightbackground="red", highlightthickness=2)

        title_label = tk.Label(container, text="Settings", font=tkfont.Font(family="Cambria", size=18),
                               fg="#FFD700", bg="#333333", padx=20, pady=10)
        title_label.grid(row=0, column=0)

        self.user_chips_label = tk.Label(container, text=f"Chips: {self.user_chips}",
                                    font=tkfont.Font(family="Cambria", size=16),
                                    fg="#FFFFFF", bg="#444444", padx=10, pady=15)
        self.user_chips_label.grid(row=1, column=0)


        reset_chips_button = tk.Button(container, text="Reset chips to 500", font=tkfont.Font(family="Cambria", size=16),
                                        fg="#FFFFFF", bg="#444444", bd=0, padx=20, pady=20, borderwidth=1,
                                        command=self.reset_chips)
        reset_chips_button.grid(row=2, column=0)

        back_button = tk.Button(container, text="Back", font=tkfont.Font(family="Cambria", size=16), fg="#FFFFFF",
                                bg="#444444", bd=0, padx=20, pady=10, command=lambda: self.controller.open_main_menu(
                self.user_id))
        back_button.grid(row=3, column=0, sticky="ew", pady=10, padx=10)

    # Allow the user to reset their chips back to the default value
    def reset_chips(self):
        response = self.controller.network_manager.send_message({"type": "update_chip_balance_for_user", "user_id":
            self.user_id, "amount": 500})

        if response['success']:
            self.user_chips = response['balance']
            self.user_chips_label.config(text=f"Chips: {self.user_chips}")