import json
import os
import random
import threading
from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.graphics import Color, Rectangle, Line, Ellipse
from kivy.clock import Clock
from kivy.uix.popup import Popup

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

class MapWidget(Widget):
    def __init__(self, **kwargs):
        super(MapWidget, self).__init__(**kwargs)
        self.deployment = "Battle Lines"
        self.mission_type = "Kein Marker"
        self.blue_faction = "Blau"
        self.red_faction = "Rot"
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def set_data(self, deployment, mission, blue, red):
        self.deployment = deployment
        self.mission_type = mission
        self.blue_faction = blue
        self.red_faction = red
        self.update_canvas()

    def update_canvas(self, *args):
        self.canvas.clear()
        w, h = self.size

        # Scaling: Legion board is 6x3.
        # We try to fit 2:1 ratio.

        with self.canvas:
            # Background
            Color(0.88, 0.96, 1, 1) # Light Blue
            Rectangle(pos=self.pos, size=self.size)

            # Border
            Color(0.01, 0.53, 0.82, 1)
            Line(rectangle=(self.x, self.y, w, h), width=2)

            # Helper functions for relative coords
            def ft_w(ft): return (ft / 6.0) * w
            def ft_h(ft): return (ft / 3.0) * h

            # Draw Zones
            # Red (Top/Right), Blue (Bottom/Left)

            mode = self.deployment

            Color(1, 0.8, 0.82, 0.5) # Red Zone Fill
            # Need to define rects based on mode.
            # Simplified logic for Kivy (origin bottom-left)

            r1 = ft_h(0.5)

            if mode == "Battle Lines":
                # Red Top
                Rectangle(pos=(self.x, self.y + h - r1), size=(w, r1))
                # Blue Bottom
                Color(0.73, 0.87, 0.98, 0.5) # Blue Fill
                Rectangle(pos=(self.x, self.y), size=(w, r1))

            elif mode == "The Long March":
                r1_w = ft_w(0.5)
                # Red Right
                Rectangle(pos=(self.x + w - r1_w, self.y), size=(r1_w, h))
                # Blue Left
                Color(0.73, 0.87, 0.98, 0.5)
                Rectangle(pos=(self.x, self.y), size=(r1_w, h))

            # ... (Other modes simplified for brevity, assume Battle Lines default) ...

            # Text Labels (using CoreLabel or just Widget Label overlay?
            # Canvas text is hard in Kivy without Label widget overlay.
            # We'll skip text on canvas for now, or rely on UI Labels outside.)

            # Objectives
            Color(0.4, 0.73, 0.41, 1) # Green

            cx, cy = self.x + w/2, self.y + h/2

            if "Intercept" in self.mission_type or "Abfangen" in self.mission_type:
                # Center
                Ellipse(pos=(cx-10, cy-10), size=(20, 20))
                # Left/Right
                Ellipse(pos=(self.x + w/4 - 10, cy-10), size=(20, 20))
                Ellipse(pos=(self.x + 3*w/4 - 10, cy-10), size=(20, 20))

            # ... (Other missions) ...

