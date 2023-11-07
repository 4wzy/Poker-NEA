import tkinter as tk
from tkinter import font as tkfont
from PIL import Image, ImageTk, ImageDraw


class UserProfile(tk.Tk):
    def __init__(self, controller, user_id, own_profile, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.controller = controller
        self.user_id = user_id
        self.own_profile = own_profile  # Boolean flag indicating if the profile belongs to the current user
        self.title("User Profile")
        self.configure(bg="#333333")

        self.statistics = self.controller.network_manager.send_message({
            "type": "get_user_statistics",
            "user_id": self.user_id
        })

        self.create_widgets()

    def create_widgets(self):
        # Profile picture
        profile_pic_size = (150, 150)
        self.image = Image.open("gui/Images/dog.png")  # Replace with actual path to the profile picture
        self.image = self.image.resize(profile_pic_size)

        # Create a mask for the circular profile picture
        mask = Image.new('L', profile_pic_size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + profile_pic_size, fill=255)

        # Create circular image
        circular_image = Image.new('RGBA', profile_pic_size, (0, 0, 0, 0))
        circular_image.paste(self.image, (0, 0), mask)

        # Convert to a format Tkinter can use
        self.profile_pic_image = ImageTk.PhotoImage(circular_image)

        # Create a Canvas widget to display the circular profile picture
        profile_pic_canvas = tk.Canvas(self, width=profile_pic_size[0], height=profile_pic_size[1], bg="#333333", bd=0,
                                       highlightthickness=0)
        profile_pic_canvas.grid(row=0, column=0, padx=10, pady=10)

        # Add the image to the Canvas
        profile_pic_canvas.create_image(profile_pic_size[0] // 2, profile_pic_size[1] // 2,
                                        image=self.profile_pic_image)

        self.username = self.controller.network_manager.send_message({
            "type": "get_username",
            "user_id": self.user_id
        })

        self.username_label = tk.Label(self, text=self.username, font=tkfont.Font(family="Cambria", size=24),
                                       fg="#F56476", bg="#333333")
        self.username_label.grid(row=0, column=1, padx=10, pady=10, sticky="W")

        if self.own_profile:
            edit_pic_button = tk.Button(self, text="Edit Picture", command=self.edit_profile_picture)
            edit_pic_button.grid(row=0, column=2, padx=10, pady=10)

            edit_name_button = tk.Button(self, text="Edit Name", command=self.edit_username)
            edit_name_button.grid(row=0, column=3, padx=10, pady=10)

        # Statistics display
        stats_frame = tk.Frame(self, bg="#555555", padx=10, pady=10)
        stats_frame.grid(row=1, column=0, columnspan=4, sticky="EW")

        games_played_label = tk.Label(stats_frame, text=f"Games Played: {self.statistics['games_played']}",
                                      bg="#555555", fg="#FFFFFF")
        games_played_label.pack(side="top", fill="x")

        games_won_label = tk.Label(stats_frame, text=f"Games Won: {self.statistics['games_won']}",
                                   bg="#555555", fg="#FFFFFF")
        games_won_label.pack(side="top", fill="x")

        total_play_time_label = tk.Label(stats_frame, text=f"Total Play Time: {self.statistics['total_play_time']}",
                                         bg="#555555", fg="#FFFFFF")
        total_play_time_label.pack(side="top", fill="x")

        # Rgscore and other details
        details_frame = tk.Frame(self, bg="#555555", padx=10, pady=10)
        details_frame.grid(row=2, column=0, columnspan=4, sticky="EW")

        rgscore_label = tk.Label(details_frame, text=f"RG Score: {self.statistics['rgscore']}",
                                 bg="#555555", fg="#FFFFFF")
        rgscore_label.pack(side="top", fill="x")

        streak_label = tk.Label(details_frame, text=f"Streak: {self.statistics['streak']}",
                                bg="#555555", fg="#FFFFFF")
        streak_label.pack(side="top", fill="x")

        aggressiveness_score_label = tk.Label(details_frame,
                                              text=f"Average Aggressiveness Score: {self.statistics['average_aggressiveness_score']}",
                                              bg="#555555", fg="#FFFFFF")
        aggressiveness_score_label.pack(side="top", fill="x")

        conservativeness_score_label = tk.Label(details_frame,
                                                text=f"Average Conservativeness Score: {self.statistics['average_conservativeness_score']}",
                                                bg="#555555", fg="#FFFFFF")
        conservativeness_score_label.pack(side="top", fill="x")

    def edit_profile_picture(self):
        # This method should handle changing the profile picture
        pass

    def edit_username(self):
        # This method should handle changing the username
        pass

# ... [more methods as needed]
