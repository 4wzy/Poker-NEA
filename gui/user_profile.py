import tkinter as tk
from tkinter import font as tkfont
from PIL import Image, ImageTk, ImageDraw


class UserProfile(tk.Frame):
    def __init__(self, parent, controller, user_id, own_profile, previous_menu, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.controller = controller
        self.user_id = user_id
        self.previous_menu = previous_menu
        self.current_pic_name = self.controller.network_manager.send_message({"type": "get_user_profile_picture",
                                                                             "user_id": self.user_id})
        self.own_profile = own_profile  # Boolean flag indicating if the profile belongs to the current user
        self.configure(bg="#333333")

        self.statistics = self.controller.network_manager.send_message({
            "type": "get_user_statistics",
            "user_id": self.user_id
        })

        self.create_widgets()
        self.pack(fill="both", expand=True)

    def create_widgets(self):
        # Profile picture
        profile_pic_size = (150, 150)
        self.image = Image.open(f"gui/Images/Pfps/{self.current_pic_name}")
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

        # Store the canvas reference
        self.profile_pic_canvas = tk.Canvas(self, width=profile_pic_size[0], height=profile_pic_size[1], bg="#333333",
                                            bd=0,
                                            highlightthickness=0)
        self.profile_pic_canvas.grid(row=0, column=0, padx=10, pady=10)

        # Add the image to the Canvas and store the image ID
        self.profile_pic_id = self.profile_pic_canvas.create_image(profile_pic_size[0] // 2, profile_pic_size[1] // 2,
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
        self.profile_pic_selection_window = SelectProfilePic(self, self.on_profile_pic_selected, self.current_pic_name)

    def on_profile_pic_selected(self, pic_name):
        # Update the profile picture display in the UI as before...

        # Send message to network manager to update the profile picture in the database
        self.controller.network_manager.send_message({
            "type": "set_user_profile_picture",
            "user_id": self.user_id,
            "new_profile_picture": pic_name
        })
        # Update UI with new profile picture
        self.update_profile_picture_display(pic_name)
        if self.previous_menu:
            self.previous_menu.update_profile_picture(pic_name)

    def update_profile_picture_display(self, pic_name):
        image_path = f"gui/Images/Pfps/{pic_name}"
        self.image = Image.open(image_path)
        profile_pic_size = (150, 150)
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

        # Update the canvas image
        self.profile_pic_canvas.itemconfig(self.profile_pic_id, image=self.profile_pic_image)

        # Update the current picture name
        self.current_pic_name = pic_name

    def edit_username(self):
        # This method should handle changing the username
        pass

class SelectProfilePic(tk.Toplevel):
    def __init__(self, parent, callback, current_pic_name):
        super().__init__(parent)
        self.callback = callback
        self.title('Select Profile Picture')
        self.geometry('400x400')  # Adjust as needed
        self.configure(bg="#333333")
        self.profile_pics = [
            "cat.png", "default.png", "elephant.png", "giraffe.png",
            "hedgehog.png", "llama.png", "octopus.png", "tiger.png"
        ]
        self.current_pic_name = current_pic_name
        self.create_widgets()

    def create_widgets(self):
        # Create two frames, each for a row of profile pics
        row1 = tk.Frame(self, bg="#333333")
        row1.pack(side='top', fill='x', pady=10)

        row2 = tk.Frame(self, bg="#333333")
        row2.pack(side='top', fill='x', pady=10)

        # Add picture buttons to the rows
        for i, pic_name in enumerate(self.profile_pics):
            target_row = row1 if i < 4 else row2
            self.add_pic_button(target_row, pic_name)

        # Current profile picture display
        current_pic_frame = tk.Frame(self, bg="#555555")
        current_pic_frame.pack(side='bottom', fill='x', pady=10)

        label = tk.Label(current_pic_frame, text="Current Picture", fg="#FFFFFF", bg="#555555")
        label.pack(side='top')

        img = Image.open(f"gui/Images/Pfps/{self.current_pic_name}")
        img.thumbnail((100, 100))  # Creates a thumbnail of the image
        current_photo = ImageTk.PhotoImage(img)

        current_pic_label = tk.Label(current_pic_frame, image=current_photo, bg="#555555")
        current_pic_label.image = current_photo  # Keep a reference
        current_pic_label.pack(side='top', pady=10)

    def add_pic_button(self, parent, pic_name):
        img = Image.open(f"gui/Images/Pfps/{pic_name}")
        img.thumbnail((80, 80))  # Creates a thumbnail of the image
        photo = ImageTk.PhotoImage(img)

        button = tk.Button(parent, image=photo, command=lambda p=pic_name: self.set_profile_picture(p), bg="#333333", bd=0)
        button.image = photo  # Keep a reference so it does not get garbage collected
        button.pack(side='left', padx=10, pady=5)

    def set_profile_picture(self, pic_name):
        self.callback(pic_name)
        self.destroy()