class MissionBuilderScreen(Screen):
    def __init__(self, **kwargs):
        super(MissionBuilderScreen, self).__init__(**kwargs)

        self.fraktionen = [
            "Galaktisches Imperium", "Rebellenallianz",
            "Galaktische Republik", "Separatistenallianz",
            "Schattenkollektiv (Shadow Collective)"
        ]
        self.gelaende_typen = ["Wald", "Wüste", "Schnee", "Stadt", "Industrie", "Gebirge"]

        self.chk_fractions = {}
        self.chk_terrain = {}

        # UI
        root = BoxLayout(orientation='vertical')

        # Header
        root.add_widget(Button(text="< Menu", size_hint_y=None, height='40dp', on_release=self.go_back))

        tabs = TabbedPanel(do_default_tab=False)

        # Tab 1: Settings
        tab_set = TabbedPanelItem(text="Einstellungen")
        scroll = ScrollView()
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        # Factions
        layout.add_widget(Label(text="Beteiligte Fraktionen:", size_hint_y=None, height='30dp', bold=True))
        for f in self.fraktionen:
            row = BoxLayout(size_hint_y=None, height='30dp')
            chk = CheckBox(size_hint_x=0.1)
            row.add_widget(chk)
            row.add_widget(Label(text=f, size_hint_x=0.9, halign='left', text_size=(None, None)))
            layout.add_widget(row)
            self.chk_fractions[f] = chk

        # Terrain
        layout.add_widget(Label(text="Gelände:", size_hint_y=None, height='30dp', bold=True))
        for g in self.gelaende_typen:
            row = BoxLayout(size_hint_y=None, height='30dp')
            chk = CheckBox(size_hint_x=0.1)
            row.add_widget(chk)
            row.add_widget(Label(text=g, size_hint_x=0.9, halign='left', text_size=(None, None)))
            layout.add_widget(row)
            self.chk_terrain[g] = chk

        # Points
        layout.add_widget(Label(text="Punkte:", size_hint_y=None, height='30dp', bold=True))
        self.ti_points = TextInput(text="800", size_hint_y=None, height='40dp', multiline=False)
        layout.add_widget(self.ti_points)

        # Generate Button
        btn_gen = Button(text="Szenario Generieren (AI)", size_hint_y=None, height='50dp', background_color=(0.13, 0.59, 0.95, 1))
        btn_gen.bind(on_release=self.generate_scenario)
        layout.add_widget(btn_gen)

        # Output Text
        self.ti_output = TextInput(text="", readonly=True, size_hint_y=None, height='200dp')
        layout.add_widget(self.ti_output)

        scroll.add_widget(layout)
        tab_set.add_widget(scroll)
        tabs.add_widget(tab_set)

        # Tab 2: Map
        tab_map = TabbedPanelItem(text="Karte")
        map_layout = BoxLayout(orientation='vertical', padding=10)

        # Controls
        ctrl_grid = GridLayout(cols=2, size_hint_y=None, height='100dp', spacing=5)

        ctrl_grid.add_widget(Label(text="Aufstellung:"))
        self.spin_deploy = Spinner(text="Battle Lines", values=["Battle Lines", "The Long March", "Disarray", "Major Offensive"])
        self.spin_deploy.bind(text=self.update_map_data)
        ctrl_grid.add_widget(self.spin_deploy)

        ctrl_grid.add_widget(Label(text="Mission:"))
        self.spin_mission = Spinner(text="Kein Marker", values=["Kein Marker", "Abfangen (Intercept)", "Durchbruch", "Eliminierung"])
        self.spin_mission.bind(text=self.update_map_data)
        ctrl_grid.add_widget(self.spin_mission)

        map_layout.add_widget(ctrl_grid)

        # Canvas Widget
        self.map_widget = MapWidget()
        map_layout.add_widget(self.map_widget)

        btn_save = Button(text="Mission Speichern", size_hint_y=None, height='50dp')
        btn_save.bind(on_release=self.save_mission_dialog)
        map_layout.add_widget(btn_save)

        tab_map.add_widget(map_layout)
        tabs.add_widget(tab_map)

        root.add_widget(tabs)
        self.add_widget(root)

    def go_back(self, instance):
        self.manager.current = 'menu'

    def update_map_data(self, *args):
        self.map_widget.set_data(
            self.spin_deploy.text,
            self.spin_mission.text,
            "Blau", "Rot"
        )

    def generate_scenario(self, instance):
        if not REQUESTS_AVAILABLE:
            self.ti_output.text = "Requests Modul fehlt."
            return

        # Get key
        key = ""
        try:
             with open("gemini_key.txt", "r") as f: key = f.read().strip()
        except: pass

        if not key:
            self.ti_output.text = "Fehler: gemini_key.txt fehlt."
            return

        self.ti_output.text = "Generiere..."

        fractions = [k for k,v in self.chk_fractions.items() if v.active]
        terrain = [k for k,v in self.chk_terrain.items() if v.active]

        prompt = f"Star Wars Legion Mission. Punkte: {self.ti_points.text}. Fraktionen: {', '.join(fractions)}. Gelände: {', '.join(terrain)}. Aufstellung: {self.spin_deploy.text}. Mission: {self.spin_mission.text}. Erstelle Story und Sonderregeln auf Deutsch."

        # Threaded request
        def req():
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={key}"
            headers = {'Content-Type': 'application/json'}
            data = {"contents": [{"parts": [{"text": prompt}]}]}
            try:
                resp = requests.post(url, headers=headers, json=data)
                if resp.status_code == 200:
                    res = resp.json()
                    txt = res['candidates'][0]['content']['parts'][0]['text']
                    Clock.schedule_once(lambda dt: setattr(self.ti_output, 'text', txt))
                else:
                    Clock.schedule_once(lambda dt: setattr(self.ti_output, 'text', f"Error: {resp.status_code}"))
            except Exception as e:
                Clock.schedule_once(lambda dt: setattr(self.ti_output, 'text', str(e)))

        threading.Thread(target=req).start()

    def save_mission_dialog(self, instance):
        # ... Similar save logic as Army Builder ...
        pass
