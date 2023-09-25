import tkinter as tk
from gui.login_menu import LoginMenu
from gui.register_menu import RegisterMenu


class Controller:
    def __init__(self):
        self.current_menu = None

    def run(self):
        self.open_login_menu()
        tk.mainloop()

    def open_login_menu(self):
        if self.current_menu:
            self.current_menu.destroy()
        self.current_menu = LoginMenu(self)

    def open_register_menu(self):
        if self.current_menu:
            self.current_menu.destroy()
        self.current_menu = RegisterMenu(self)
