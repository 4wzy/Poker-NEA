import tkinter as tk
from tkinter import font as tkfont
from PIL import Image, ImageDraw, ImageTk
from client.gui.user_profile import ProfilePictureManager

class HallOfFame(tk.Tk):
    def __init__(self, controller, user_id):
        super().__init__()
        self.controller = controller
        self.user_id = user_id
        self.title("Hall of Fame")
        self.configure(bg="#333333")
        self.geometry('800x600')
        self.player_banners = {}  # Dictionary to store player banners
        self.profile_picture_manager = ProfilePictureManager(self.controller)

        top_frame = tk.Frame(self, bg="#333333")
        top_frame.pack(pady=10, fill="x")

        back_button = tk.Button(top_frame, text="Back", font=tkfont.Font(family="Cambria", size=16), fg="#FFFFFF",
                                bg="#444444", bd=0, padx=20, pady=10, command=lambda: self.controller.open_main_menu(
                self.user_id))
        back_button.pack(side="left", padx=10)

        title_label = tk.Label(top_frame, text="Hall of Fame", font=tkfont.Font(family="Cambria", size=20),
                               fg="#FFD700",
                               bg="#333333")
        title_label.pack(side="left", expand=True)

        # Dropdown for sorting attributes
        self.sort_var = tk.StringVar(self)
        self.sort_var.set("Select Attribute")
        sorting_options = ["RGScore", "Chips", "Aggressiveness Score", "Conservativeness Score", "Games won"]
        dropdown = tk.OptionMenu(top_frame, self.sort_var, *sorting_options, command=self.update_hall)
        dropdown.pack(side="right", padx=10)

        self.top_players_var = tk.StringVar(self)
        self.top_players_var.set("10")
        top_players_options = ["5", "10", "20", "50", "100"]
        top_players_dropdown = tk.OptionMenu(top_frame, self.top_players_var, *top_players_options, command=self.update_hall)
        top_players_dropdown.pack(side="right", padx=10)

        self.canvas = tk.Canvas(self, bg="#333333")
        scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scroll_frame = tk.Frame(self.canvas, bg="#333333")

        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.canvas_window = self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.scroll_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)

    def on_frame_configure(self, event):
        """Reset the scroll region to encompass the inner frame."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_canvas_configure(self, event):
        """Reset the width of the scroll frame to match the width of the canvas."""
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)

    def add_player_banner(self, player_name, profile_pic_path, attribute_value, user_id):
        banner = tk.Frame(self.scroll_frame, bg="#555555", pady=5)
        banner.pack(fill="x", pady=5, expand=True)

        # Circular profile picture
        profile_pic_canvas = tk.Canvas(banner, width=50, height=50, bg="#555555", bd=0, highlightthickness=0)
        profile_pic_canvas.pack(side="left", padx=10)

        image = Image.open(profile_pic_path)
        image = image.resize((40, 40))

        mask = Image.new('L', (40, 40), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, 40, 40), fill=255)

        circular_image = Image.new('RGBA', (40, 40), (0, 0, 0, 0))
        circular_image.paste(image, (0, 0), mask)
        profile_pic_image = ImageTk.PhotoImage(circular_image)

        profile_pic_canvas.create_image(25, 25, image=profile_pic_image)
        profile_pic_canvas.image = profile_pic_image

        profile_pic_canvas.bind("<Button-1>", lambda event: self.controller.open_user_profile(profile_user_id=user_id,
                                                                                         own_user_id=self.user_id,
                                                                                         update_previous_menu=True))

        profile_pic_id = profile_pic_canvas.create_image(25, 25, image=profile_pic_image, tags="profile_pic")

        # Player name (Left)
        name_label = tk.Label(banner, text=player_name, font=tkfont.Font(family="Cambria", size=16), fg="#F56476",
                              bg="#555555")
        name_label.pack(side="left", padx=20)

        # Attribute value (Right)
        attr_value_label = tk.Label(banner, text=attribute_value, font=tkfont.Font(family="Cambria", size=14),
                                    fg="#FFFFFF", bg="#555555")
        attr_value_label.pack(side="right", padx=20)

        self.player_banners[user_id] = {
            "banner": banner,
            "name_label": name_label,
            "profile_pic_canvas": profile_pic_canvas
        }

    def update_hall(self, *args):
        selected_attribute = self.sort_var.get()
        if selected_attribute == "Select Attribute":
            return
        limit = int(self.top_players_var.get())

        # Get players based on the selected attribute
        if selected_attribute == "Chips":
            players = self.controller.network_manager.send_message({"type": "get_top_players_by_chips", "limit": limit})
            if players is None:
                return
        else:
            attribute_mapping = {
                "RGScore": "rgscore",
                "Aggressiveness Score": "average_aggressiveness_score",
                "Conservativeness Score": "average_conservativeness_score",
                "Games won": "games_won"
            }
            players = self.controller.network_manager.send_message({
                "type": "get_top_players_by_attribute",
                "attribute": attribute_mapping[selected_attribute],
                "limit": limit
            })

            if players is None:
                print("No players found from hall of fame")
                return

        # Clear current player banners
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        # Add new player banners
        for player in players:
            user_id, username, profile_pic, attribute_value = player
            print(f"username: {username}, user_id: {user_id}")
            profile_pic_path = self.profile_picture_manager.check_and_fetch_profile_picture(user_id)
            if profile_pic_path:
                self.add_player_banner(username, profile_pic_path, f"{selected_attribute}: {attribute_value}", user_id)

    def get_profile_pic_path(self, user_id):
        # Placeholder method to return the profile picture path based on the user_id
        profile_picture_name = self.controller.network_manager.send_message({"type": "get_user_profile_picture",
                                                                             "user_id": user_id})
        return f"gui/Images/Pfps/{profile_picture_name}"

    def update_profile_picture(self, user_id, new_pic_name):
        if user_id in self.player_banners:
            profile_pic_canvas = self.player_banners[user_id]["profile_pic_canvas"]

            profile_pic_path = f"gui/Images/Pfps/{new_pic_name}"
            new_image = Image.open(profile_pic_path)
            new_image = new_image.resize((40, 40))

            mask = Image.new('L', (40, 40), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, 40, 40), fill=255)

            circular_image = Image.new('RGBA', (40, 40), (0, 0, 0, 0))
            circular_image.paste(new_image, (0, 0), mask)
            new_profile_pic_image = ImageTk.PhotoImage(circular_image)

            profile_pic_canvas.itemconfig("profile_pic", image=new_profile_pic_image)
            profile_pic_canvas.image = new_profile_pic_image

    def update_username(self, user_id, new_username):
        if user_id in self.player_banners:
            name_label = self.player_banners[user_id]["name_label"]
            name_label.config(text=new_username)

