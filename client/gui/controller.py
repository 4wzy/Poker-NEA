import tkinter as tk
from gui.login_menu import LoginMenu
from gui.register_menu import RegisterMenu
from gui.lobby_browser import LobbyBrowser
from gui.main_menu import MainMenu
from gui.game_gui import GameGUI
from gui.hall_of_fame import HallOfFame
from helpers.network_manager import NetworkManager
from gui.settings_menu import SettingsMenu
from gui.responsible_gambling_menu import ResponsibleGamblingMenu
from gui.how_to_play import HowToPlay
from gui.user_profile import UserProfile


class Controller:
    def __init__(self):
        self.__current_menu = None
        self.network_manager = NetworkManager()

    # Note: When running the application properly, use self.open_login_menu()
    def run(self):
        # self.open_login_menu()
        # The call to open_main_menu() is for debugging purposes only - to skip the login stage for time efficiency
        self.open_main_menu(23)
        tk.mainloop()

    def open_login_menu(self):
        if self.__current_menu:
            self.__current_menu.destroy()
        self.__current_menu = LoginMenu(self)

    def open_register_menu(self):
        if self.__current_menu:
            self.__current_menu.destroy()
        self.__current_menu = RegisterMenu(self)

    def open_main_menu(self, user_id):
        if self.__current_menu:
            self.__current_menu.destroy()
        self.__current_menu = MainMenu(self, user_id)

    def open_user_profile(self, profile_user_id, own_user_id, update_previous_menu=False):
        # Create a new Toplevel window for the user profile
        user_profile_window = tk.Toplevel(self.__current_menu)
        user_profile_window.title("User Profile")
        user_profile_window.configure(bg="#333333")
        if update_previous_menu:
            UserProfile(user_profile_window, self, profile_user_id, own_user_id, self.__current_menu)
        else:
            UserProfile(user_profile_window, self, profile_user_id, own_user_id, None)

    def open_lobby_browser(self, user_id, games_played_today):
        if self.__current_menu:
            self.__current_menu.destroy()
        self.__current_menu = LobbyBrowser(self, user_id, games_played_today)

    def open_hall_of_fame(self, user_id):
        if self.__current_menu:
            self.__current_menu.destroy()
        self.__current_menu = HallOfFame(self, user_id)

    def open_how_to_play(self, user_id):
        if self.__current_menu:
            self.__current_menu.destroy()
        self.__current_menu = HowToPlay(self, user_id)

    def open_settings(self, user_id):
        if self.__current_menu:
            self.__current_menu.destroy()
        self.__current_menu = SettingsMenu(self, user_id)

    def open_responsible_gambling_menu(self, user_id):
        if self.__current_menu:
            self.__current_menu.destroy()
        self.__current_menu = ResponsibleGamblingMenu(self, user_id)

    def join_lobby(self, user_id, lobby_id, show_odds):
        response_data = self.network_manager.join_lobby(user_id, lobby_id)
        print(f"(controller): RESPONSE FROM JOINING LOBBY: {response_data}")
        if response_data and response_data.get("success", True):
            if self.__current_menu:
                self.__current_menu.destroy()
            if response_data.get('type') == "game_starting":
                self.__current_menu = GameGUI(self, user_id, lobby_id, response_data, True, False, show_odds)
            elif response_data.get('type') == "reconnecting":
                self.__current_menu = GameGUI(self, user_id, lobby_id, response_data, False, True, show_odds)
            else:
                self.__current_menu = GameGUI(self, user_id, lobby_id, response_data, False, False, show_odds)
        return response_data

    def process_received_message(self, message_type, message_content):
        if message_type == 'lobby_list':
            if isinstance(self.__current_menu, LobbyBrowser):
                self.__current_menu.populate_lobby_list(message_content)
