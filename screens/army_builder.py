import json
import os
import logging
from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.popup import Popup
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.properties import BooleanProperty, StringProperty, ListProperty, ObjectProperty
from kivy.core.clipboard import Clipboard
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.utils import platform

# --- KV Styles ---
Builder.load_string('''
<UnitListItem>:
    orientation: 'horizontal'
    size_hint_y: None
    height: '48dp'
    padding: '5dp'
    spacing: '5dp'
    canvas.before:
        Color:
            rgba: (0.9, 0.9, 0.9, 1) if self.selected else (1, 1, 1, 1)
        Rectangle:
            pos: self.pos
            size: self.size
    Label:
        text: root.text
        color: (0, 0, 0, 1)
        text_size: self.size
        halign: 'left'
        valign: 'middle'
        size_hint_x: 0.7
    Label:
        text: root.points_txt
        color: (0, 0, 0, 1)
        size_hint_x: 0.2
    Button:
        text: '+'
        size_hint_x: 0.1
        on_release: root.on_add_btn()

<ArmyListItem>:
    orientation: 'horizontal'
    size_hint_y: None
    height: '60dp'
    padding: '5dp'
    spacing: '5dp'
    canvas.before:
        Color:
            rgba: (0.95, 0.95, 0.95, 1)
        Rectangle:
            pos: self.pos
            size: self.size
    BoxLayout:
        orientation: 'vertical'
        size_hint_x: 0.8
        Label:
            text: root.text
            color: (0, 0, 0, 1)
            bold: True
            text_size: self.size
            halign: 'left'
            valign: 'middle'
        Label:
            text: root.details
            color: (0.3, 0.3, 0.3, 1)
            font_size: '12sp'
            text_size: self.size
            halign: 'left'
            valign: 'middle'
    Label:
        text: root.points_txt
        color: (0, 0, 0, 1)
        size_hint_x: 0.15
    Button:
        text: 'X'
        background_color: (1, 0.5, 0.5, 1)
        size_hint_x: 0.05
        on_release: root.on_remove_btn()

<CommandCardItem>:
    orientation: 'horizontal'
    size_hint_y: None
    height: '40dp'
    Label:
        text: root.text
        size_hint_x: 0.8
    Label:
        text: root.pips
        size_hint_x: 0.1
    CheckBox:
        active: root.is_selected
        on_active: root.on_checkbox(self.active)
        size_hint_x: 0.1
''')

class UnitListItem(RecycleDataViewBehavior, BoxLayout):
    text = StringProperty("")
    points_txt = StringProperty("")
    selected = BooleanProperty(False)
    index = None

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        self.text = data['text']
        self.points_txt = str(data['points'])
        return super(UnitListItem, self).refresh_view_attrs(rv, index, data)

    def on_add_btn(self):
        # Trigger popup in parent screen
        app = App.get_running_app()
        screen = app.root.get_screen('army_builder')
        screen.open_unit_config(self.text)

class ArmyListItem(RecycleDataViewBehavior, BoxLayout):
    text = StringProperty("")
    details = StringProperty("")
    points_txt = StringProperty("")
    index = None

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        self.text = data['text']
        self.details = data['details']
        self.points_txt = str(data['points'])
        return super(ArmyListItem, self).refresh_view_attrs(rv, index, data)

    def on_remove_btn(self):
        app = App.get_running_app()
        screen = app.root.get_screen('army_builder')
        screen.remove_unit(self.index)

