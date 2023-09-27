import tkinter as tk
from gui.login_menu import LoginMenu
from gui.register_menu import RegisterMenu
from gui.lobby_browser import LobbyBrowser
from gui.main_menu import MainMenu
from gui.game_gui import GameGUI
from logic.network_manager import NetworkManager

class Controller:
    def __init__(self):
        self.current_menu = None
        self.network_manager = NetworkManager()

    def run(self):
        # self.open_login_menu()
        self.open_main_menu(2)
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

    def open_lobby_browser(self, user_id):
        if self.current_menu:
            self.current_menu.destroy()
        self.current_menu = LobbyBrowser(self, user_id)

    def join_lobby(self, user_id, lobby_name):
        if self.current_menu:
            self.current_menu.destroy()
        self.network_manager.join_lobby()
        self.current_menu = GameGUI(self, user_id, lobby_name)
