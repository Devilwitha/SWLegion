
class LegionDatabase:
    def __init__(self):
        # ---------------------------------------------------------------------
        # 1. UPGRADE-LISTE
        # ---------------------------------------------------------------------
        self.upgrades = [
            # --- MACHT (FORCE) ---
            {"name": "Machtschub (Force Push)", "type": "Force", "points": 10, "restricted_to": None},
            {"name": "Machtreflexe", "type": "Force", "points": 5, "restricted_to": None},
            {"name": "Säbelwurf", "type": "Force", "points": 5, "restricted_to": None},
            {"name": "Machtwürgen", "type": "Force", "points": 5, "restricted_to": ["Dunkle Seite", "Galaktisches Imperium", "Separatistenallianz"]},
            {"name": "Jedi-Gedankentrick", "type": "Force", "points": 5, "restricted_to": ["Helle Seite", "Rebellenallianz", "Galaktische Republik"]},

            # --- KOMMANDO (COMMAND) ---
            {"name": "Aggressive Taktiken", "type": "Command", "points": 15, "restricted_to": None},
            {"name": "Führungsqualitäten", "type": "Command", "points": 5, "restricted_to": None},
            {"name": "Strenge Befehle", "type": "Command", "points": 5, "restricted_to": None},
            {"name": "Improvisierte Befehle", "type": "Command", "points": 5, "restricted_to": None},

            # --- AUSRÜSTUNG (GEAR) ---
            {"name": "Zielausrüstung (Targeting Scopes)", "type": "Gear", "points": 4, "restricted_to": None},
            {"name": "Kletterhaken", "type": "Gear", "points": 1, "restricted_to": None},
            {"name": "Aufklärungsdaten (Recon Intel)", "type": "Gear", "points": 2, "restricted_to": None},
            {"name": "Stim-Packs", "type": "Gear", "points": 8, "restricted_to": None},
            {"name": "Notfall-Stims", "type": "Gear", "points": 8, "restricted_to": None},

            # --- TRAINING ---
            {"name": "Zähigkeit (Tenacity)", "type": "Training", "points": 4, "restricted_to": None},
            {"name": "Jäger (Hunter)", "type": "Training", "points": 6, "restricted_to": None},
            {"name": "Entschlossenheit (Duck and Cover)", "type": "Training", "points": 2, "restricted_to": None},
            {"name": "Überblick (Situational Awareness)", "type": "Training", "points": 2, "restricted_to": None},

            # --- KOMMUNIKATION (COMMS) ---
            {"name": "HQ-Uplink", "type": "Comms", "points": 10, "restricted_to": None},
            {"name": "Langstrecken-Comlink", "type": "Comms", "points": 5, "restricted_to": None},
            {"name": "Komms-Störsender", "type": "Comms", "points": 5, "restricted_to": None},

            # --- GRANATEN (GRENADES) ---
            {"name": "Erschütterungsgranaten", "type": "Grenades", "points": 3, "restricted_to": None},
            {"name": "Fragmentgranaten", "type": "Grenades", "points": 5, "restricted_to": None},
            {"name": "Impact-Granaten", "type": "Grenades", "points": 3, "restricted_to": None},

            # --- SCHWERE WAFFEN (IMPERIUM) ---
            {"name": "DLT-19 Stormtrooper", "type": "Heavy Weapon", "points": 20, "restricted_to": ["Stormtroopers"]},
            {"name": "HH-12 Stormtrooper", "type": "Heavy Weapon", "points": 16, "restricted_to": ["Stormtroopers"]},
            {"name": "T-21B Shoretrooper", "type": "Heavy Weapon", "points": 32, "restricted_to": ["Shoretroopers"]},
            {"name": "RT-97C (Snowtrooper)", "type": "Heavy Weapon", "points": 24, "restricted_to": ["Snowtroopers"]},
            {"name": "DLT-19D (Death Trooper)", "type": "Heavy Weapon", "points": 34, "restricted_to": ["Imperial Death Troopers"]},

            # --- SCHWERE WAFFEN (REBELLEN) ---
            {"name": "Z-6 Trooper", "type": "Heavy Weapon", "points": 20, "restricted_to": ["Rebel Troopers"]},
            {"name": "MPL-57 Ion Trooper", "type": "Heavy Weapon", "points": 18, "restricted_to": ["Rebel Troopers"]},
            {"name": "CM-O/93 (Veterans)", "type": "Heavy Weapon", "points": 26, "restricted_to": ["Rebel Veterans"]},
            {"name": "Sniper (Commandos)", "type": "Heavy Weapon", "points": 28, "restricted_to": ["Rebel Commandos"]},

            # --- SCHWERE WAFFEN (SEPARATISTEN) ---
            {"name": "E-5C B1 Trooper", "type": "Heavy Weapon", "points": 16, "restricted_to": ["B1 Battle Droids"]},
            {"name": "E-60R B1 Trooper", "type": "Heavy Weapon", "points": 18, "restricted_to": ["B1 Battle Droids"]},
            {"name": "ACM B2 Trooper", "type": "Heavy Weapon", "points": 24, "restricted_to": ["B2 Super Battle Droids"]},
            {"name": "B2-HA Trooper", "type": "Heavy Weapon", "points": 30, "restricted_to": ["B2 Super Battle Droids"]},

            # --- SCHWERE WAFFEN (REPUBLIK) ---
            {"name": "Z-6 Phase I Clone", "type": "Heavy Weapon", "points": 23, "restricted_to": ["Phase I Clone Troopers"]},
            {"name": "DC-15 Phase I Clone", "type": "Heavy Weapon", "points": 26, "restricted_to": ["Phase I Clone Troopers"]},
            {"name": "RPS-6 Phase I Clone", "type": "Heavy Weapon", "points": 21, "restricted_to": ["Phase I Clone Troopers"]},
            {"name": "Z-6 Phase II Clone", "type": "Heavy Weapon", "points": 27, "restricted_to": ["Phase II Clone Troopers"]},
            {"name": "Mortar Trooper", "type": "Heavy Weapon", "points": 18, "restricted_to": ["Phase II Clone Troopers"]},

            # --- PILOTEN ---
            {"name": "Imperialer Hammer-Pilot", "type": "Pilot", "points": 10, "restricted_to": ["Galaktisches Imperium"]},
            {"name": "Wedge Antilles", "type": "Pilot", "points": 5, "restricted_to": ["Rebellenallianz"]},
            {"name": "Ryder Azadi", "type": "Pilot", "points": 5, "restricted_to": ["Rebellenallianz"]},
        ]

        # ---------------------------------------------------------------------
        # 2. EINHEITEN-LISTE (Erweitert mit Kampf-Stats)
        # ---------------------------------------------------------------------
        # Erklärung Keys:
        # speed: 1, 2 oder 3
        # defense: "Red" oder "White"
        # surge: {"attack": "hit"|"crit"|None, "defense": "block"|None}
        # weapons: Liste von Dictionaries {"name", "range": [min, max], "dice": {"red":x, "black":y, "white":z}, "keywords": []}

        self.units = {
            "Galaktisches Imperium": [
                {
                    "name": "Darth Vader (Commander)", "points": 190, "rank": "Commander", "hp": 8, "courage": "-",
                    "slots": ["Force", "Force", "Command"], "info": "Deflect, Immune: Pierce",
                    "speed": 1, "defense": "Red", "surge": {"attack": None, "defense": None}, # Vader hat keine Surges, aber Konversion durch Karten/Keywords
                    "weapons": [{"name": "Vader's Lightsaber", "range": [0, 1], "dice": {"red": 6, "black": 0, "white": 0}, "keywords": ["Impact 3", "Pierce 3"]}]
                },
                {
                    "name": "Imperator Palpatine", "points": 190, "rank": "Commander", "hp": 5, "courage": "-",
                    "slots": ["Force", "Force", "Force", "Command"], "info": "Pulling the Strings",
                    "speed": 1, "defense": "Red", "surge": {"attack": "crit", "defense": "block"},
                    "weapons": [{"name": "Force Lightning", "range": [1, 2], "dice": {"red": 0, "black": 6, "white": 0}, "keywords": ["Pierce 2", "Suppressive"]}]
                },
                {
                    "name": "General Veers", "points": 75, "rank": "Commander", "hp": 5, "courage": 2,
                    "slots": ["Command", "Gear"], "info": "Spotter 2, Inspire 1",
                    "speed": 2, "defense": "Red", "surge": {"attack": "crit", "defense": "block"},
                    "weapons": [{"name": "E-11 Blaster Rifle", "range": [1, 3], "dice": {"red": 0, "black": 0, "white": 3}, "keywords": ["Pierce 1"]}]
                },
                {
                    "name": "Iden Versio", "points": 100, "rank": "Commander", "hp": 6, "courage": 3,
                    "slots": ["Training", "Gear", "Armament", "Comms"], "info": "Loadout, Marksman, Nimble",
                    "speed": 2, "defense": "Red", "surge": {"attack": "crit", "defense": "block"},
                    "weapons": [{"name": "TL-50 Repeater", "range": [1, 3], "dice": {"red": 0, "black": 2, "white": 2}, "keywords": ["Impact 1"]}]
                },
                {
                    "name": "Stormtroopers", "points": 44, "rank": "Corps", "hp": 1, "courage": 1,
                    "slots": ["Heavy Weapon", "Personnel", "Gear", "Grenades"], "info": "Precise 1",
                    "speed": 2, "defense": "Red", "surge": {"attack": "hit", "defense": None},
                    "weapons": [{"name": "E-11 Blaster Rifle", "range": [1, 3], "dice": {"red": 0, "black": 0, "white": 3}, "keywords": []}]
                },
                {
                    "name": "Shoretroopers", "points": 52, "rank": "Corps", "hp": 1, "courage": 1,
                    "slots": ["Heavy Weapon", "Personnel", "Gear", "Grenades"], "info": "Target 1, Coordinate",
                    "speed": 2, "defense": "Red", "surge": {"attack": None, "defense": None},
                    "weapons": [{"name": "E-22 Blaster Rifle", "range": [1, 3], "dice": {"red": 0, "black": 1, "white": 2}, "keywords": []}]
                },
                {
                    "name": "Snowtroopers", "points": 44, "rank": "Corps", "hp": 1, "courage": 1,
                    "slots": ["Heavy Weapon", "Personnel", "Gear", "Grenades"], "info": "Steady",
                    "speed": 1, "defense": "Red", "surge": {"attack": "hit", "defense": None},
                    "weapons": [{"name": "E-11 Blaster Rifle", "range": [1, 3], "dice": {"red": 0, "black": 0, "white": 3}, "keywords": []}]
                },
                {
                    "name": "Imperial Death Troopers", "points": 72, "rank": "Special Forces", "hp": 1, "courage": 2,
                    "slots": ["Heavy Weapon", "Training", "Comms", "Gear", "Grenades"], "info": "Disciplined 1, Precise 2",
                    "speed": 2, "defense": "Red", "surge": {"attack": "hit", "defense": None},
                    "weapons": [{"name": "SE-14r Light Blaster", "range": [1, 2], "dice": {"red": 0, "black": 0, "white": 2}, "keywords": []},
                                {"name": "E-11D Blaster Rifle", "range": [1, 3], "dice": {"red": 0, "black": 2, "white": 0}, "keywords": []}]
                },
                {
                    "name": "Scout Troopers (Strike Team)", "points": 20, "rank": "Special Forces", "hp": 1, "courage": 2,
                    "slots": ["Heavy Weapon", "Training", "Gear", "Grenades"], "info": "Low Profile, Scout 1",
                    "speed": 2, "defense": "White", "surge": {"attack": "hit", "defense": "block"},
                    "weapons": [{"name": "EC-17 Hold-out Blaster", "range": [1, 2], "dice": {"red": 0, "black": 2, "white": 0}, "keywords": []}]
                },
                {
                    "name": "74-Z Speeder Bikes", "points": 70, "rank": "Support", "hp": 3, "courage": 2,
                    "slots": ["Comms"], "info": "Cover 1, Speeder 1",
                    "speed": 3, "defense": "White", "surge": {"attack": "crit", "defense": "block"},
                    "weapons": [{"name": "Ax-20 Blaster Cannon", "range": [1, 3], "dice": {"red": 1, "black": 1, "white": 1}, "keywords": ["Fixed: Front", "Impact 1"]}]
                },
                {
                    "name": "Dewback Rider", "points": 70, "rank": "Support", "hp": 6, "courage": 2,
                    "slots": ["Training", "Comms", "Armament"], "info": "Armor 1, Relentless",
                    "speed": 1, "defense": "Red", "surge": {"attack": "hit", "defense": None},
                    "weapons": [{"name": "Shock Prod", "range": [0, 1], "dice": {"red": 1, "black": 0, "white": 2}, "keywords": ["Suppressive"]},
                                {"name": "T-21 Blaster Rifle", "range": [1, 3], "dice": {"red": 0, "black": 0, "white": 4}, "keywords": ["Critical 1"]}]
                },
                {
                    "name": "AT-ST", "points": 155, "rank": "Heavy", "hp": 11, "courage": 8,
                    "slots": ["Pilot", "Hardpoint", "Hardpoint", "Comms"], "info": "Armor, Arsenal 2",
                    "speed": 2, "defense": "White", "surge": {"attack": "hit", "defense": "block"},
                    "weapons": [{"name": "MS-4 Twin Blaster Cannon", "range": [1, 4], "dice": {"red": 2, "black": 2, "white": 2}, "keywords": ["Fixed: Front", "Impact 3"]}]
                },
                {
                    "name": "Boba Fett (Operative)", "points": 120, "rank": "Operative", "hp": 5, "courage": 3,
                    "slots": ["Training", "Training", "Gear", "Gear", "Comms"], "info": "Bounty, Jump 2, Impervious, Arsenal 2",
                    "speed": 2, "defense": "Red", "surge": {"attack": "crit", "defense": "block"},
                    "weapons": [
                        {"name": "EE-3 Carbine (Custom)", "range": [1, 3], "dice": {"red": 3, "black": 0, "white": 3}, "keywords": ["Pierce 1", "Sharpshooter 2"]},
                        {"name": "Wrist Rocket", "range": [1, 2], "dice": {"red": 0, "black": 2, "white": 0}, "keywords": ["Impact 1"]}
                    ]
                },
            ],
            "Rebellenallianz": [
                {
                    "name": "Luke Skywalker (Commander)", "points": 160, "rank": "Commander", "hp": 6, "courage": 3,
                    "slots": ["Force", "Force", "Gear"], "info": "Jump 1, Charge, Deflect",
                    "speed": 2, "defense": "Red", "surge": {"attack": "crit", "defense": None},
                    "weapons": [{"name": "Anakin's Lightsaber", "range": [0, 1], "dice": {"red": 0, "black": 6, "white": 0}, "keywords": ["Impact 2", "Pierce 2"]}]
                },
                {
                    "name": "Leia Organa", "points": 85, "rank": "Commander", "hp": 4, "courage": 2,
                    "slots": ["Command", "Gear"], "info": "Inspire 2, Nimble, Take Cover 2",
                    "speed": 2, "defense": "White", "surge": {"attack": "crit", "defense": "block"},
                    "weapons": [{"name": "Defender Sporting Blaster", "range": [1, 3], "dice": {"red": 0, "black": 3, "white": 0}, "keywords": ["Pierce 1", "Sharpshooter 1"]}]
                },
                {
                    "name": "Han Solo", "points": 100, "rank": "Commander", "hp": 6, "courage": 2,
                    "slots": ["Command", "Training", "Gear"], "info": "Gunslinger, Low Profile",
                    "speed": 2, "defense": "White", "surge": {"attack": "crit", "defense": "block"},
                    "weapons": [{"name": "DL-44 Blaster Pistol", "range": [1, 2], "dice": {"red": 2, "black": 0, "white": 0}, "keywords": ["Pierce 1"]}]
                },
                {
                    "name": "Rebel Troopers", "points": 40, "rank": "Corps", "hp": 1, "courage": 1,
                    "slots": ["Heavy Weapon", "Personnel", "Gear", "Grenades"], "info": "Nimble",
                    "speed": 2, "defense": "White", "surge": {"attack": "crit", "defense": "block"},
                    "weapons": [{"name": "A-280 Blaster Rifle", "range": [1, 3], "dice": {"red": 0, "black": 1, "white": 0}, "keywords": []}]
                },
                {
                    "name": "Rebel Veterans", "points": 48, "rank": "Corps", "hp": 1, "courage": 1,
                    "slots": ["Heavy Weapon", "Personnel", "Gear", "Grenades"], "info": "Defend 1, Coordinate",
                    "speed": 2, "defense": "White", "surge": {"attack": "crit", "defense": "block"},
                    "weapons": [{"name": "A-280 Blaster Rifle", "range": [1, 3], "dice": {"red": 0, "black": 1, "white": 0}, "keywords": []}]
                },
                {
                    "name": "Rebel Commandos", "points": 48, "rank": "Special Forces", "hp": 1, "courage": 2,
                    "slots": ["Heavy Weapon", "Training", "Gear", "Grenades"], "info": "Low Profile, Scout 2",
                    "speed": 2, "defense": "White", "surge": {"attack": "crit", "defense": "block"},
                    "weapons": [{"name": "A-280 Blaster Rifle", "range": [1, 3], "dice": {"red": 0, "black": 1, "white": 0}, "keywords": []}]
                },
                {
                    "name": "Wookiee Warriors", "points": 69, "rank": "Special Forces", "hp": 3, "courage": 2,
                    "slots": ["Heavy Weapon", "Training", "Training", "Gear", "Grenades"], "info": "Charge, Duelist, Indomitable",
                    "speed": 2, "defense": "White", "surge": {"attack": "hit", "defense": None},
                    "weapons": [{"name": "Ryyk Blades", "range": [0, 1], "dice": {"red": 0, "black": 2, "white": 0}, "keywords": []},
                                {"name": "Kashyyyk Pistol", "range": [1, 2], "dice": {"red": 0, "black": 1, "white": 1}, "keywords": []}]
                },
                {
                    "name": "AT-RT", "points": 55, "rank": "Support", "hp": 6, "courage": 4,
                    "slots": ["Hardpoint", "Comms"], "info": "Armor, Climbing Vehicle",
                    "speed": 2, "defense": "White", "surge": {"attack": "crit", "defense": "block"},
                    "weapons": [{"name": "Grappling Claws", "range": [0, 1], "dice": {"red": 3, "black": 0, "white": 0}, "keywords": []}]
                },
                {
                    "name": "T-47 Airspeeder", "points": 130, "rank": "Heavy", "hp": 7, "courage": 5,
                    "slots": ["Pilot", "Hardpoint", "Comms"], "info": "Armor, Arsenal 2, Speeder 2",
                    "speed": 3, "defense": "White", "surge": {"attack": "crit", "defense": "block"},
                    "weapons": [{"name": "Ap/11 Double Laser Cannon", "range": [1, 3], "dice": {"red": 3, "black": 3, "white": 0}, "keywords": ["Fixed: Front", "Impact 3"]}]
                },
            ],
            "Separatistenallianz": [
                {
                    "name": "General Grievous", "points": 155, "rank": "Commander", "hp": 8, "courage": 2,
                    "slots": ["Command", "Training", "Gear", "Armament"], "info": "Arsenal 2, Block, Jedi Hunter",
                    "speed": 2, "defense": "Red", "surge": {"attack": "crit", "defense": None},
                    "weapons": [{"name": "Trophy Lightsabers", "range": [0, 1], "dice": {"red": 2, "black": 2, "white": 0}, "keywords": ["Pierce 1"]},
                                {"name": "DT-57 Annihilator", "range": [1, 2], "dice": {"red": 1, "black": 2, "white": 0}, "keywords": ["Pierce 1"]}]
                },
                {
                    "name": "Count Dooku", "points": 195, "rank": "Commander", "hp": 5, "courage": "-",
                    "slots": ["Force", "Force", "Force", "Command"], "info": "Cunning, Deflect, Immune: Pierce",
                    "speed": 2, "defense": "Red", "surge": {"attack": "crit", "defense": "block"},
                    "weapons": [{"name": "Dooku's Lightsaber", "range": [0, 1], "dice": {"red": 5, "black": 0, "white": 0}, "keywords": ["Pierce 2", "Impact 2"]}]
                },
                {
                    "name": "Super Tactical Droid", "points": 90, "rank": "Commander", "hp": 5, "courage": 2,
                    "slots": ["Command", "Command", "Comms", "Gear"], "info": "Strategist 1, Direct: AI",
                    "speed": 2, "defense": "Red", "surge": {"attack": "crit", "defense": "block"},
                    "weapons": [{"name": "E-5 Blaster Rifle", "range": [1, 3], "dice": {"red": 0, "black": 0, "white": 3}, "keywords": []}]
                },
                {
                    "name": "B1 Battle Droids", "points": 38, "rank": "Corps", "hp": 1, "courage": 1,
                    "slots": ["Heavy Weapon", "Personnel", "Comms", "Electrobinoculars"], "info": "AI: Attack, Coordinate: Droid",
                    "speed": 2, "defense": "White", "surge": {"attack": None, "defense": None},
                    "weapons": [{"name": "E-5 Blaster Rifle", "range": [1, 3], "dice": {"red": 0, "black": 0, "white": 1}, "keywords": []}]
                },
                {
                    "name": "B2 Super Battle Droids", "points": 45, "rank": "Corps", "hp": 2, "courage": 1,
                    "slots": ["Heavy Weapon", "Personnel", "Comms"], "info": "AI: Attack, Armor 1",
                    "speed": 2, "defense": "White", "surge": {"attack": None, "defense": None},
                    "weapons": [{"name": "Wrist Blasters", "range": [1, 2], "dice": {"red": 0, "black": 1, "white": 1}, "keywords": []}]
                },
                {
                    "name": "BX-Series Droid Commandos", "points": 68, "rank": "Special Forces", "hp": 1, "courage": 2,
                    "slots": ["Heavy Weapon", "Training", "Gear", "Grenades", "Comms"], "info": "AI: Move/Attack, Scale, Scout 3",
                    "speed": 2, "defense": "Red", "surge": {"attack": "crit", "defense": "block"},
                    "weapons": [{"name": "E-5 Blaster Rifle", "range": [1, 3], "dice": {"red": 0, "black": 0, "white": 2}, "keywords": []}]
                },
                {
                    "name": "Droidekas", "points": 75, "rank": "Support", "hp": 4, "courage": 2,
                    "slots": ["Comms"], "info": "Shields 4, Wheel Mode",
                    "speed": 1, "defense": "White", "surge": {"attack": None, "defense": None},
                    "weapons": [{"name": "Dual Blaster Cannons", "range": [1, 3], "dice": {"red": 0, "black": 2, "white": 0}, "keywords": ["Suppressive"]}]
                },
                {
                    "name": "STAP Riders", "points": 70, "rank": "Support", "hp": 3, "courage": 2,
                    "slots": ["Comms"], "info": "Cover 1, Speeder 1",
                    "speed": 3, "defense": "White", "surge": {"attack": "hit", "defense": "block"},
                    "weapons": [{"name": "Twin Blaster Cannon", "range": [1, 3], "dice": {"red": 0, "black": 1, "white": 1}, "keywords": ["Fixed: Front"]}]
                },
                {
                    "name": "AAT Trade Federation Tank", "points": 175, "rank": "Heavy", "hp": 9, "courage": 6,
                    "slots": ["Pilot", "Hardpoint", "Comms"], "info": "Armor, Arsenal 2",
                    "speed": 1, "defense": "Red", "surge": {"attack": None, "defense": None},
                    "weapons": [{"name": "MX-8 Artillery Laser Cannon", "range": [1, 4], "dice": {"red": 2, "black": 2, "white": 0}, "keywords": ["Critical 2", "High Velocity"]}]
                },
            ],
            "Galaktische Republik": [
                {
                    "name": "Obi-Wan Kenobi", "points": 170, "rank": "Commander", "hp": 6, "courage": 3,
                    "slots": ["Force", "Force", "Command", "Training"], "info": "Guardian 3, Soresu Mastery",
                    "speed": 2, "defense": "Red", "surge": {"attack": "crit", "defense": "block"},
                    "weapons": [{"name": "Obi-Wan's Lightsaber", "range": [0, 1], "dice": {"red": 0, "black": 3, "white": 3}, "keywords": ["Impact 2", "Pierce 2"]}]
                },
                {
                    "name": "Clone Captain Rex", "points": 95, "rank": "Commander", "hp": 5, "courage": 2,
                    "slots": ["Command", "Training", "Gear", "Grenades"], "info": "Gunslinger, Scout 1, Tactical 1",
                    "speed": 2, "defense": "Red", "surge": {"attack": "crit", "defense": "block"},
                    "weapons": [{"name": "Dual DC-17 Hand Blasters", "range": [1, 2], "dice": {"red": 2, "black": 0, "white": 0}, "keywords": ["Pierce 1"]}]
                },
                {
                    "name": "Anakin Skywalker", "points": 155, "rank": "Commander", "hp": 6, "courage": 3,
                    "slots": ["Force", "Force", "Training"], "info": "Deflect, Djem So Mastery, Tempted",
                    "speed": 2, "defense": "Red", "surge": {"attack": "crit", "defense": None},
                    "weapons": [{"name": "Anakin's Lightsaber", "range": [0, 1], "dice": {"red": 4, "black": 0, "white": 0}, "keywords": ["Impact 3", "Pierce 3"]}]
                },
                {
                    "name": "Phase I Clone Troopers", "points": 52, "rank": "Corps", "hp": 1, "courage": 1,
                    "slots": ["Heavy Weapon", "Personnel", "Gear", "Grenades"], "info": "Fire Support",
                    "speed": 2, "defense": "Red", "surge": {"attack": None, "defense": None},
                    "weapons": [{"name": "DC-15A Blaster Rifle", "range": [1, 3], "dice": {"red": 0, "black": 1, "white": 0}, "keywords": []}]
                },
                {
                    "name": "Phase II Clone Troopers", "points": 60, "rank": "Corps", "hp": 1, "courage": 2,
                    "slots": ["Heavy Weapon", "Personnel", "Training", "Gear"], "info": "Reliable 1",
                    "speed": 2, "defense": "Red", "surge": {"attack": None, "defense": None},
                    "weapons": [{"name": "DC-15A Blaster Rifle", "range": [1, 3], "dice": {"red": 0, "black": 1, "white": 0}, "keywords": []}]
                },
                {
                    "name": "ARC Troopers", "points": 72, "rank": "Special Forces", "hp": 1, "courage": 2,
                    "slots": ["Heavy Weapon", "Personnel", "Training", "Gear"], "info": "Impervious, Jetpacks, Tactical 1",
                    "speed": 2, "defense": "Red", "surge": {"attack": "crit", "defense": "block"},
                    "weapons": [{"name": "DC-17 Hand Blaster", "range": [1, 2], "dice": {"red": 0, "black": 1, "white": 1}, "keywords": ["Pierce 1"]}]
                },
                {
                    "name": "BARC Speeder", "points": 55, "rank": "Support", "hp": 5, "courage": 3,
                    "slots": ["Crew", "Comms"], "info": "Cover 1, Speeder 1",
                    "speed": 3, "defense": "Red", "surge": {"attack": "hit", "defense": "block"},
                    "weapons": [{"name": "Twin Blaster Cannons", "range": [1, 3], "dice": {"red": 0, "black": 1, "white": 1}, "keywords": ["Fixed: Front"]}]
                },
                {
                    "name": "AT-RT (Republic)", "points": 55, "rank": "Support", "hp": 6, "courage": 4,
                    "slots": ["Hardpoint", "Comms"], "info": "Armor, Climbing Vehicle",
                    "speed": 2, "defense": "White", "surge": {"attack": "crit", "defense": "block"},
                    "weapons": [{"name": "Grappling Claws", "range": [0, 1], "dice": {"red": 3, "black": 0, "white": 0}, "keywords": []}]
                },
                {
                    "name": "TX-130 Saber Tank", "points": 170, "rank": "Heavy", "hp": 9, "courage": 5,
                    "slots": ["Pilot", "Hardpoint", "Comms"], "info": "Armor, Arsenal 2",
                    "speed": 2, "defense": "Red", "surge": {"attack": "crit", "defense": "block"},
                    "weapons": [{"name": "Laser Cannons", "range": [1, 3], "dice": {"red": 0, "black": 1, "white": 2}, "keywords": ["Fixed: Front", "Impact 1"]}]
                },
            ],
             "Schattenkollektiv": [
                 {
                     "name": "Maul (Shadow Collective)", "points": 160, "rank": "Commander", "hp": 6, "courage": 3,
                     "slots": ["Force", "Force", "Command", "Armament"], "info": "Juyo Mastery, Allies of Convenience",
                     "speed": 2, "defense": "Red", "surge": {"attack": "crit", "defense": "block"},
                     "weapons": [{"name": "Maul's Lightsaber", "range": [0, 1], "dice": {"red": 4, "black": 4, "white": 0}, "keywords": ["Pierce 2", "Impact 2"]}]
                 },
                 {
                     "name": "Pyke Syndicate Capo", "points": 45, "rank": "Commander", "hp": 4, "courage": 2,
                     "slots": ["Command", "Gear", "Armament"], "info": "Aid, Danger Sense 2",
                     "speed": 2, "defense": "White", "surge": {"attack": "hit", "defense": "block"},
                     "weapons": [{"name": "Blaster Pistol", "range": [1, 2], "dice": {"red": 0, "black": 1, "white": 1}, "keywords": []}]
                 },
                 {
                     "name": "Black Sun Enforcers", "points": 48, "rank": "Corps", "hp": 1, "courage": 2,
                     "slots": ["Heavy Weapon", "Personnel", "Gear", "Grenades"], "info": "Dauntless, Indomitable",
                     "speed": 2, "defense": "White", "surge": {"attack": "crit", "defense": "block"},
                     "weapons": [{"name": "Blaster Pistol", "range": [1, 2], "dice": {"red": 0, "black": 1, "white": 1}, "keywords": []}]
                 },
                 {
                     "name": "Pyke Syndicate Foot Soldiers", "points": 40, "rank": "Corps", "hp": 1, "courage": 1,
                     "slots": ["Heavy Weapon", "Personnel", "Gear", "Grenades"], "info": "Danger Sense 2, Independent: Dodge 1",
                     "speed": 2, "defense": "White", "surge": {"attack": "hit", "defense": "block"},
                     "weapons": [{"name": "Blaster Rifle", "range": [1, 3], "dice": {"red": 0, "black": 1, "white": 1}, "keywords": []}]
                },
            ]
        }

    def get_valid_upgrades(self, slot_type, unit_name, faction_name):
        """
        Filtert Upgrades basierend auf Slot, Fraktion und Einheitenbeschränkung.
        """
        valid = []
        for upg in self.upgrades:
            # 1. Passt der Typ?
            if upg["type"] != slot_type:
                continue

            # 2. Prüfe Beschränkungen (Restrictions)
            restrictions = upg.get("restricted_to")

            if restrictions is None:
                # Keine Beschränkung -> Erlaubt
                valid.append(upg)
            else:
                # Ist der Einheiten-Name ODER Fraktions-Name in der Liste?
                if unit_name in restrictions or faction_name in restrictions:
                    valid.append(upg)
                # Fraktionsübergreifende Logik (Dunkle/Helle Seite)
                elif faction_name in ["Galaktisches Imperium", "Separatistenallianz", "Schattenkollektiv"] and "Dunkle Seite" in restrictions:
                    valid.append(upg)
                elif faction_name in ["Rebellenallianz", "Galaktische Republik"] and "Helle Seite" in restrictions:
                    valid.append(upg)

        return valid
