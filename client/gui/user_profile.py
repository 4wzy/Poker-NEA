import base64
import glob
import os
import time
import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont
from PIL import Image, ImageTk, ImageDraw
from tkinter import messagebox, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class UserProfile(tk.Frame):
    def __init__(self, parent, controller, profile_user_id, own_user_id, previous_menu, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.__num_games = 10
        self.controller = controller
        self.profile_user_id = profile_user_id
        self.previous_menu = previous_menu
        self.profile_picture_manager = ProfilePictureManager(self.controller)
        self.__current_pic_path = self.profile_picture_manager.check_and_fetch_profile_picture(self.profile_user_id)
        self.__own_profile = self.profile_user_id == own_user_id  # Boolean flag indicating if the profile belongs to
        # the current user
        self.configure(bg="#333333")

        self.statistics = self.controller.network_manager.send_message({
            "type": "get_user_statistics",
            "user_id": self.profile_user_id
        })

        self.__create_widgets()
        self.pack(fill="both", expand=True)

    def __create_widgets(self):
        top_frame = tk.Frame(self, bg="#333333")
        top_frame.grid(row=0, column=0, columnspan=4, sticky="ew")

        # Profile picture
        profile_pic_size = (150, 150)
        self.image = Image.open(self.__current_pic_path)
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

        self.username = self.controller.network_manager.send_message({
            "type": "get_username",
            "user_id": self.profile_user_id
        })

        self.profile_pic_canvas = tk.Canvas(top_frame, width=profile_pic_size[0], height=profile_pic_size[1],
                                            bg="#333333", bd=0, highlightthickness=0)
        self.profile_pic_canvas.pack(side="left", padx=10, pady=10)
        self.profile_pic_id = self.profile_pic_canvas.create_image(profile_pic_size[0] // 2, profile_pic_size[1] // 2,
                                                                   image=self.profile_pic_image)

        self.username_label = tk.Label(top_frame, text=self.username, font=tkfont.Font(family="Cambria", size=24),
                                       fg="#F56476", bg="#333333")
        self.username_label.pack(side="left", padx=10, pady=10)

        if self.__own_profile:
            edit_pic_button = tk.Button(top_frame, text="Edit Picture", command=self.edit_profile_picture)
            edit_pic_button.pack(side="left", padx=10, pady=10)

            edit_name_button = tk.Button(top_frame, text="Edit Name", command=self.edit_username)
            edit_name_button.pack(side="left", padx=10, pady=10)

        if self.statistics:
            # Statistics display
            stats_details_frame = tk.Frame(self, bg="#555555", padx=10, pady=10)
            stats_details_frame.grid(row=1, column=0, columnspan=4, sticky="ew")

            games_played_label = tk.Label(stats_details_frame, text=f"Games Played: {self.statistics['games_played']}",
                                          bg="#555555", fg="#FFFFFF")
            games_played_label.pack(side="top", fill="x")

            games_won_label = tk.Label(stats_details_frame, text=f"Games Won: {self.statistics['games_won']}",
                                       bg="#555555", fg="#FFFFFF")
            games_won_label.pack(side="top", fill="x")

            total_play_time_label = tk.Label(stats_details_frame,
                                             text=f"Total Play Time: {self.statistics['total_play_time']} seconds",
                                             bg="#555555", fg="#FFFFFF")
            total_play_time_label.pack(side="top", fill="x")

            rgscore_label = tk.Label(stats_details_frame, text=f"RG Score: {self.statistics['rgscore']}",
                                     bg="#555555", fg="#FFFFFF")
            rgscore_label.pack(side="top", fill="x")

            streak_label = tk.Label(stats_details_frame, text=f"Streak: {self.statistics['streak']}",
                                    bg="#555555", fg="#FFFFFF")
            streak_label.pack(side="top", fill="x")

            aggressiveness_score_label = tk.Label(stats_details_frame,
                                                  text=f"Average Aggressiveness Score: {self.statistics['average_aggressiveness_score']}",
                                                  bg="#555555", fg="#FFFFFF")
            aggressiveness_score_label.pack(side="top", fill="x")

            conservativeness_score_label = tk.Label(stats_details_frame,
                                                    text=f"Average Conservativeness Score: {self.statistics['average_conservativeness_score']}",
                                                    bg="#555555", fg="#FFFFFF")
            conservativeness_score_label.pack(side="top", fill="x")

            # Separate frames for the table and the graph (to make the GUI more compact)
            self.left_frame = tk.Frame(self, bg="#333333")
            self.left_frame.grid(row=4, column=0, sticky="nswe")

            self.right_frame = tk.Frame(self, bg="#333333")
            self.right_frame.grid(row=4, column=1, sticky="nswe")

            self.create_recent_games_table(self.left_frame)

            # GUI features related to graph
            options_frame = tk.Frame(self, bg="#333333")
            options_frame.grid(row=2, column=0, columnspan=4, sticky="ew")

            info_label = tk.Label(options_frame, text="Select options to view graph",
                                  font=tkfont.Font(family="Cambria", size=14),
                                  fg="#FFFFFF", bg="#333333")
            info_label.pack(side="top", fill="x")

            self.num_games_var = tk.StringVar()
            self.num_games_dropdown = ttk.Combobox(self, textvariable=self.num_games_var, state="readonly")
            self.num_games_dropdown['values'] = (5, 10, 20, 50, 100)
            self.num_games_dropdown.set(10)
            self.num_games_dropdown.grid(row=3, column=0, padx=10, pady=10)
            self.num_games_dropdown.bind("<<ComboboxSelected>>", self.on_num_games_selected)

            self.attribute_var = tk.StringVar()
            self.attribute_dropdown = ttk.Combobox(self, textvariable=self.attribute_var, state="readonly")
            self.attribute_dropdown['values'] = ("pos", "winnings", "aggressiveness_score", "conservativeness_score")
            self.attribute_dropdown.set("conservativeness_score")  # default value
            self.attribute_dropdown.grid(row=3, column=1, padx=10, pady=10)
            self.attribute_dropdown.bind("<<ComboboxSelected>>", self.on_attribute_selected)

            default_attribute = "aggressiveness_score"
            default_scores = self.controller.network_manager.send_message({
                "type": "get_attribute_from_user_games_played",
                "user_id": self.profile_user_id,
                "attribute": default_attribute,
                "num_games": self.__num_games
            })
            self.display_graph(default_scores, default_attribute, self.right_frame)

            self.grid_rowconfigure(4, weight=1)
            self.grid_columnconfigure(0, weight=1)
            self.grid_columnconfigure(1, weight=1)

    def on_attribute_selected(self, event):
        num_games = int(self.num_games_var.get())
        attribute = self.attribute_var.get()
        scores = self.controller.network_manager.send_message({
            "type": "get_attribute_from_user_games_played",
            "user_id": self.profile_user_id,
            "attribute": attribute,
            "num_games": num_games
        })
        self.display_graph(scores, attribute, self.right_frame)

    def on_num_games_selected(self, event):
        self.__num_games = int(self.num_games_var.get())
        attribute = "conservativeness_score"
        scores = self.controller.network_manager.send_message({
            "type": "get_attribute_from_user_games_played",
            "user_id": self.profile_user_id,
            "attribute": attribute,
            "num_games": self.__num_games
        })
        self.display_graph(scores, attribute, self.right_frame)
        self.create_recent_games_table(self.left_frame)

    def display_graph(self, scores, attribute, frame):
        for widget in frame.winfo_children():
            widget.destroy()

        # If there are no scores, display an error message instead of the graph
        if not scores:
            no_data_label = tk.Label(frame,
                                     text="No games played yet or no data available for graph based on games played.",
                                     fg="#FFFFFF", bg="#333333")
            no_data_label.pack(side="top", fill="both", expand=True)
            return

        figure = Figure(figsize=(5, 5), dpi=100)
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
        plot.set_title(f'{title} Over Last {len(scores)} Games')
        plot.set_ylabel(title)
        plot.set_xlabel('Games')

        plot.set_xticks(x_range)
        plot.set_xticklabels([str(i) for i in x_range])

        # Display the graph on the canvas
        canvas = FigureCanvasTkAgg(figure, frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.grid(row=0, column=0, sticky="ew")
        canvas.draw()

    def edit_profile_picture(self):
        self.__current_pic_path = self.profile_picture_manager.check_and_fetch_profile_picture(self.profile_user_id)
        self.profile_pic_selection_window = SelectProfilePic(self, self.on_profile_pic_selected,
                                                             self.__current_pic_path, self.controller,
                                                             self.profile_user_id)

    def create_recent_games_table(self, frame):
        columns = ("start_time", "end_time", "position", "buy_in", "participants")
        self.recent_games_table = ttk.Treeview(frame, columns=columns, show="headings")
        for col in columns:
            self.recent_games_table.heading(col, text=col.replace("_", " ").title())
            self.recent_games_table.column(col, anchor="center", width=100)

        self.recent_games_table.grid(row=0, column=0, sticky="ew")

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.recent_games_table.yview)
        self.recent_games_table.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky='ns')

        # Get the details of recent games
        recent_games = self.controller.network_manager.send_message({
            "type": "get_recent_games_details",
            "user_id": self.profile_user_id,
            "num_games": self.__num_games
        })

        # The code below is for resizing the columns so that they fit based on the longest value in each column
        # I am using a dictionary to keep track of the maximum text width of each column
        column_widths = {col: tkfont.Font().measure(col.title()) for col in columns}

        for game in recent_games:
            participant_names = ', '.join(game['participants'])
            game_details = (game["start_time"], game["end_time"], game["position"], game["buy_in"], participant_names)
            # Insert the game details as a new row in the table
            self.recent_games_table.insert("", "end", values=game_details)

            # Measure the width of each entry in the row and update column_width if it's larger than previous ones
            for index, value in enumerate(game_details):
                entry_width = tkfont.Font().measure(str(value))
                column_name = columns[index]
                if entry_width > column_widths[column_name]:
                    column_widths[column_name] = entry_width

        # Set the width of each column from the table
        for column in columns:
            self.recent_games_table.column(column, width=column_widths[column])

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

        if len(new_username) < 3 or len(new_username) > 20:
            tk.messagebox.showerror(f"Error changing username", "Length requirements not met. Username must be more "
                                                                "than 3 characters long and less than 20 characters "
                                                                "long.")
            self.edit_username_window.destroy()
            return

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
    def __init__(self, parent, callback, current_pic_path, controller, profile_user_id):
        super().__init__(parent)
        self.callback = callback
        self.title('Select Profile Picture')
        self.geometry('400x450')
        self.configure(bg="#333333")
        self.profile_pics = [
            "cat.png", "default.png", "elephant.png", "giraffe.png",
            "hedgehog.png", "llama.png", "octopus.png", "tiger.png"
        ]
        self.current_pic_path = current_pic_path
        self.controller = controller
        self.profile_user_id = profile_user_id
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

        img = Image.open(self.current_pic_path)
        img.thumbnail((100, 100))
        current_photo = ImageTk.PhotoImage(img)

        current_pic_label = tk.Label(current_pic_frame, image=current_photo, bg="#555555")
        current_pic_label.image = current_photo  # Keep a reference
        current_pic_label.pack(side='top', pady=10)

        upload_btn = tk.Button(self, text="Upload New Picture", command=self.upload_new_picture, bg="#555555",
                               fg="#FFFFFF")
        upload_btn.pack(side='bottom', pady=10)

    def upload_new_picture(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            # Resize and send to server
            self.resize_and_upload(file_path)

    def resize_and_upload(self, file_path):
        # Resize the image
        img = Image.open(file_path)
        img = img.resize((150, 150))

        # Generate a filename using a timestamp
        current_timestamp = int(time.time())
        filename = f"{self.profile_user_id}_{current_timestamp}.png"

        # Save the resized image to the local directory
        local_path = os.path.join('gui/Images/Pfps', filename)
        img.save(local_path)

        with open(local_path, "rb") as file:
            image_data = file.read()
            encoded_image_data = base64.b64encode(image_data).decode('utf-8')  # Encode as Base64

        # Send the base64 encoded image data and filename to the server
        self.controller.network_manager.send_message({
            "type": "upload_profile_picture",
            "user_id": self.profile_user_id,
            "image_data": encoded_image_data,
            "filename": filename  # Include the filename in the message
        })

        self.set_profile_picture(filename)

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


class ProfilePictureManager:
    def __init__(self, controller):
        self.controller = controller
        self.profile_pictures_path = "gui/Images/Pfps"

    # This method checks if the profile picture in question is already stored on the client side
    # and requests it from the server to save locally if it isn't, then returns the file path to the picture
    def check_and_fetch_profile_picture(self, user_id):
        filename_response = self.controller.network_manager.send_message({
            "type": "get_user_profile_picture",
            "user_id": user_id
        })
        print(f"filename_response: {filename_response}")
        if filename_response:
            filename = filename_response if filename_response else "default.png"
            local_file_path = os.path.join(self.profile_pictures_path, filename)
            print(f"local_file_path: {local_file_path}")

            if not os.path.exists(local_file_path):
                # Delete old profile pictures
                for old_file in glob.glob(f"{self.profile_pictures_path}/{user_id}_*.png"):
                    os.remove(old_file)
                    print(f"removed {old_file}")

                image_data_response = self.controller.network_manager.send_message({
                    "type": "get_profile_picture",
                    "user_id": user_id
                })
                if image_data_response:
                    # Save the profile picture locally
                    print(f"Image data response received")
                    if image_data_response.get("success"):
                        self.save_profile_picture(local_file_path, image_data_response['image_data'])
                    else:
                        return False

            return local_file_path

        return False

    def save_profile_picture(self, file_path, image_data_base64):
        image_data = base64.b64decode(image_data_base64)
        with open(file_path, 'wb') as file:
            file.write(image_data)
        print(f"Saved profile picture to {file_path}")
