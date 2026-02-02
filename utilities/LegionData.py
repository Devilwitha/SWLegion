import json
import os
import logging
from utilities.LegionRules import LegionRules

class LegionDatabase:
    def __init__(self):
        logging.info("Initializing LegionDatabase...")
        self.rules = LegionRules
        self.units = {}
        self.upgrades = []
        self.command_cards = []
        self.battle_cards = []

        # --- TRANSLATION MAP (Generated from previous data) ---
        self.translations = {
            "factions": {
                "imperials": "Galaktisches Imperium",
                "rebels": "Rebellenallianz",
                "separatists": "Separatistenallianz",
                "republic": "Galaktische Republik",
                "shadow-collective": "Schattenkollektiv",
                "neutral": "Neutral"
            },
            "ranks": {
                "commander": "Commander",
                "operative": "Operative",
                "corps": "Corps",
                "special-forces": "Special Forces",
                "support": "Support",
                "heavy": "Heavy"
            },
            "types": {
                "force": "Force",
                "command": "Command",
                "gear": "Gear",
                "training": "Training",
                "comms": "Comms",
                "grenades": "Grenades",
                "heavy-weapon": "Heavy Weapon",
                "personnel": "Personnel",
                "pilot": "Pilot",
                "hard-point": "Hardpoint",
                "armament": "Armament",
                "generator": "Generator",
                "crew": "Crew"
            }
        }

        # Explicit Name Mapping for known units/upgrades
        self.name_map = {
             # Units
            "74-z-speeder-bikes": "74-Z Speeder Bikes",
            "at-st": "AT-ST",
            "boba-fett": "Boba Fett (Operative)",
            "darth-vader": "Darth Vader (Commander)",
            "general-veers": "General Veers",
            "snowtroopers": "Snowtroopers",
            "stormtroopers": "Stormtroopers",
            "at-rt": "AT-RT",
            "han-solo": "Han Solo",
            "leia-organa": "Leia Organa",
            "luke-skywalker": "Luke Skywalker (Commander)",
            "rebel-troopers": "Rebel Troopers",
            "t-47-airspeeder": "T-47 Airspeeder",

            # Upgrades
            "force-push": "Machtschub (Force Push)",
            "recon-intel": "Aufklärungsdaten (Recon Intel)",
            "targeting-scopes": "Zielausrüstung (Targeting Scopes)",
            "duck-and-cover": "Entschlossenheit (Duck and Cover)",
            "hunter": "Jäger (Hunter)",
            "tenacity": "Zähigkeit (Tenacity)"
        }

        # --- LEGACY DATA (Missing in catalog.json) ---
        # Data for Separatists, Republic, Shadow Collective, etc.
        self.legacy_units_json = """
        {
            "Separatistenallianz": [
                {"name": "General Grievous", "points": 155, "rank": "Commander", "hp": 8, "courage": 2, "slots": ["Command", "Training", "Gear", "Armament"], "info": "Arsenal 2, Block, Jedi Hunter", "minis": 1, "speed": 2, "defense": "Red", "surge": {"attack": "crit", "defense": null}, "weapons": [{"name": "Trophy Lightsabers", "range": [0, 1], "dice": {"red": 2, "black": 2, "white": 0}, "keywords": ["Pierce 1"]}, {"name": "DT-57 Annihilator", "range": [1, 2], "dice": {"red": 1, "black": 2, "white": 0}, "keywords": ["Pierce 1"]}]},
                {"name": "Count Dooku", "points": 195, "rank": "Commander", "hp": 5, "courage": "-", "slots": ["Force", "Force", "Force", "Command"], "info": "Cunning, Deflect, Immune: Pierce", "minis": 1, "speed": 2, "defense": "Red", "surge": {"attack": "crit", "defense": "block"}, "weapons": [{"name": "Dooku's Lightsaber", "range": [0, 1], "dice": {"red": 5, "black": 0, "white": 0}, "keywords": ["Pierce 2", "Impact 2"]}]},
                {"name": "Super Tactical Droid", "points": 90, "rank": "Commander", "hp": 5, "courage": 2, "slots": ["Command", "Command", "Comms", "Gear"], "info": "Strategist 1, Direct: AI", "minis": 1, "speed": 2, "defense": "Red", "surge": {"attack": "crit", "defense": "block"}, "weapons": [{"name": "E-5 Blaster Rifle", "range": [1, 3], "dice": {"red": 0, "black": 0, "white": 3}, "keywords": []}]},
                {"name": "B1 Battle Droids", "points": 38, "rank": "Corps", "hp": 1, "courage": 1, "slots": ["Heavy Weapon", "Personnel", "Comms", "Electrobinoculars"], "info": "AI: Attack, Coordinate: Droid", "minis": 6, "speed": 2, "defense": "White", "surge": {"attack": null, "defense": null}, "weapons": [{"name": "E-5 Blaster Rifle", "range": [1, 3], "dice": {"red": 0, "black": 0, "white": 1}, "keywords": []}]},
                {"name": "B2 Super Battle Droids", "points": 45, "rank": "Corps", "hp": 2, "courage": 1, "slots": ["Heavy Weapon", "Personnel", "Comms"], "info": "AI: Attack, Armor 1", "minis": 3, "speed": 2, "defense": "White", "surge": {"attack": null, "defense": null}, "weapons": [{"name": "Wrist Blasters", "range": [1, 2], "dice": {"red": 0, "black": 1, "white": 1}, "keywords": []}]},
                {"name": "BX-Series Droid Commandos", "points": 68, "rank": "Special Forces", "hp": 1, "courage": 2, "slots": ["Heavy Weapon", "Training", "Gear", "Grenades", "Comms"], "info": "AI: Move/Attack, Scale, Scout 3", "minis": 5, "speed": 2, "defense": "Red", "surge": {"attack": "crit", "defense": "block"}, "weapons": [{"name": "E-5 Blaster Rifle", "range": [1, 3], "dice": {"red": 0, "black": 0, "white": 2}, "keywords": []}]},
                {"name": "Droidekas", "points": 75, "rank": "Support", "hp": 4, "courage": 2, "slots": ["Comms"], "info": "Shields 4, Wheel Mode", "minis": 2, "speed": 1, "defense": "White", "surge": {"attack": null, "defense": null}, "weapons": [{"name": "Dual Blaster Cannons", "range": [1, 3], "dice": {"red": 0, "black": 2, "white": 0}, "keywords": ["Suppressive"]}]},
                {"name": "STAP Riders", "points": 70, "rank": "Support", "hp": 3, "courage": 2, "slots": ["Comms"], "info": "Cover 1, Speeder 1", "minis": 2, "speed": 3, "defense": "White", "surge": {"attack": "hit", "defense": "block"}, "weapons": [{"name": "Twin Blaster Cannon", "range": [1, 3], "dice": {"red": 0, "black": 1, "white": 1}, "keywords": ["Fixed: Front"]}]},
                {"name": "AAT Trade Federation Tank", "points": 175, "rank": "Heavy", "hp": 9, "courage": 6, "slots": ["Pilot", "Hardpoint", "Comms"], "info": "Armor, Arsenal 2", "minis": 1, "speed": 1, "defense": "Red", "surge": {"attack": null, "defense": null}, "weapons": [{"name": "MX-8 Artillery Laser Cannon", "range": [1, 4], "dice": {"red": 2, "black": 2, "white": 0}, "keywords": ["Critical 2", "High Velocity"]}]}
            ],
            "Galaktische Republik": [
                {"name": "Obi-Wan Kenobi", "points": 170, "rank": "Commander", "hp": 6, "courage": 3, "slots": ["Force", "Force", "Command", "Training"], "info": "Guardian 3, Soresu Mastery", "minis": 1, "speed": 2, "defense": "Red", "surge": {"attack": "crit", "defense": "block"}, "weapons": [{"name": "Obi-Wan's Lightsaber", "range": [0, 1], "dice": {"red": 0, "black": 3, "white": 3}, "keywords": ["Impact 2", "Pierce 2"]}]},
                {"name": "Clone Captain Rex", "points": 95, "rank": "Commander", "hp": 5, "courage": 2, "slots": ["Command", "Training", "Gear", "Grenades"], "info": "Gunslinger, Scout 1, Tactical 1", "minis": 1, "speed": 2, "defense": "Red", "surge": {"attack": "crit", "defense": "block"}, "weapons": [{"name": "Dual DC-17 Hand Blasters", "range": [1, 2], "dice": {"red": 2, "black": 0, "white": 0}, "keywords": ["Pierce 1"]}]},
                {"name": "Anakin Skywalker", "points": 155, "rank": "Commander", "hp": 6, "courage": 3, "slots": ["Force", "Force", "Training"], "info": "Deflect, Djem So Mastery, Tempted", "minis": 1, "speed": 2, "defense": "Red", "surge": {"attack": "crit", "defense": null}, "weapons": [{"name": "Anakin's Lightsaber", "range": [0, 1], "dice": {"red": 4, "black": 0, "white": 0}, "keywords": ["Impact 3", "Pierce 3"]}]},
                {"name": "Phase I Clone Troopers", "points": 52, "rank": "Corps", "hp": 1, "courage": 1, "slots": ["Heavy Weapon", "Personnel", "Gear", "Grenades"], "info": "Fire Support", "minis": 4, "speed": 2, "defense": "Red", "surge": {"attack": null, "defense": null}, "weapons": [{"name": "DC-15A Blaster Rifle", "range": [1, 3], "dice": {"red": 0, "black": 1, "white": 0}, "keywords": []}]},
                {"name": "Phase II Clone Troopers", "points": 60, "rank": "Corps", "hp": 1, "courage": 2, "slots": ["Heavy Weapon", "Personnel", "Training", "Gear"], "info": "Reliable 1", "minis": 4, "speed": 2, "defense": "Red", "surge": {"attack": null, "defense": null}, "weapons": [{"name": "DC-15A Blaster Rifle", "range": [1, 3], "dice": {"red": 0, "black": 1, "white": 0}, "keywords": []}]},
                {"name": "ARC Troopers", "points": 72, "rank": "Special Forces", "hp": 1, "courage": 2, "slots": ["Heavy Weapon", "Personnel", "Training", "Gear"], "info": "Impervious, Jetpacks, Tactical 1", "minis": 4, "speed": 2, "defense": "Red", "surge": {"attack": "crit", "defense": "block"}, "weapons": [{"name": "DC-17 Hand Blaster", "range": [1, 2], "dice": {"red": 0, "black": 1, "white": 1}, "keywords": ["Pierce 1"]}]},
                {"name": "BARC Speeder", "points": 55, "rank": "Support", "hp": 5, "courage": 3, "slots": ["Crew", "Comms"], "info": "Cover 1, Speeder 1", "minis": 1, "speed": 3, "defense": "Red", "surge": {"attack": "hit", "defense": "block"}, "weapons": [{"name": "Twin Blaster Cannons", "range": [1, 3], "dice": {"red": 0, "black": 1, "white": 1}, "keywords": ["Fixed: Front"]}]},
                {"name": "AT-RT (Republic)", "points": 55, "rank": "Support", "hp": 6, "courage": 4, "slots": ["Hardpoint", "Comms"], "info": "Armor, Climbing Vehicle", "minis": 1, "speed": 2, "defense": "White", "surge": {"attack": "crit", "defense": "block"}, "weapons": [{"name": "Grappling Claws", "range": [0, 1], "dice": {"red": 3, "black": 0, "white": 0}, "keywords": []}]},
                {"name": "TX-130 Saber Tank", "points": 170, "rank": "Heavy", "hp": 9, "courage": 5, "slots": ["Pilot", "Hardpoint", "Comms"], "info": "Armor, Arsenal 2", "minis": 1, "speed": 2, "defense": "Red", "surge": {"attack": "crit", "defense": "block"}, "weapons": [{"name": "Laser Cannons", "range": [1, 3], "dice": {"red": 0, "black": 1, "white": 2}, "keywords": ["Fixed: Front", "Impact 1"]}]}
            ],
            "Schattenkollektiv": [
                 {"name": "Maul (Shadow Collective)", "points": 160, "rank": "Commander", "hp": 6, "courage": 3, "slots": ["Force", "Force", "Command", "Armament"], "info": "Juyo Mastery, Allies of Convenience", "minis": 1, "speed": 2, "defense": "Red", "surge": {"attack": "crit", "defense": "block"}, "weapons": [{"name": "Maul's Lightsaber", "range": [0, 1], "dice": {"red": 4, "black": 4, "white": 0}, "keywords": ["Pierce 2", "Impact 2"]}]},
                 {"name": "Pyke Syndicate Capo", "points": 45, "rank": "Commander", "hp": 4, "courage": 2, "slots": ["Command", "Gear", "Armament"], "info": "Aid, Danger Sense 2", "minis": 1, "speed": 2, "defense": "White", "surge": {"attack": "hit", "defense": "block"}, "weapons": [{"name": "Blaster Pistol", "range": [1, 2], "dice": {"red": 0, "black": 1, "white": 1}, "keywords": []}]},
                 {"name": "Black Sun Enforcers", "points": 48, "rank": "Corps", "hp": 1, "courage": 2, "slots": ["Heavy Weapon", "Personnel", "Gear", "Grenades"], "info": "Dauntless, Indomitable", "minis": 4, "speed": 2, "defense": "White", "surge": {"attack": "crit", "defense": "block"}, "weapons": [{"name": "Blaster Pistol", "range": [1, 2], "dice": {"red": 0, "black": 1, "white": 1}, "keywords": []}]},
                 {"name": "Pyke Syndicate Foot Soldiers", "points": 40, "rank": "Corps", "hp": 1, "courage": 1, "slots": ["Heavy Weapon", "Personnel", "Gear", "Grenades"], "info": "Danger Sense 2, Independent: Dodge 1", "minis": 4, "speed": 2, "defense": "White", "surge": {"attack": "hit", "defense": "block"}, "weapons": [{"name": "Blaster Rifle", "range": [1, 3], "dice": {"red": 0, "black": 1, "white": 1}, "keywords": []}]}
            ],
            "Galaktisches Imperium": [
                {"name": "Iden Versio", "points": 100, "rank": "Commander", "hp": 6, "courage": 3, "slots": ["Training", "Gear", "Armament", "Comms"], "info": "Loadout, Marksman, Nimble", "minis": 1, "speed": 2, "defense": "Red", "surge": {"attack": "crit", "defense": "block"}, "weapons": [{"name": "TL-50 Repeater", "range": [1, 3], "dice": {"red": 0, "black": 2, "white": 2}, "keywords": ["Impact 1"]}]},
                {"name": "Shoretroopers", "points": 52, "rank": "Corps", "hp": 1, "courage": 1, "slots": ["Heavy Weapon", "Personnel", "Gear", "Grenades"], "info": "Target 1, Coordinate", "minis": 4, "speed": 2, "defense": "Red", "surge": {"attack": null, "defense": null}, "weapons": [{"name": "E-22 Blaster Rifle", "range": [1, 3], "dice": {"red": 0, "black": 1, "white": 2}, "keywords": []}]},
                {"name": "Imperial Death Troopers", "points": 72, "rank": "Special Forces", "hp": 1, "courage": 2, "slots": ["Heavy Weapon", "Training", "Comms", "Gear", "Grenades"], "info": "Disciplined 1, Precise 2", "minis": 4, "speed": 2, "defense": "Red", "surge": {"attack": "hit", "defense": null}, "weapons": [{"name": "SE-14r Light Blaster", "range": [1, 2], "dice": {"red": 0, "black": 0, "white": 2}, "keywords": []}, {"name": "E-11D Blaster Rifle", "range": [1, 3], "dice": {"red": 0, "black": 2, "white": 0}, "keywords": []}]},
                {"name": "Dewback Rider", "points": 70, "rank": "Support", "hp": 6, "courage": 2, "slots": ["Training", "Comms", "Armament"], "info": "Armor 1, Relentless", "minis": 1, "speed": 1, "defense": "Red", "surge": {"attack": "hit", "defense": null}, "weapons": [{"name": "Shock Prod", "range": [0, 1], "dice": {"red": 1, "black": 0, "white": 2}, "keywords": ["Suppressive"]}, {"name": "T-21 Blaster Rifle", "range": [1, 3], "dice": {"red": 0, "black": 0, "white": 4}, "keywords": ["Critical 1"]}]}
            ],
            "Rebellenallianz": [
                {"name": "Rebel Veterans", "points": 48, "rank": "Corps", "hp": 1, "courage": 1, "slots": ["Heavy Weapon", "Personnel", "Gear", "Grenades"], "info": "Defend 1, Coordinate", "minis": 4, "speed": 2, "defense": "White", "surge": {"attack": "crit", "defense": "block"}, "weapons": [{"name": "A-280 Blaster Rifle", "range": [1, 3], "dice": {"red": 0, "black": 1, "white": 0}, "keywords": []}]},
                {"name": "Rebel Commandos", "points": 48, "rank": "Special Forces", "hp": 1, "courage": 2, "slots": ["Heavy Weapon", "Training", "Gear", "Grenades"], "info": "Low Profile, Scout 2", "minis": 4, "speed": 2, "defense": "White", "surge": {"attack": "crit", "defense": "block"}, "weapons": [{"name": "A-280 Blaster Rifle", "range": [1, 3], "dice": {"red": 0, "black": 1, "white": 0}, "keywords": []}]},
                {"name": "Wookiee Warriors", "points": 69, "rank": "Special Forces", "hp": 3, "courage": 2, "slots": ["Heavy Weapon", "Training", "Training", "Gear", "Grenades"], "info": "Charge, Duelist, Indomitable", "minis": 3, "speed": 2, "defense": "White", "surge": {"attack": "hit", "defense": null}, "weapons": [{"name": "Ryyk Blades", "range": [0, 1], "dice": {"red": 0, "black": 2, "white": 0}, "keywords": []}, {"name": "Kashyyyk Pistol", "range": [1, 2], "dice": {"red": 0, "black": 1, "white": 1}, "keywords": []}]}
            ]
        }
        """

        self.legacy_upgrades_json = """
        [
            {"name": "Machtreflexe", "type": "Force", "points": 5, "restricted_to": null},
            {"name": "Säbelwurf", "type": "Force", "points": 5, "restricted_to": null},
            {"name": "Machtwürgen", "type": "Force", "points": 5, "restricted_to": ["Dunkle Seite", "Galaktisches Imperium", "Separatistenallianz"]},
            {"name": "Jedi-Gedankentrick", "type": "Force", "points": 5, "restricted_to": ["Helle Seite", "Rebellenallianz", "Galaktische Republik"]},
            {"name": "Aggressive Taktiken", "type": "Command", "points": 15, "restricted_to": null},
            {"name": "Führungsqualitäten", "type": "Command", "points": 5, "restricted_to": null},
            {"name": "Strenge Befehle", "type": "Command", "points": 5, "restricted_to": null},
            {"name": "Improvisierte Befehle", "type": "Command", "points": 5, "restricted_to": null},
            {"name": "Kletterhaken", "type": "Gear", "points": 1, "restricted_to": null},
            {"name": "Stim-Packs", "type": "Gear", "points": 8, "restricted_to": null},
            {"name": "Notfall-Stims", "type": "Gear", "points": 8, "restricted_to": null},
            {"name": "Überblick (Situational Awareness)", "type": "Training", "points": 2, "restricted_to": null},
            {"name": "HQ-Uplink", "type": "Comms", "points": 10, "restricted_to": null},
            {"name": "Langstrecken-Comlink", "type": "Comms", "points": 5, "restricted_to": null},
            {"name": "Komms-Störsender", "type": "Comms", "points": 5, "restricted_to": null},
            {"name": "Erschütterungsgranaten", "type": "Grenades", "points": 3, "restricted_to": null},
            {"name": "Fragmentgranaten", "type": "Grenades", "points": 5, "restricted_to": null},
            {"name": "Impact-Granaten", "type": "Grenades", "points": 3, "restricted_to": null},
            {"name": "T-21B Shoretrooper", "type": "Heavy Weapon", "points": 32, "restricted_to": ["Shoretroopers"], "adds_mini": true},
            {"name": "DLT-19D (Death Trooper)", "type": "Heavy Weapon", "points": 34, "restricted_to": ["Imperial Death Troopers"], "adds_mini": true},
            {"name": "CM-O/93 (Veterans)", "type": "Heavy Weapon", "points": 26, "restricted_to": ["Rebel Veterans"], "adds_mini": true},
            {"name": "Sniper (Commandos)", "type": "Heavy Weapon", "points": 28, "restricted_to": ["Rebel Commandos"], "adds_mini": true},
            {"name": "E-5C B1 Trooper", "type": "Heavy Weapon", "points": 16, "restricted_to": ["B1 Battle Droids"], "adds_mini": true},
            {"name": "E-60R B1 Trooper", "type": "Heavy Weapon", "points": 18, "restricted_to": ["B1 Battle Droids"], "adds_mini": true},
            {"name": "ACM B2 Trooper", "type": "Heavy Weapon", "points": 24, "restricted_to": ["B2 Super Battle Droids"], "adds_mini": true},
            {"name": "B2-HA Trooper", "type": "Heavy Weapon", "points": 30, "restricted_to": ["B2 Super Battle Droids"], "adds_mini": true},
            {"name": "Z-6 Phase I Clone", "type": "Heavy Weapon", "points": 23, "restricted_to": ["Phase I Clone Troopers"], "adds_mini": true},
            {"name": "DC-15 Phase I Clone", "type": "Heavy Weapon", "points": 26, "restricted_to": ["Phase I Clone Troopers"], "adds_mini": true},
            {"name": "RPS-6 Phase I Clone", "type": "Heavy Weapon", "points": 21, "restricted_to": ["Phase I Clone Troopers"], "adds_mini": true},
            {"name": "Z-6 Phase II Clone", "type": "Heavy Weapon", "points": 27, "restricted_to": ["Phase II Clone Troopers"], "adds_mini": true},
            {"name": "Mortar Trooper", "type": "Heavy Weapon", "points": 18, "restricted_to": ["Phase II Clone Troopers"], "adds_mini": true},
            {"name": "Imperialer Hammer-Pilot", "type": "Pilot", "points": 10, "restricted_to": ["Galaktisches Imperium"]}
        ]
        """

        self.load_catalog()
        self.load_legacy()
        self.load_custom_units()
        self.load_custom_command_cards()
        self.load_custom_upgrades()
        self.load_custom_battle_cards()

    def load_custom_battle_cards(self):
        """Loads custom battle cards from custom_battle_cards.json."""
        if not os.path.exists("db/custom_battle_cards.json"):
            return

        try:
            logging.info("Loading custom battle cards...")
            with open("db/custom_battle_cards.json", "r", encoding="utf-8") as f:
                cards = json.load(f)

            for c in cards:
                c["is_custom"] = True
                self.battle_cards.append(c)

        except Exception as e:
            logging.error(f"Error loading custom battle cards: {e}")

    def load_custom_upgrades(self):
        """Loads custom upgrades from custom_upgrades.json."""
        if not os.path.exists("db/custom_upgrades.json"):
            return

        try:
            logging.info("Loading custom upgrades...")
            with open("db/custom_upgrades.json", "r", encoding="utf-8") as f:
                upgrades = json.load(f)

            for u in upgrades:
                u["is_custom"] = True
                self.upgrades.append(u)

        except Exception as e:
            logging.error(f"Error loading custom upgrades: {e}")

    def load_custom_command_cards(self):
        """Loads custom command cards from custom_command_cards.json."""
        if not os.path.exists("db/custom_command_cards.json"):
            return

        try:
            logging.info("Loading custom command cards...")
            with open("db/custom_command_cards.json", "r", encoding="utf-8") as f:
                cards = json.load(f)

            for c in cards:
                # Format needs to match what Army Builder expects
                # Army Builder checks 'ger_faction' or 'faction'
                # Custom cards have a LIST of factions.
                # We need to duplicate the card object for each faction to ensure simple filtering later?
                # Or just ensure get_command_cards handles it.

                # Let's adjust get_command_cards instead, but we need to store these carefully.
                # Just append them to self.command_cards with a special flag?

                c["is_custom"] = True
                self.command_cards.append(c)

        except Exception as e:
            logging.error(f"Error loading custom command cards: {e}")

    def load_custom_units(self):
        """Loads custom units from custom_units.json."""
        if not os.path.exists("db/custom_units.json"):
            return

        try:
            logging.info("Loading custom units...")
            with open("db/custom_units.json", "r", encoding="utf-8") as f:
                custom_data = json.load(f)

            for entry in custom_data:
                unit_data = entry.get("unit_data")
                factions = entry.get("factions", [])

                if not unit_data: continue

                # Mark as custom (optional, helps UI)
                unit_data["is_custom"] = True

                for faction in factions:
                    if faction not in self.units:
                        self.units[faction] = []

                    # Check for duplicates by ID or Name to allow updates
                    existing_idx = next((i for i, u in enumerate(self.units[faction]) if u.get("id") == unit_data.get("id")), -1)

                    if existing_idx >= 0:
                        self.units[faction][existing_idx] = unit_data
                    else:
                        self.units[faction].append(unit_data)

        except Exception as e:
            logging.error(f"Error loading custom units: {e}")
            print(f"Error loading custom units: {e}")

    def translate(self, category, key, default=None):
        """Translates a key using the translation map."""
        if not key: return default
        if default is None: default = key.title().replace("-", " ")
        return self.translations.get(category, {}).get(key.lower(), default)

    def load_catalog(self):
        if not os.path.exists("db/catalog.json"):
            logging.warning("db/catalog.json not found! Using internal legacy data only.")
            print("Warning: db/catalog.json not found!")
            return

        try:
            logging.info("Loading catalog.json...")
            with open("db/catalog.json", "r", encoding="utf-8") as f:
                data = json.load(f)

            # Process Units
            for u in data.get("units", []):
                eng_faction = u.get("faction")
                ger_faction = self.translate("factions", eng_faction)

                if not ger_faction:
                    continue # Skip unknown factions

                if ger_faction not in self.units:
                    self.units[ger_faction] = []

                # Convert ID to Name (use map if available)
                uid = u.get("id")
                name = self.name_map.get(uid, u.get("name"))

                rank = self.translate("ranks", u.get("rank"), u.get("rank"))

                # Convert upgrades dict to list of slots
                # Catalog: {"heavy-weapon": 1, "training": 2}
                # App: ["Heavy Weapon", "Training", "Training"]
                slots = []
                for slot_key, count in u.get("upgrades", {}).items():
                    slot_name = self.translate("types", slot_key, slot_key)
                    for _ in range(count):
                        slots.append(slot_name)

                # Convert weapons
                # Catalog weapons are complex. We need to simplify for App.
                weapons = []
                for w in u.get("weapons", []):
                    w_name = w.get("name")
                    w_range = [w.get("min_range", 0), w.get("max_range", 0)]

                    # Fix Dice schema (ensure 0 defaults)
                    raw_dice = w.get("dice", {})
                    w_dice = {
                        "red": raw_dice.get("red", 0),
                        "black": raw_dice.get("black", 0),
                        "white": raw_dice.get("white", 0)
                    }

                    # Format Weapon Keywords with values
                    w_kw_list = []
                    for k, v in w.get("keywords", {}).items():
                        key_str = k.replace("-", " ").title()

                        # Try to find German translation
                        rule_kw = self.rules.get_keyword(key_str)
                        if rule_kw and "german" in rule_kw:
                            key_str = rule_kw["german"]

                        if v and str(v) != "":
                            w_kw_list.append(f"{key_str} {v}")
                        else:
                            w_kw_list.append(key_str)

                    weapons.append({
                        "name": w_name,
                        "range": w_range,
                        "dice": w_dice,
                        "keywords": w_kw_list
                    })

                # Defense surge
                surge_def = "block" if u.get("has_defense_surge") else None
                surge_atk = u.get("attack_surge")
                if surge_atk == "critical": surge_atk = "crit"

                # Format Unit Keywords with values
                unit_kw_list = []
                for k, v in u.get("keywords", {}).items():
                    key_str = k.replace("-", " ").title()

                    # Try to find German translation
                    rule_kw = self.rules.get_keyword(key_str)
                    if rule_kw and "german" in rule_kw:
                        key_str = rule_kw["german"]

                    if v and str(v) != "":
                        unit_kw_list.append(f"{key_str} {v}")
                    else:
                        unit_kw_list.append(key_str)

                unit_dict = {
                    "name": name,
                    "points": u.get("points", 0),
                    "rank": rank,
                    "hp": u.get("wounds", 1),
                    "courage": u.get("courage", "-"),
                    "slots": slots,
                    "info": ", ".join(unit_kw_list),
                    "minis": u.get("miniatures", 1),
                    "speed": u.get("speed", 0),
                    "defense": u.get("defense", "White").title(),
                    "surge": {"attack": surge_atk, "defense": surge_def},
                    "weapons": weapons,
                    "id": uid # Store ID for internal use
                }

                self.units[ger_faction].append(unit_dict)

            # Process Upgrades
            for upg in data.get("upgrades", []):
                uid = upg.get("id")
                name = self.name_map.get(uid, upg.get("name"))

                u_type = self.translate("types", upg.get("type"))

                # Restrictions
                # Catalog has restricted_to_unit (list of IDs) or restricted_to_faction
                restrictions = []

                # Faction restriction
                res_fac = upg.get("restricted_to_faction") # "imperials"
                if res_fac:
                    tr_fac = self.translate("factions", res_fac)
                    if tr_fac: restrictions.append(tr_fac)

                # Unit restriction
                res_units = upg.get("restricted_to_unit", [])
                for ru in res_units:
                    # Resolve ID to Name from catalog data or our map
                    # Since we processed units first, we could look them up,
                    # but for now rely on name_map or raw ID if not found (ArmeeBuilder might fail to match if name differs)
                    # We try to use the Name we assigned to the unit.

                    # Quick lookup in our loaded units?
                    # Too expensive. Use name_map
                    r_name = self.name_map.get(ru["id"], ru.get("name")) # Catalog restriction objects usually just have ID?
                    # Catalog JSON: "restricted_to_unit": [{"id": "..."}]

                    # Wait, restricted_to_unit is a list of objects with ID
                    rid = ru.get("id") if isinstance(ru, dict) else ru

                    # Try to find the name we gave this unit
                    unit_name = self.name_map.get(rid)
                    if not unit_name:
                         # Fallback: Convert ID to Title Case roughly
                         unit_name = rid.replace("-", " ").title()

                    restrictions.append(unit_name)

                # Type restriction (e.g. only Heavy Vehicles) - App doesn't support this well yet, ignore or add as string?
                # App logic matches checks: "if unit_name in restrictions or faction_name in restrictions"

                if not restrictions: restrictions = None

                adds_mini = upg.get("adds_miniature", False)

                upg_dict = {
                    "name": name,
                    "type": u_type,
                    "points": upg.get("points", 0),
                    "restricted_to": restrictions,
                    "adds_mini": adds_mini,
                    "id": uid
                }
                self.upgrades.append(upg_dict)

            # Process Command Cards
            self.command_cards = []
            for cc in data.get("commandCards", []):
                eng_fac = cc.get("faction")
                ger_fac = self.translate("factions", eng_fac)
                cc['ger_faction'] = ger_fac
                self.command_cards.append(cc)

        except Exception as e:
            logging.error(f"Error loading catalog.json: {e}")
            print(f"Error loading catalog.json: {e}")

    def load_legacy(self):
        # Load legacy units
        try:
            logging.info("Loading internal legacy units...")
            leg_units = json.loads(self.legacy_units_json)
            for faction, u_list in leg_units.items():
                if faction not in self.units:
                    self.units[faction] = []

                # Check for duplicates? Or just append?
                # The user said "Mine is wrong", maybe I should prefer Legacy over Catalog if I trust legacy structure more?
                # But Catalog didn't have these units, so we are safe to append.
                # For units that exist in BOTH (like Vader), we already loaded from Catalog.
                # Legacy only contains MISSING units (Shadow Collective, Droids, Clones).
                # There is some overlap in my legacy data dump (Imperials/Rebels) because I dumped missing units.
                # Check for duplicates by name.

                existing_names = {u['name'] for u in self.units[faction]}

                for u in u_list:
                    if u['name'] not in existing_names:
                        self.units[faction].append(u)

        except Exception as e:
            print(f"Error loading legacy units: {e}")

        # Load legacy upgrades
        try:
            leg_upgrades = json.loads(self.legacy_upgrades_json)
            existing_upg_names = {u['name'] for u in self.upgrades}

            for u in leg_upgrades:
                if u['name'] not in existing_upg_names:
                     self.upgrades.append(u)

        except Exception as e:
             print(f"Error loading legacy upgrades: {e}")

    def get_valid_upgrades(self, slot_type, unit_name, faction_name):
        """
        Filtert Upgrades basierend auf Slot, Fraktion und Einheitenbeschränkung.
        """
        valid = []
        for upg in self.upgrades:
            # 1. Passt der Typ?
            # Safe comparison
            if str(upg.get("type")) != str(slot_type):
                continue

            # 2. Prüfe Beschränkungen (Restrictions)
            restrictions = upg.get("restricted_to")

            if restrictions is None or len(restrictions) == 0:
                # Keine Beschränkung -> Erlaubt
                valid.append(upg)
            else:
                # Ist der Einheiten-Name ODER Fraktions-Name in der Liste?
                # restrictions might be a list of strings

                # Normalize logic
                if unit_name in restrictions or faction_name in restrictions:
                    valid.append(upg)

                # Fraktionsübergreifende Logik (Dunkle/Helle Seite) - Catalog has "force_alignment"
                # Legacy logic:
                elif faction_name in ["Galaktisches Imperium", "Separatistenallianz", "Schattenkollektiv"] and "Dunkle Seite" in restrictions:
                    valid.append(upg)
                elif faction_name in ["Rebellenallianz", "Galaktische Republik"] and "Helle Seite" in restrictions:
                    valid.append(upg)

                # Catalog logic using IDs/Factions needs to map here if we rely on names.
                # Since we mapped restrictions to Names in load_catalog, this check should work
                # IF the unit_name passed here matches what we stored in restrictions.

        return valid

    def get_command_cards(self, faction_name):
        """Returns command cards for the given faction (and neutral ones)."""
        cards = []
        for c in self.command_cards:
            # Standard logic
            is_valid = False
            if c.get("ger_faction") == faction_name or c.get("faction") == "neutral":
                is_valid = True

            # Custom logic (list of factions)
            if c.get("is_custom"):
                factions = c.get("factions", [])
                if faction_name in factions or "Neutral" in factions:
                    is_valid = True

            if is_valid:
                cards.append(c)
        return cards
