import tkinter as tk
from tkinter import font as tkfont
from PIL import Image, ImageDraw, ImageTk


class MainMenu(tk.Tk):
    def __init__(self, controller, user_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.controller = controller
        self.user_id = user_id
        print(f"USING MAIN MENU WITH USER_ID: {self.user_id}")
        self.controller.network_manager.reset_connection()
        self.username = self.controller.network_manager.send_message({"type": "get_username", "user_id": self.user_id})
        self.rg_score = self.controller.network_manager.send_message({"type": "update_rg_score", "user_id":
            self.user_id})
        print(self.rg_score)
        self.games_played_today = self.controller.network_manager.send_message(
            {"type": "get_and_check_to_reset_daily_games_played", "user_id": self.user_id})
        print(f"Sent get_and_check_daily_games_played request with id {self.user_id}")

        self.title("AceAware Poker")

        self.configure(bg="#333333")

        container = tk.Frame(self, bg="#333333", bd=5)
        container.pack(side="top", fill="both", expand=True)

        container.config(highlightbackground="red", highlightthickness=2)

        title_label = tk.Label(container, text="AceAware Poker", font=tkfont.Font(family="Cambria", size=18),
                               fg="#FFD700", bg="#333333", padx=20)
        title_label.grid(row=0, column=0, columnspan=3, sticky="w")

        user_banner = tk.Frame(container, bg="#555555")
        user_banner.grid(row=0, column=3, sticky="ne")

        username_label = tk.Label(user_banner, text=f"{self.username[0].upper() + self.username[1:].lower()}",
                                  font=tkfont.Font(
                                      family="Cambria",
                                      size=24),
                                  fg="#F56476", bg="#555555")
        username_label.pack(side="left")

        self.profile_pic = tk.Canvas(user_banner, width=105, height=50, bg="#555555", bd=0, highlightthickness=0)
        self.profile_pic.pack(side="right")
        self.profile_pic.create_oval(54, 4, 96, 46, outline="red", fill="#777777")

        self.profile_picture = self.controller.network_manager.send_message({"type": "get_user_profile_picture",
                                                                             "user_id": self.user_id})
        self.image = Image.open(f"gui/Images/Pfps/{self.profile_picture}")
        self.image = self.image.resize((40, 40))

        mask = Image.new('L', (40, 40), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, 40, 40), fill=255)

        self.circular_image = Image.new('RGBA', (40, 40), (0, 0, 0, 0))
        self.circular_image.paste(self.image, (0, 0), mask)
        self.profile_pic_image = ImageTk.PhotoImage(self.circular_image)

        # Add this line here to store the image ID
        self.profile_pic_id = self.profile_pic.create_image(75, 25, image=self.profile_pic_image)

        self.profile_pic.bind("<Button-1>", lambda event: self.controller.open_user_profile(self.user_id,
                                                                                            update_previous_menu=True))

        left_buttons_frame = tk.Frame(container, bg="#333333", width=200, padx=20)
        left_buttons_frame.grid(row=1, column=0, rowspan=3, sticky="ns")
        container.columnconfigure(0, minsize=200)

        play_button = tk.Button(left_buttons_frame, text="Play", font=tkfont.Font(family="Cambria", size=16),
                                fg="#FFFFFF", bg="#444444", bd=0, padx=20, pady=10, width=50, borderwidth=1,
                                command=lambda: self.controller.open_lobby_browser(self.user_id,
                                                                                   self.games_played_today))
        play_button.pack(side="top", fill="x", pady=5)

        hall_of_fame_button = tk.Button(left_buttons_frame, text="Hall of Fame",
                                        font=tkfont.Font(family="Cambria", size=16), fg="#FFFFFF", bg="#444444", bd=0,
                                        padx=20, pady=10, borderwidth=1,
                                        command=lambda: self.controller.open_hall_of_fame(self.user_id))
        hall_of_fame_button.pack(side="top", fill="x", pady=5)

        settings_button = tk.Button(left_buttons_frame, text="Settings", font=tkfont.Font(family="Cambria", size=16),
                                    fg="#FFFFFF", bg="#444444", bd=0, padx=20, pady=10, borderwidth=1,
                                    command=lambda: self.controller.open_settings(self.user_id))
        settings_button.pack(side="top", fill="x", pady=5)

        self.logo = Image.open("gui/Images/logo.png")
        self.logo = self.logo.resize((200, 200))
        self.logo = ImageTk.PhotoImage(self.logo)

        logo_label = tk.Label(container, image=self.logo, bg="#333333")
        logo_label.grid(row=1, column=3, rowspan=3, sticky="nse")
        logo_label.image = self.logo

        how_to_play_button = tk.Button(container, text="How to Play", font=tkfont.Font(family="Cambria", size=16),
                                       fg="#FFFFFF", bg="#444444", bd=0, padx=40, pady=10, borderwidth=1,
                                       command=lambda: self.controller.open_how_to_play(self.user_id))
        how_to_play_button.grid(row=4, column=0, columnspan=4, sticky="ew", pady=5)

        responsible_gambling_button = tk.Button(container, text="Responsible Gambling",
                                                font=tkfont.Font(family="Cambria", size=16), fg="#FFFFFF", bg="#444444",
                                                bd=0, padx=20, pady=10, borderwidth=1,
                                                command=lambda: self.controller.open_responsible_gambling_menu(
                                                    self.user_id))
        responsible_gambling_button.grid(row=5, column=0, columnspan=4, sticky="ew", pady=5)

        text_frame = tk.Frame(container, bg="#555555", padx=10, pady=5)
        text_frame.grid(row=6, column=0, columnspan=4, sticky="ew", pady=10)

        placeholder_text = tk.Label(text_frame, text="This game has been created to encourage users to gamble "
                                                     "responsibly. Please check out the Responsible Gambling section "
                                                     "to learn more!", font=tkfont.Font(family="Cambria", size=12),
                                    fg="#FFFFFF", bg="#555555")
        placeholder_text.pack()

        quit_button = tk.Button(container, text="Quit", font=tkfont.Font(family="Cambria", size=16), fg="#FFFFFF",
                                bg="#444444", bd=0, padx=20, pady=10, command=self.destroy)
        quit_button.grid(row=7, column=3, sticky="se", pady=10, padx=10)

    def update_profile_picture(self, new_pic_name):
        profile_pic_path = f"gui/Images/Pfps/{new_pic_name}"
        new_image = Image.open(profile_pic_path)
        new_image = new_image.resize((40, 40))

        mask = Image.new('L', (40, 40), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, 40, 40), fill=255)

        circular_image = Image.new('RGBA', (40, 40), (0, 0, 0, 0))
        circular_image.paste(new_image, (0, 0), mask)
        new_profile_pic_image = ImageTk.PhotoImage(circular_image)

        # Assuming 'self.profile_pic' is the Canvas for the profile picture, and the image ID is stored in 'self.profile_pic_id'
        self.profile_pic.itemconfig(self.profile_pic_id, image=new_profile_pic_image)
        # Update the image reference to prevent garbage collection
        self.profile_pic_image = new_profile_pic_image
