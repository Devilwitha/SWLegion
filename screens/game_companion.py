import json
import os
import random
import logging
from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.lang import Builder

# Helper for Unit Lists
Builder.load_string('''
<GameUnitItem>:
    orientation: 'horizontal'
    size_hint_y: None
    height: '40dp'
    padding: '5dp'
    Label:
        text: root.text
        size_hint_x: 0.6
    Label:
        text: root.hp_txt
        size_hint_x: 0.2
    Label:
        text: root.status_txt
        color: (0, 1, 0, 1) if root.status_txt == 'Bereit' else (0.5, 0.5, 0.5, 1)
        size_hint_x: 0.2
''')

class GameUnitItem(BoxLayout):
    def __init__(self, text, hp, status, **kwargs):
        super(GameUnitItem, self).__init__(**kwargs)
        self.text = text
        self.hp_txt = str(hp)
        self.status_txt = status

class GameCompanionScreen(Screen):
    def __init__(self, **kwargs):
        super(GameCompanionScreen, self).__init__(**kwargs)
        self.player_army = {"units": []}
        self.opponent_army = {"units": []}
        self.order_pool = []
        self.round = 0
        self.phase = "Setup"
        self.active_unit = None
        self.active_side = None

        root = BoxLayout(orientation='vertical')

        # Header
        header = BoxLayout(size_hint_y=0.08, padding=5)
        header.add_widget(Button(text="< Menu", size_hint_x=0.2, on_release=self.go_back))
        header.add_widget(Label(text="Game Companion", font_size='18sp', bold=True))
        root.add_widget(header)

        # Tabs
        self.tabs = TabbedPanel(do_default_tab=False)

        # Tab Center: Action
        self.tab_center = TabbedPanelItem(text="Schlachtfeld")
        self.center_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.lbl_info = Label(text="Bitte Armeen laden", font_size='20sp')
        self.center_layout.add_widget(self.lbl_info)

        self.btn_action = Button(text="Setup Starten", size_hint_y=None, height='60dp', disabled=True)
        self.btn_action.bind(on_release=self.on_main_action)
        self.center_layout.add_widget(self.btn_action)

        self.tab_center.add_widget(self.center_layout)
        self.tabs.add_widget(self.tab_center)

        # Tab Player
        self.tab_player = TabbedPanelItem(text="Spieler")
        p_layout = BoxLayout(orientation='vertical')
        p_layout.add_widget(Button(text="Armee Laden", size_hint_y=None, height='50dp', on_release=lambda x: self.load_army_dialog('Player')))
        self.scroll_p = ScrollView()
        self.list_p = BoxLayout(orientation='vertical', size_hint_y=None)
        self.list_p.bind(minimum_height=self.list_p.setter('height'))
        self.scroll_p.add_widget(self.list_p)
        p_layout.add_widget(self.scroll_p)
        self.tab_player.add_widget(p_layout)
        self.tabs.add_widget(self.tab_player)

        # Tab Opponent
        self.tab_opp = TabbedPanelItem(text="Gegner")
        o_layout = BoxLayout(orientation='vertical')
        o_layout.add_widget(Button(text="Armee Laden", size_hint_y=None, height='50dp', on_release=lambda x: self.load_army_dialog('Opponent')))
        self.scroll_o = ScrollView()
        self.list_o = BoxLayout(orientation='vertical', size_hint_y=None)
        self.list_o.bind(minimum_height=self.list_o.setter('height'))
        self.scroll_o.add_widget(self.list_o)
        o_layout.add_widget(self.scroll_o)

        self.tab_opp.add_widget(o_layout)
        self.tabs.add_widget(self.tab_opp)

        root.add_widget(self.tabs)
        self.add_widget(root)

    def go_back(self, instance):
        self.manager.current = 'menu'

    def load_army_dialog(self, side):
        # ... File Chooser Logic similar to ArmyBuilder ...
        # Simplified for brevity:
        app = App.get_running_app()
        base_dir = os.path.join(app.user_data_dir, "Armeen")

        content = BoxLayout(orientation='vertical')
        from kivy.uix.filechooser import FileChooserListView
        fc = FileChooserListView(path=base_dir, filters=['*.json'])
        content.add_widget(fc)
        btn = Button(text="Laden", size_hint_y=None, height='50dp')
        content.add_widget(btn)
        popup = Popup(title=f"{side} Armee laden", content=content, size_hint=(0.9, 0.9))

        def do_load(inst):
            if fc.selection:
                self.load_army_file(fc.selection[0], side)
            popup.dismiss()
        btn.bind(on_release=do_load)
        popup.open()

    def load_army_file(self, path, side):
        try:
            with open(path, 'r') as f: data = json.load(f)

            # Enrich
            units = []
            db = App.get_running_app().db
            faction = data.get("faction")

            for u in data.get("army", []):
                # Simple enrichment
                full = u.copy()
                full["current_hp"] = full.get("hp", 1) # Fallback if save lacks hp
                # Find in DB for max HP
                db_u = next((x for x in db.units.get(faction, []) if x["name"] == u["name"]), None)
                if db_u:
                     full["hp"] = db_u["hp"]
                     full["current_hp"] = db_u["hp"]
                     full["weapons"] = db_u.get("weapons", [])

                full["activated"] = False
                units.append(full)

            if side == "Player":
                self.player_army = {"faction": faction, "units": units}
                self.update_list_ui(self.list_p, units)
            else:
                self.opponent_army = {"faction": faction, "units": units}
                self.update_list_ui(self.list_o, units)

            if self.player_army["units"] and self.opponent_army["units"]:
                self.btn_action.disabled = False
                self.btn_action.text = "Spiel Starten"

        except Exception as e:
            logging.error(f"Load error: {e}")

    def update_list_ui(self, layout, units):
        layout.clear_widgets()
        for u in units:
            st = "Aktiviert" if u["activated"] else "Bereit"
            layout.add_widget(GameUnitItem(u["name"], f"{u['current_hp']}/{u.get('hp','?')}", st))

    def on_main_action(self, instance):
        if self.phase == "Setup":
            self.start_game()
        elif self.phase == "Activation":
            self.draw_order()

    def start_game(self):
        self.round = 1
        self.phase = "Activation" # Simplified: Skip Command Phase for now
        self.lbl_info.text = f"Runde {self.round}: Aktivierung"
        self.create_order_pool()
        self.btn_action.text = "Befehl Ziehen"

    def create_order_pool(self):
        self.order_pool = []
        for u in self.player_army["units"]:
            if u["current_hp"] > 0: self.order_pool.append({'side': 'Player', 'unit': u})
        for u in self.opponent_army["units"]:
            if u["current_hp"] > 0: self.order_pool.append({'side': 'Opponent', 'unit': u})
        random.shuffle(self.order_pool)

    def draw_order(self):
        if not self.order_pool:
            self.lbl_info.text = "Runde Beendet"
            self.btn_action.text = "Nächste Runde"
            self.btn_action.bind(on_release=self.next_round)
            return

        token = self.order_pool.pop(0)
        self.active_unit = token['unit']
        self.active_side = token['side']
        self.active_unit['activated'] = True

        self.lbl_info.text = f"AKTIV: {self.active_unit['name']} ({self.active_side})"

        # Show Actions
        self.show_actions_popup()

        # Update lists
        self.update_list_ui(self.list_p, self.player_army["units"])
        self.update_list_ui(self.list_o, self.opponent_army["units"])

    def next_round(self, instance):
        self.round += 1
        # Reset activated
        for u in self.player_army["units"] + self.opponent_army["units"]:
            u["activated"] = False

        self.btn_action.unbind(on_release=self.next_round)
        self.btn_action.bind(on_release=self.on_main_action)
        self.start_game()

    def show_actions_popup(self):
        content = BoxLayout(orientation='vertical', padding=10)
        content.add_widget(Label(text=f"{self.active_unit['name']}", font_size='20sp', bold=True))

        grid = GridLayout(cols=2, spacing=10)
        grid.add_widget(Button(text="Bewegung", on_release=lambda x: self.action_move(popup)))
        grid.add_widget(Button(text="Angriff", on_release=lambda x: self.action_attack(popup)))
        grid.add_widget(Button(text="Zielen/Ausweichen", on_release=lambda x: popup.dismiss())) # Placeholder
        grid.add_widget(Button(text="Passen", on_release=lambda x: popup.dismiss()))

        content.add_widget(grid)
        popup = Popup(title="Aktionen", content=content, size_hint=(0.8, 0.5), auto_dismiss=False)
        popup.open()

    def action_move(self, parent_popup):
        parent_popup.dismiss()
        # Logic for move...

    def action_attack(self, parent_popup):
        parent_popup.dismiss()
        # Open Dice Roller
        self.open_dice_roller()

    def open_dice_roller(self):
        # Simplified Dice Roller
        content = BoxLayout(orientation='vertical', padding=10)

        # Weapon Select (Mock)
        # In real implementation, read self.active_unit['weapons']

        lbl_res = Label(text="Ergebnis: -")
        content.add_widget(lbl_res)

        btn_roll = Button(text="Würfeln (Simuliert)", size_hint_y=None, height='50dp')

        def roll(inst):
            # Dummy logic
            hits = random.randint(0, 5)
            lbl_res.text = f"Treffer: {hits}"

        btn_roll.bind(on_release=roll)
        content.add_widget(btn_roll)

        btn_apply = Button(text="Schaden anwenden", size_hint_y=None, height='50dp')

        def apply(inst):
            # Apply to target... (need target selection)
            # Just close for now
            popup.dismiss()

        btn_apply.bind(on_release=apply)
        content.add_widget(btn_apply)

        popup = Popup(title="Angriff", content=content, size_hint=(0.9, 0.6))
        popup.open()
