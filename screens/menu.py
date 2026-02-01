from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.app import App

class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super(MenuScreen, self).__init__(**kwargs)

        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

        # Title
        title = Label(
            text="Star Wars Legion Zentrale",
            font_size='24sp',
            bold=True,
            size_hint=(1, 0.2)
        )
        layout.add_widget(title)

        # Buttons
        btn_army = Button(
            text="Armee Builder",
            background_color=(0.13, 0.59, 0.95, 1), # #2196F3
            font_size='18sp',
            bold=True,
            size_hint=(1, 0.15),
            on_release=self.go_to_army
        )
        layout.add_widget(btn_army)

        btn_mission = Button(
            text="Mission Generator",
            background_color=(1, 0.6, 0, 1), # #FF9800
            font_size='18sp',
            bold=True,
            size_hint=(1, 0.15),
            on_release=self.go_to_mission
        )
        layout.add_widget(btn_mission)

        btn_game = Button(
            text="Spiel-Begleiter (Game Companion)",
            background_color=(0.3, 0.69, 0.31, 1), # #4CAF50
            font_size='18sp',
            bold=True,
            size_hint=(1, 0.15),
            on_release=self.go_to_game
        )
        layout.add_widget(btn_game)

        # Footer
        footer = Label(
            text="Wähle ein Modul um zu starten.",
            font_size='14sp',
            size_hint=(1, 0.1)
        )
        layout.add_widget(footer)

        self.add_widget(layout)

    def go_to_army(self, instance):
        self.manager.current = 'army_builder'

    def go_to_mission(self, instance):
        self.manager.current = 'mission_builder'

    def go_to_game(self, instance):
        self.manager.current = 'game_companion'
