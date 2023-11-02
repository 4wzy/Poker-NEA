import time
import tkinter as tk
from gui.login_menu import LoginMenu
from gui.register_menu import RegisterMenu
from gui.lobby_browser import LobbyBrowser
from gui.main_menu import MainMenu
from gui.game_gui import GameGUI
from gui.hall_of_fame import HallOfFame
from logic.network_manager import NetworkManager
from gui.settings_menu import SettingsMenu
from gui.responsible_gambling_menu import ResponsibleGamblingMenu


class Controller:
    def __init__(self):
        self.current_menu = None
        self.network_manager = NetworkManager()

    # Note: When running the application properly, use self.open_login_menu()
    def run(self):
        # self.open_login_menu()
        # The call to open_main_menu() is for debugging purposes only - to skip the login stage for time efficiency
        self.open_main_menu(14)
        tk.mainloop()

    def open_login_menu(self):
        if self.current_menu:
            self.current_menu.destroy()
        self.current_menu = LoginMenu(self)

    def open_register_menu(self):
        if self.current_menu:
            self.current_menu.destroy()
        self.current_menu = RegisterMenu(self)

    def open_main_menu(self, user_id):
        if self.current_menu:
            self.current_menu.destroy()
        self.current_menu = MainMenu(self, user_id)

    def open_lobby_browser(self, user_id, games_played_today):
        if self.current_menu:
            self.current_menu.destroy()
        self.current_menu = LobbyBrowser(self, user_id, games_played_today)

    def open_hall_of_fame(self, user_id):
        if self.current_menu:
            self.current_menu.destroy()
        self.current_menu = HallOfFame(self, user_id)

    def open_settings(self, user_id):
        if self.current_menu:
            self.current_menu.destroy()
        self.current_menu = SettingsMenu(self, user_id)

    def open_responsible_gambling_menu(self, user_id):
        if self.current_menu:
            self.current_menu.destroy()
        self.current_menu = ResponsibleGamblingMenu(self, user_id)

    def join_lobby(self, user_id, lobby_id):
        response_data = self.network_manager.join_lobby(user_id, lobby_id)
        print(f"(controller): RESPONSE FROM JOINING LOBBY: {response_data}")
        if response_data and response_data.get("success", True):
            if self.current_menu:
                self.current_menu.destroy()
            if response_data.get('type') == "game_starting":
                self.current_menu = GameGUI(self, user_id, lobby_id, response_data, True, False)
            elif response_data.get('type') == "reconnecting":
                self.current_menu = GameGUI(self, user_id, lobby_id, response_data, False, True)
            else:
                self.current_menu = GameGUI(self, user_id, lobby_id, response_data, False, False)
        return response_data

    def process_received_message(self, message_type, message_content):
        if message_type == 'lobby_list':
            if isinstance(self.current_menu, LobbyBrowser):
                self.current_menu.populate_lobby_list(message_content)
