import logging
import os
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.core.window import Window
from kivy.utils import platform

from LegionData import LegionDatabase
from screens.menu import MenuScreen
from screens.army_builder import ArmyBuilderScreen
from screens.mission_builder import MissionBuilderScreen
from screens.game_companion import GameCompanionScreen

class LegionApp(App):
    def build(self):
        self.title = "Star Wars Legion Tools"

        # Initialize Database
        self.db = LegionDatabase()

        # Handle Permissions for Android
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.INTERNET, Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])

        # Screen Manager
        sm = ScreenManager(transition=FadeTransition())

        # Add Screens
        # Pass 'app' or 'db' to screens if needed, or they can access App.get_running_app().db
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(ArmyBuilderScreen(name='army_builder'))
        sm.add_widget(MissionBuilderScreen(name='mission_builder'))
        sm.add_widget(GameCompanionScreen(name='game_companion'))

        return sm

if __name__ == '__main__':
    LegionApp().run()
