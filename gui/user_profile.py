import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont
from PIL import Image, ImageTk, ImageDraw
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class UserProfile(tk.Frame):
    def __init__(self, parent, controller, profile_user_id, own_user_id, previous_menu, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.controller = controller
        self.profile_user_id = profile_user_id
        self.previous_menu = previous_menu
        self.current_pic_name = self.controller.network_manager.send_message({"type": "get_user_profile_picture",
                                                                              "user_id": self.profile_user_id})
        self.own_profile = self.profile_user_id == own_user_id  # Boolean flag indicating if the profile belongs to the current user
        self.configure(bg="#333333")

        self.statistics = self.controller.network_manager.send_message({
            "type": "get_user_statistics",
            "user_id": self.profile_user_id
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
            "user_id": self.profile_user_id
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

        # GUI features related to graph
        info_label = tk.Label(self, text="Select options to view graph", font=tkfont.Font(family="Cambria", size=14),
                              fg="#FFFFFF", bg="#333333")
        info_label.grid(row=4, column=0, padx=10, pady=10)

        self.create_recent_games_table()

        self.num_games_var = tk.StringVar()
        self.num_games_dropdown = ttk.Combobox(self, textvariable=self.num_games_var, state="readonly")
        self.num_games_dropdown['values'] = (5, 10, 20, 50, 100)
        self.num_games_dropdown.set(10)
        self.num_games_dropdown.grid(row=5, column=0, padx=10, pady=10)

        self.attribute_var = tk.StringVar()
        self.attribute_dropdown = ttk.Combobox(self, textvariable=self.attribute_var, state="readonly")
        self.attribute_dropdown['values'] = ("pos", "winnings", "aggressiveness_score", "conservativeness_score")
        self.attribute_dropdown.set("conservativeness_score")  # default value
        self.attribute_dropdown.grid(row=5, column=1, padx=10, pady=10)
        self.attribute_dropdown.bind("<<ComboboxSelected>>", self.on_attribute_selected)

    def on_attribute_selected(self, event):
        num_games = int(self.num_games_var.get())
        attribute = self.attribute_var.get()
        scores = self.controller.network_manager.send_message({
            "type": "get_attribute_from_user_games_played",
            "user_id": self.profile_user_id,
            "attribute": attribute,
            "num_games": num_games
        })
        self.display_graph(scores, attribute)

    def on_num_games_selected(self, event):
        num_games = int(self.num_games_var.get())
        attribute = "conservativeness_score"
        scores = self.controller.network_manager.send_message({
            "type": "get_attribute_from_user_games_played",
            "user_id": self.profile_user_id,
            "attribute": attribute,
            "num_games": num_games
        })
        self.display_graph(scores, attribute)

    def display_graph(self, scores, attribute):
        # If there are no scores or all scores are zero, display error message
        # I did this because there is no point in rendering an empty graph
        if not scores or all(score == 0 for score in scores):
            messagebox.showinfo("No Data", "No games played yet or no data available for games played.")
            return

        figure = Figure(figsize=(6, 4), dpi=100)
        plot = figure.add_subplot(111)

        # Set the range for the x-axis based on the number of games
        x_range = list(range(1, len(scores) + 1))  # Start range at 1 for game count

        title = attribute.replace("_", " ").title()
        if attribute == "pos":
            title = "Position"
            plot.set_yticks(range(1, 7))
            plot.set_ylim(0.5, 6.5)
        elif attribute in ["aggressiveness_score", "conservativeness_score"]:
            plot.set_ylim(0, 100)

        # Plot the data
        plot.plot(x_range, scores, marker='o')
        plot.set_title(f'Average {title} Over Last Games')
        plot.set_ylabel(title)
        plot.set_xlabel('Games')

        plot.set_xticks(x_range)
        plot.set_xticklabels([str(i) for i in x_range])

        # Display the graph on the canvas
        canvas = FigureCanvasTkAgg(figure, self)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.grid(row=6, column=0, columnspan=4)
        canvas.draw()

    def edit_profile_picture(self):
        self.profile_pic_selection_window = SelectProfilePic(self, self.on_profile_pic_selected, self.current_pic_name)

    def create_recent_games_table(self):
        columns = ("start_time", "end_time", "pos", "buy_in", "participants")
        self.recent_games_table = ttk.Treeview(self, columns=columns, show="headings")
        for col in columns:
            self.recent_games_table.heading(col, text=col.replace("_", " ").title())
            self.recent_games_table.column(col, anchor="center")

        self.recent_games_table.grid(row=3, column=0, columnspan=4, sticky="ew")

        # Get the details of recent games
        recent_games = self.controller.network_manager.send_message({
            "type": "get_recent_games_details",
            "user_id": self.profile_user_id,
            "num_games": 10
        })

        for game in recent_games:
            participants = ', '.join(game['participants'])
            self.recent_games_table.insert("", "end", values=(
            game["start_time"], game["end_time"], game["position"], game["buy_in"], participants))

        for col in columns:
            self.recent_games_table.column(col, width=tkfont.Font().measure(col.title()))

    def on_profile_pic_selected(self, pic_name):
        # Send message to network manager to update the profile picture in the database
        self.controller.network_manager.send_message({
            "type": "set_user_profile_picture",
            "user_id": self.profile_user_id,
            "new_profile_picture": pic_name
        })
        # Update UI with new profile picture
        self.update_profile_picture_display(pic_name)

        if self.previous_menu:
            self.previous_menu.update_profile_picture(self.profile_user_id, pic_name)

    def update_profile_picture_display(self, pic_name):
        image_path = f"gui/Images/Pfps/{pic_name}"
        self.image = Image.open(image_path)
        profile_pic_size = (150, 150)
        self.image = self.image.resize(profile_pic_size)

        # Set up the circular profile picture
        mask = Image.new('L', profile_pic_size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + profile_pic_size, fill=255)

        circular_image = Image.new('RGBA', profile_pic_size, (0, 0, 0, 0))
        circular_image.paste(self.image, (0, 0), mask)
        self.profile_pic_image = ImageTk.PhotoImage(circular_image)

        # Update the canvas image
        self.profile_pic_canvas.itemconfig(self.profile_pic_id, image=self.profile_pic_image)

        # Update the current picture name
        self.current_pic_name = pic_name

    def edit_username(self):
        # Create a new top-level window
        self.edit_username_window = tk.Toplevel(self)
        self.edit_username_window.title("Edit Username")

        # Add an entry widget for the new username
        self.new_username_entry = tk.Entry(self.edit_username_window)
        self.new_username_entry.pack(padx=10, pady=10)

        # Add a button to submit the new username
        submit_button = tk.Button(self.edit_username_window, text="Submit", command=self.submit_new_username)
        submit_button.pack(pady=10)

    def submit_new_username(self):
        new_username = self.new_username_entry.get()

        response = self.controller.network_manager.send_message(
            {"type": "set_username", "user_id": self.profile_user_id, "new_username": new_username})
        if not response.get('success'):
            tk.messagebox.showerror(f"Error changing username", f"{response.get('error')}")
        else:
            self.username = new_username
            self.username_label.config(text=new_username)

            # Update the change in username on the previous menu
            if self.previous_menu is not None:
                # Polymorphism - different methods are called based on the class which the previous_menu variable represents
                self.previous_menu.update_username(new_username, new_username)

            # Close the edit username window
            self.edit_username_window.destroy()


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

        button = tk.Button(parent, image=photo, command=lambda p=pic_name: self.set_profile_picture(p), bg="#333333",
                           bd=0)
        button.image = photo  # Keep a reference so it does not get garbage collected
        button.pack(side='left', padx=10, pady=5)

    def set_profile_picture(self, pic_name):
        self.callback(pic_name)
        self.destroy()
