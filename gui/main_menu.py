import tkinter as tk
from tkinter import font as tkfont
from PIL import Image, ImageDraw, ImageTk
from logic.database_interaction import DatabaseInteraction


class MainMenu(tk.Tk):
    def __init__(self, controller, user_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.controller = controller
        self.user_id = user_id
        self.database_interaction = DatabaseInteraction()
        self.username = self.database_interaction.get_username(self.user_id)

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

        profile_pic = tk.Canvas(user_banner, width=105, height=50, bg="#555555", bd=0, highlightthickness=0)
        profile_pic.pack(side="right")
        profile_pic.create_oval(54, 4, 96, 46, outline="red", fill="#777777")

        self.image = Image.open("gui/Images/dog.png")
        self.image = self.image.resize((40, 40))

        mask = Image.new('L', (40, 40), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, 40, 40), fill=255)

        self.circular_image = Image.new('RGBA', (40, 40), (0, 0, 0, 0))
        self.circular_image.paste(self.image, (0, 0), mask)
        self.profile_pic_image = ImageTk.PhotoImage(self.circular_image)

        profile_pic.create_image(75, 25, image=self.profile_pic_image)

        left_buttons_frame = tk.Frame(container, bg="#333333", width=200, padx=20)
        left_buttons_frame.grid(row=1, column=0, rowspan=3, sticky="ns")
        container.columnconfigure(0, minsize=200)

        play_button = tk.Button(left_buttons_frame, text="Play", font=tkfont.Font(family="Cambria", size=16),
                                fg="#FFFFFF", bg="#444444", bd=0, padx=20, pady=10, width=50, borderwidth=1,
                                command=lambda: self.controller.open_lobby_browser(self.user_id))
        play_button.pack(side="top", fill="x", pady=5)

        hall_of_fame_button = tk.Button(left_buttons_frame, text="Hall of Fame",
                                        font=tkfont.Font(family="Cambria", size=16), fg="#FFFFFF", bg="#444444", bd=0,
                                        padx=20, pady=10, borderwidth=1)
        hall_of_fame_button.pack(side="top", fill="x", pady=5)

        settings_button = tk.Button(left_buttons_frame, text="Settings", font=tkfont.Font(family="Cambria", size=16),
                                    fg="#FFFFFF", bg="#444444", bd=0, padx=20, pady=10, borderwidth=1)
        settings_button.pack(side="top", fill="x", pady=5)

        self.logo = Image.open("gui/Images/logo.png")
        self.logo = self.logo.resize((200, 200))
        self.logo = ImageTk.PhotoImage(self.logo)

        logo_label = tk.Label(container, image=self.logo, bg="#333333")
        logo_label.grid(row=1, column=3, rowspan=3, sticky="nse")
        logo_label.image = self.logo

        how_to_play_button = tk.Button(container, text="How to Play", font=tkfont.Font(family="Cambria", size=16),
                                       fg="#FFFFFF", bg="#444444", bd=0, padx=40, pady=10, borderwidth=1)
        how_to_play_button.grid(row=4, column=0, columnspan=4, sticky="ew", pady=5)

        responsible_gambling_button = tk.Button(container, text="Responsible Gambling",
                                                font=tkfont.Font(family="Cambria", size=16), fg="#FFFFFF", bg="#444444",
                                                bd=0, padx=20, pady=10, borderwidth=1)
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