class ArmyBuilderScreen(Screen):
    def __init__(self, **kwargs):
        super(ArmyBuilderScreen, self).__init__(**kwargs)
        self.current_faction = ""
        self.current_army_list = []
        self.current_command_cards = []
        self.total_points = 0

        # UI Structure
        root_layout = BoxLayout(orientation='vertical')

        # -- Top Bar --
        top_bar = BoxLayout(size_hint_y=0.1, padding=5, spacing=5)

        btn_back = Button(text="< Menu", size_hint_x=0.2, on_release=self.go_back)
        top_bar.add_widget(btn_back)

        self.spinner_faction = Spinner(
            text='Fraktion wählen',
            values=[],
            size_hint_x=0.5,
            sync_height=True
        )
        self.spinner_faction.bind(text=self.on_faction_select)
        top_bar.add_widget(self.spinner_faction)

        self.lbl_points = Label(text="0 / 800", size_hint_x=0.3, font_size='16sp', bold=True)
        top_bar.add_widget(self.lbl_points)

        root_layout.add_widget(top_bar)

        # -- Tabs --
        self.tabs = TabbedPanel(do_default_tab=False)

        # Tab 1: Library
        tab_lib = TabbedPanelItem(text="Einheiten")
        lib_layout = BoxLayout(orientation='vertical')

        # Filter (Rank) - Optional, for now just list all

        # RecycleView for Units
        self.rv_units = RecycleView(viewclass='UnitListItem')
        self.rv_units_layout = RecycleBoxLayout(default_size=(None, dp(48)), default_size_hint=(1, None), size_hint_y=None, orientation='vertical')
        self.rv_units_layout.bind(minimum_height=self.rv_units_layout.setter('height'))
        self.rv_units.add_widget(self.rv_units_layout)
        lib_layout.add_widget(self.rv_units)

        tab_lib.add_widget(lib_layout)
        self.tabs.add_widget(tab_lib)

        # Tab 2: Army List
        tab_list = TabbedPanelItem(text="Meine Liste")
        list_layout = BoxLayout(orientation='vertical')

        self.rv_army = RecycleView(viewclass='ArmyListItem')
        self.rv_army_layout = RecycleBoxLayout(default_size=(None, dp(60)), default_size_hint=(1, None), size_hint_y=None, orientation='vertical')
        self.rv_army_layout.bind(minimum_height=self.rv_army_layout.setter('height'))
        self.rv_army.add_widget(self.rv_army_layout)
        list_layout.add_widget(self.rv_army)

        # Actions for List
        btn_box = BoxLayout(size_hint_y=None, height='50dp', spacing=5)
        btn_box.add_widget(Button(text="Karten", on_release=self.open_deck_builder))
        btn_box.add_widget(Button(text="Speichern", on_release=self.save_army_dialog))
        btn_box.add_widget(Button(text="Laden", on_release=self.load_army_dialog))
        btn_box.add_widget(Button(text="Export", on_release=self.export_to_clipboard))
        list_layout.add_widget(btn_box)

        tab_list.add_widget(list_layout)
        self.tabs.add_widget(tab_list)

        root_layout.add_widget(self.tabs)
        self.add_widget(root_layout)

    def on_enter(self):
        # Load Factions
        app = App.get_running_app()
        if hasattr(app, 'db'):
            self.db = app.db
            factions = list(self.db.units.keys())
            self.spinner_faction.values = factions

            # Create Army Dir
            self.base_dir = os.path.join(app.user_data_dir, "Armeen")
            if not os.path.exists(self.base_dir):
                os.makedirs(self.base_dir)

    def go_back(self, instance):
        self.manager.current = 'menu'

    def on_faction_select(self, spinner, text):
        self.current_faction = text
        self.update_unit_list()
        # Reset current army if faction changes?
        # Ideally warn user. For now, we allow mixing only if we don't clear, but Legion rules usually 1 faction.
        # Simple approach: Clear army if faction changes? No, user might just be browsing.
        # But units from other faction shouldn't be valid.
        # We will keep list but it might look weird.
        # Better: User manually clears or we clear.
        # Let's just update the library list.

    def update_unit_list(self):
        if not self.current_faction or not self.db: return

        units = self.db.units.get(self.current_faction, [])
        # Sort by rank
        order = {"Commander": 1, "Operative": 2, "Corps": 3, "Special Forces": 4, "Support": 5, "Heavy": 6}
        units_sorted = sorted(units, key=lambda x: order.get(x["rank"], 99))

        data = []
        for u in units_sorted:
            data.append({'text': u['name'], 'points': u['points']})
        self.rv_units.data = data

    def open_unit_config(self, unit_name):
        if not self.current_faction: return
        unit_data = next((u for u in self.db.units[self.current_faction] if u["name"] == unit_name), None)
        if not unit_data: return

        # Popup Content
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Header
        content.add_widget(Label(text=f"{unit_name} ({unit_data['points']} Pkt)", size_hint_y=None, height='30dp', bold=True))

        # ScrollView for Upgrades
        from kivy.uix.scrollview import ScrollView
        scroll = ScrollView()
        upgrades_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=5)
        upgrades_layout.bind(minimum_height=upgrades_layout.setter('height'))

        selectors = []

        for slot in unit_data["slots"]:
            row = BoxLayout(size_hint_y=None, height='40dp')
            row.add_widget(Label(text=f"{slot}:", size_hint_x=0.3))

            # Get valid upgrades
            valid_upgrades = self.db.get_valid_upgrades(slot, unit_name, self.current_faction)

            # Spinner values
            options = ["-"]
            upg_map = {}
            for upg in valid_upgrades:
                txt = f"{upg['name']} ({upg['points']})"
                options.append(txt)
                upg_map[txt] = upg

            spinner = Spinner(text="-", values=options, size_hint_x=0.7)
            row.add_widget(spinner)
            upgrades_layout.add_widget(row)

            selectors.append({'spinner': spinner, 'map': upg_map})

        scroll.add_widget(upgrades_layout)
        content.add_widget(scroll)

        # Add Button
        btn_add = Button(text="Hinzufügen", size_hint_y=None, height='50dp', background_color=(0, 1, 0, 1))
        content.add_widget(btn_add)

        popup = Popup(title="Einheit Konfigurieren", content=content, size_hint=(0.9, 0.9))

        def confirm(instance):
            total_cost = unit_data["points"]
            chosen_upgrades_list = []
            base_minis = unit_data.get("minis", 1)
            extra_minis = 0

            for sel in selectors:
                val = sel['spinner'].text
                if val != "-":
                    upg = sel['map'][val]
                    total_cost += upg['points']
                    chosen_upgrades_list.append(val)
                    if upg.get("adds_mini"):
                        extra_minis += 1

            self.current_army_list.append({
                "name": unit_name,
                "upgrades": chosen_upgrades_list,
                "points": total_cost,
                "base_points": unit_data["points"],
                "minis": base_minis + extra_minis
            })
            self.refresh_army_view()
            popup.dismiss()
            # Switch to list tab
            self.tabs.switch_to(self.tabs.tab_list[0] if self.tabs.tab_list[0].text == "Meine Liste" else self.tabs.tab_list[1])

        btn_add.bind(on_release=confirm)
        popup.open()

    def refresh_army_view(self):
        self.total_points = 0
        data = []
        for u in self.current_army_list:
            upg_str = ", ".join(u["upgrades"]) if u["upgrades"] else "-"
            data.append({
                'text': u['name'],
                'details': upg_str,
                'points': u['points']
            })
            self.total_points += u['points']

        self.rv_army.data = data
        self.lbl_points.text = f"{self.total_points} / 800"
        self.lbl_points.color = (1, 0, 0, 1) if self.total_points > 800 else (1, 1, 1, 1)

    def remove_unit(self, index):
        if index is not None and 0 <= index < len(self.current_army_list):
            del self.current_army_list[index]
            self.refresh_army_view()

    def save_army_dialog(self):
        # Since we don't have standard OS dialogs easily on Android without Plyer,
        # we'll implement a simple Popup with a TextInput for filename.

        content = BoxLayout(orientation='vertical', padding=10, spacing=10)

        ti_name = Factory.TextInput(text="MeineArmee", multiline=False, size_hint_y=None, height='40dp')
        content.add_widget(Label(text="Name der Liste:", size_hint_y=None, height='30dp'))
        content.add_widget(ti_name)

        btn_save = Button(text="Speichern", size_hint_y=None, height='50dp')
        content.add_widget(btn_save)

        popup = Popup(title="Armee speichern", content=content, size_hint=(0.8, 0.4))

        def do_save(instance):
            name = ti_name.text
            if not name: return
            if not name.endswith(".json"): name += ".json"

            faction = self.current_faction or "Unbekannt"
            save_dir = os.path.join(self.base_dir, faction)
            if not os.path.exists(save_dir): os.makedirs(save_dir)

            file_path = os.path.join(save_dir, name)

            data = {
                "faction": faction,
                "total_points": self.total_points,
                "army": self.current_army_list,
                "command_cards": self.current_command_cards
            }

            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                # Toast? or Popup
                # Factory.Popup(title="Info", content=Label(text="Gespeichert!"), size_hint=(0.5, 0.3)).open()
            except Exception as e:
                logging.error(f"Save failed: {e}")

            popup.dismiss()

        btn_save.bind(on_release=do_save)
        popup.open()

    def load_army_dialog(self):
        # Simple File Chooser Popup
        content = BoxLayout(orientation='vertical')

        from kivy.uix.filechooser import FileChooserListView

        # Start at base_dir
        fc = FileChooserListView(path=self.base_dir, filters=['*.json'])
        content.add_widget(fc)

        btn_load = Button(text="Laden", size_hint_y=None, height='50dp')
        content.add_widget(btn_load)

        popup = Popup(title="Armee laden", content=content, size_hint=(0.9, 0.9))

        def do_load(instance):
            if not fc.selection: return
            file_path = fc.selection[0]

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                self.current_faction = data.get("faction", "")
                self.spinner_faction.text = self.current_faction
                self.current_army_list = data.get("army", [])
                self.current_command_cards = data.get("command_cards", [])

                self.update_unit_list()
                self.refresh_army_view()

            except Exception as e:
                logging.error(f"Load failed: {e}")

            popup.dismiss()

        btn_load.bind(on_release=do_load)
        popup.open()

    def export_to_clipboard(self):
        text = f"STAR WARS LEGION LISTE\nFraktion: {self.current_faction}\nGesamtpunkte: {self.total_points}\n"
        text += "="*40 + "\n\n"

        for unit in self.current_army_list:
            text += f"• {unit['name']} ({unit['points']} Pkt)\n"
            if unit['upgrades']:
                for upg in unit['upgrades']:
                    text += f"   - {upg}\n"
            text += "\n"

        Clipboard.copy(text)
        # Feedback?

    def open_deck_builder(self):
        if not self.current_faction: return

        # Popup for deck building
        content = BoxLayout(orientation='vertical', padding=5)

        # Status Label
        lbl_status = Label(text="Gewählt: 0/7", size_hint_y=None, height='30dp')
        content.add_widget(lbl_status)

        # Scrollable List of Checkboxes
        from kivy.uix.scrollview import ScrollView
        scroll = ScrollView()
        list_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=2)
        list_layout.bind(minimum_height=list_layout.setter('height'))

        all_cards = self.db.get_command_cards(self.current_faction)
        all_cards.sort(key=lambda x: x.get("pips", 0))

        # Temporary selection logic
        temp_selection = list(self.current_command_cards)

        # Helper to check if card is in temp_selection (by name)
        def is_selected(card):
            return any(c['name'] == card['name'] for c in temp_selection)

        def on_checkbox(card, active):
            if active:
                if len(temp_selection) < 7 and not is_selected(card):
                    temp_selection.append(card)
            else:
                # Remove
                # Need to find index
                for i, c in enumerate(temp_selection):
                    if c['name'] == card['name']:
                        del temp_selection[i]
                        break

            lbl_status.text = f"Gewählt: {len(temp_selection)}/7"

        for card in all_cards:
            row = BoxLayout(size_hint_y=None, height='40dp')
            row.add_widget(Label(text=f"{card['name']} ({card['pips']}•)", size_hint_x=0.8, halign='left', valign='middle', text_size=(None, None)))

            cb = Factory.CheckBox(active=is_selected(card), size_hint_x=0.2)
            # Bind carefully using closure default arg
            cb.bind(active=lambda instance, val, c=card: on_checkbox(c, val))
            row.add_widget(cb)

            list_layout.add_widget(row)

        scroll.add_widget(list_layout)
        content.add_widget(scroll)

        btn_done = Button(text="Fertig", size_hint_y=None, height='50dp')
        content.add_widget(btn_done)

        popup = Popup(title="Kommandokarten", content=content, size_hint=(0.9, 0.9))

        def done(instance):
            self.current_command_cards = temp_selection
            popup.dismiss()

        btn_done.bind(on_release=done)
        popup.open()

def dp(val):
    from kivy.metrics import dp as kivy_dp
    return kivy_dp(val)
