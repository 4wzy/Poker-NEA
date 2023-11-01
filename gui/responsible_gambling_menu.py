import tkinter as tk
from tkinter import font as tkfont
from tkinter import messagebox
import json
from tkinter import ttk


class ResponsibleGamblingMenu(tk.Tk):
    def __init__(self, controller, user_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.controller = controller
        self.user_id = user_id
        self.title("Responsible Gambling")
        self.configure(bg="#333333")
        self.daily_game_limit = self.controller.network_manager.send_message(
            {'type': 'get_daily_game_limit', "user_id": self.user_id})

        self.user_id = user_id
        self.daily_game_limit = self.daily_game_limit

        title_label = tk.Label(self, text="Responsible Gambling", font=tkfont.Font(family="Cambria", size=20),
                               fg="#FFD700", bg="#333333")
        title_label.grid(row=0, column=0, columnspan=2, pady=10)

        self.current_limit_label = tk.Label(self, text=f"Current Daily Game Limit: {self.daily_game_limit}",
                                            font=tkfont.Font(family="Cambria", size=16), fg="#FFFFFF", bg="#333333")
        self.current_limit_label.grid(row=1, column=0, columnspan=2, pady=10)

        self.new_limit_var = tk.StringVar(self)
        self.new_limit_var.set("Set New Limit")
        new_limit_entry = tk.Entry(self, textvariable=self.new_limit_var, font=tkfont.Font(family="Cambria", size=16),
                                   fg="#333333", bg="#FFFFFF", width=15)
        new_limit_entry.grid(row=2, column=0, columnspan=2, pady=10)

        set_limit_button = tk.Button(self, text="Set Limit", font=tkfont.Font(family="Cambria", size=16), fg="#FFFFFF",
                                     bg="#444444", bd=0, padx=20, pady=10, command=self.set_limit)
        set_limit_button.grid(row=3, column=0, columnspan=2, pady=10)

        info_label = tk.Label(self, text="If you or someone you know is struggling with gambling, please contact:",
                              font=tkfont.Font(family="Cambria", size=14), fg="#FFFFFF", bg="#333333", wraplength=450,
                              justify="left")
        info_label.grid(row=4, column=0, columnspan=2, pady=10)

        help_info = [
            ("Gambling Helpline", "0808 8020 133", "www.gamblinghelpline.com"),
            ("BeGambleAware", "0808 8020 133", "www.begambleaware.org"),
            ("Gamblers Anonymous", "020 7384 3040", "www.gamblersanonymous.org.uk"),
        ]

        for i, (name, phone, website) in enumerate(help_info, start=5):
            name_label = tk.Label(self, text=name, font=tkfont.Font(family="Cambria", size=14), fg="#FFD700",
                                  bg="#333333")
            name_label.grid(row=i, column=0, padx=20, sticky='w')

            phone_label = tk.Label(self, text=phone, font=tkfont.Font(family="Cambria", size=14), fg="#FFFFFF",
                                   bg="#333333")
            phone_label.grid(row=i, column=1, padx=20, sticky='w')

            website_label = tk.Label(self, text=website, font=tkfont.Font(family="Cambria", size=14), fg="#FFFFFF",
                                     bg="#333333")
            website_label.grid(row=i, column=2, padx=20, sticky='e')

        back_button = tk.Button(self, text="Back", font=tkfont.Font(family="Cambria", size=16), fg="#FFFFFF",
                                bg="#444444", bd=0, padx=20, pady=10,
                                command=lambda: self.controller.open_main_menu(
                                    self.user_id))
        back_button.grid(row=i + 1, column=0, columnspan=2, pady=20)

    def set_limit(self):
        new_limit = self.new_limit_var.get()
        try:
            new_limit = int(new_limit)
            if new_limit <= 0 or new_limit >= 500:
                raise ValueError
        except ValueError:
            tk.messagebox.showerror("Invalid Input", "Please enter a valid number between 1 and 499.")
            return

        # Update the daily game limit in the database (you need to implement this method)
        self.update_daily_game_limit(new_limit)

        # Update the label showing the current limit
        self.current_limit_label.config(text=f"Current Daily Game Limit: {new_limit}")

        tk.messagebox.showinfo("Limit Updated", "Your daily game limit has been updated.")

    def update_daily_game_limit(self, new_limit):
        self.daily_game_limit = self.controller.network_manager.send_message({'type': 'get_daily_game_limit', "user_id": self.user_id, "new_limit": new_limit})