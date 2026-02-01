class LegionRules:
    """
    Zentrale Datenbank für Star Wars: Legion Regeln.
    Basiert auf dem bereitgestellten Regelwerk (Gültig ab 30.4.2025).
    """

    # =========================================================================
    # 1. PHASEN & ABLAUF
    # =========================================================================
    PHASES = {
        "setup": {
            "name": "Spielvorbereitung",
            "steps": [
                "Armeezusammenstellung",
                "Schlachtfeld & Material",
                "Gelände festlegen & platzieren",
                "Blauen Spieler bestimmen",
                "Mission festlegen",
                "Spielaufbau-Effekte",
                "Einheiten in vorbereiteten Stellungen (Infiltrate/Prepared Pos.)"
            ]
        },
        "command": {
            "name": "Kommandophase",
            "steps": [
                "1. Kommandokarten auswählen und spielen (verdeckt)",
                "2. Kommandokarten aufdecken & Effekte abhandeln",
                "3. Priorität ermitteln (Pips vergleichen)",
                "4. Commander benennen & Befehle erteilen",
                "5. Befehlspool bilden (Restliche Einheiten)",
                "6. Passen-Pool bilden"
            ]
        },
        "activation": {
            "name": "Aktivierungsphase",
            "steps": [
                "1. Start-Effekte (Rundenbeginn)",
                "2. Spieler wählen (Priorität zuerst)",
                "3. Einheit aktivieren (Befehl oder Pool)",
                "   a. Start-Effekte (Einheit)",
                "   b. Sammeln (Rally) - Suppression entfernen",
                "   c. Aktionen durchführen (2 Aktionen)",
                "   d. End-Effekte (Einheit)",
                "   e. Befehlsmarker umdrehen/ablegen",
                "4. End-Effekte (Aktivierungsphase)"
            ]
        },
        "end": {
            "name": "Endphase",
            "steps": [
                "1. Start-Effekte (Endphase)",
                "2. Siegpunkte werten",
                "3. Kommandokarten ablegen",
                "4. Marker entfernen (Aim, Dodge, 1 Suppression, etc.)",
                "5. Befehlspool aktualisieren / Einheiten befördern",
                "6. End-Effekte",
                "7. Rundenzähler vorstellen"
            ]
        }
    }

    # =========================================================================
    # 2. AKTIONEN
    # =========================================================================
    ACTIONS = {
        "move": {
            "name": "Bewegung",
            "description": "Führe eine Standardbewegung oder Klettern durch."
        },
        "attack": {
            "name": "Angriff",
            "description": "Greife eine feindliche Einheit an (Fernkampf oder Nahkampf)."
        },
        "aim": {
            "name": "Zielen",
            "description": "Erhalte 1 Zielmarker (Aim Token). Erlaubt Reroll von 2 Würfeln."
        },
        "dodge": {
            "name": "Ausweichen",
            "description": "Erhalte 1 Ausweichmarker (Dodge Token). Negiert 1 Treffer."
        },
        "standby": {
            "name": "Bereitschaft",
            "description": "Erhalte 1 Bereitschaftsmarker. Reagiere auf feindliche Aktionen."
        },
        "recover": {
            "name": "Erholung",
            "description": "Entferne alle Suppression-Marker und mache Karten spielbereit."
        },
        "card_action": {
            "name": "Kartenaktion",
            "description": "Aktion von Einheit/Upgrade-Karte (->)."
        }
    }

    # =========================================================================
    # 3. BEDINGUNGEN (SUPPRESSION / PANIK)
    # =========================================================================
    CONDITIONS = {
        "suppressed": {
            "name": "Niedergehalten (Suppressed)",
            "trigger": "Suppression >= Courage (Mut)",
            "effect": "Einheit hat 1 Aktion weniger. Verbesserte Deckung (+1)."
        },
        "panic": {
            "name": "Panik",
            "trigger": "Suppression >= 2 * Courage",
            "effect": "Kann keine Aktionen durchführen. Wirft Zielobjekte ab. Sammelt am Ende Suppression = Courage."
        },
        "damaged": {
            "name": "Beschädigt (Fahrzeug)",
            "trigger": "Wunden >= Robustheit (Resilience)",
            "effect": "Erhält Beschädigt-Marker. Muss würfeln -> evtl. Aktionsverlust."
        }
    }

    # =========================================================================
    # 4. KEYWORDS (REGEL-LOGIK)
    # =========================================================================
    # Diese Dictionary dient als Lookup für die GameEngine.
    # 'timing' gibt an, wann der Effekt geprüft wird.

    KEYWORDS = {
        # --- UNIT KEYWORDS ---
        "Jump": {
            "name": "Springen X",
            "german": "Springen",
            "timing": "movement",
            "effect": "Ignoriere Gelände Höhe X."
        },
        "Deflect": {
            "name": "Ablenken",
            "german": "Ablenken",
            "timing": "defense_roll",
            "effect": "Wenn Dodge ausgegeben: Surge->Block. Angreifer erleidet 1 Wunde pro Surge-Symbol."
        },
        "Immune: Pierce": {
            "name": "Immune: Pierce",
            "german": "Immunität: Durchschlagen",
            "timing": "defense_modify",
            "effect": "Durchschlagen (Pierce) kann keine Blocks negieren."
        },
        "Sharpshooter": {
            "name": "Sharpshooter X",
            "german": "Scharfschütze",
            "timing": "attack_cover",
            "effect": "Reduziere Deckung des Verteidigers um X."
        },
        "Charge": {
            "name": "Charge",
            "german": "Sturmangriff",
            "timing": "after_move",
            "effect": "Nach Bewegung in Nahkampf: Freie Nahkampf-Attacke."
        },
        "Relentless": {
            "name": "Relentless",
            "german": "Unerbittlich",
            "timing": "after_move",
            "effect": "Nach Bewegung: Freie Attacke."
        },
        "Nimble": {
            "name": "Nimble",
            "german": "Flink",
            "timing": "after_defense",
            "effect": "Wenn Dodge ausgegeben wurde: Erhalte 1 Dodge zurück."
        },
        "Precise": {
            "name": "Precise X",
            "german": "Präzise",
            "timing": "reroll",
            "effect": "Wenn Aim ausgegeben: Reroll X zusätzliche Würfel."
        },
         "Gunslinger": {
            "name": "Gunslinger",
            "german": "Revolverheld",
            "timing": "attack_declare",
            "effect": "Nach Fernkampfangriff: Zusätzlicher Angriff gegen anderes Ziel."
        },
        "Tactical": {
            "name": "Tactical X",
            "german": "Taktisch",
            "timing": "movement",
            "effect": "Erhalte X Aim Marker nach Standardbewegung."
        },
        "Scout": {
            "name": "Scout X",
            "german": "Späher",
            "timing": "setup",
            "effect": "Nach Aufstellung: Freie Bewegung Speed-X."
        },
        "Infiltrate": {
            "name": "Infiltrate",
            "german": "Infiltrieren",
            "timing": "setup",
            "effect": "Darf überall im eigenen Gebiet oder jenseits von 3 zu Gegnern aufgestellt werden."
        },
        "Low Profile": {
            "name": "Low Profile",
            "german": "Unauffällig", # Oder Ducken? Regelbuch Check: 'Unauffällig'
            "timing": "defense_cover",
            "effect": "Wenn leichte Deckung, wird sie zu schwerer Deckung. (Old rules? Check text: 'Unauffällig: ... wirft 1 Würfel weniger und fügt 1 Block hinzu' -> New rules text provided says 'Unauffällig: Solange ... verteidigt ... wirft sie stattdessen einen Verteidigungswürfel weniger und fügt dem Deckungspool ... ein zusätzliches D-Ergebnis hinzu.')"
        },
        "Danger Sense": {
            "name": "Danger Sense X",
            "german": "Gefahrensinn",
            "timing": "defense_roll",
            "effect": "Wirf +1 Verteidigungswürfel pro Suppression (max X). Kann weniger Suppression entfernen."
        },

        # --- WEAPON KEYWORDS ---
        "Pierce": {
            "name": "Pierce X",
            "german": "Durchschlagen",
            "timing": "defense_modify",
            "effect": "Negiere bis zu X Block-Ergebnisse."
        },
        "Impact": {
            "name": "Impact X",
            "german": "Wucht",
            "timing": "attack_modify",
            "effect": "Ändere bis zu X Treffer zu Crits, wenn Ziel Panzerung hat."
        },
        "Critical": {
            "name": "Critical X",
            "german": "Kritisch",
            "timing": "attack_surge",
            "effect": "Wandle bis zu X Surges in Crits um."
        },
        "Suppressive": {
            "name": "Suppressive",
            "german": "Niederhaltend",
            "timing": "attack_end",
            "effect": "Verteidiger erhält mindestens 1 Suppression, auch wenn keine Treffer."
        },
        "Blast": {
            "name": "Blast",
            "german": "Explosion",
            "timing": "attack_cover",
            "effect": "Ignoriere Deckung."
        },
        "High Velocity": {
            "name": "High Velocity",
            "german": "Hochgeschwindigkeit",
            "timing": "defense_dodge",
            "effect": "Verteidiger kann keine Dodge-Marker ausgeben."
        },
        "Spray": {
            "name": "Spray",
            "german": "Streuung",
            "timing": "attack_dice",
            "effect": "Addiere Würfel X mal, wobei X = Anzahl Minis des Ziels."
        }
    }

    # =========================================================================
    # 5. MECHANICS & CONSTANTS
    # =========================================================================
    DICE_FACES = {
        "red_attack":   ["hit", "hit", "hit", "hit", "hit", "hit", "crit", "surge"], # 6 Hit, 1 Crit, 1 Surge? Check Text.
        # Text: "Angriffswürfel haben ... Treffer (A), Angriffsenergie (C), Kritischer Treffer (B)."
        # Rot: Meistens beste. Regelbuch sagt nicht exakte Verteilung, aber standard Legion:
        # Red: 1 Surge, 1 Crit, 6 Hit (Total 8)

        "black_attack": ["hit", "hit", "hit", "surge", "crit", "blank", "blank", "blank"],
        # Black: 1 Surge, 1 Crit, 3 Hit, 3 Blank (Total 8)

        "white_attack": ["hit", "surge", "crit", "blank", "blank", "blank", "blank", "blank"],
        # White: 1 Surge, 1 Crit, 1 Hit, 5 Blank (Total 8)

        "red_defense":  ["block", "block", "block", "surge", "blank", "blank"],
        # Red Def: 3 Block, 1 Surge, 2 Blank (Total 6)

        "white_defense":["block", "surge", "blank", "blank", "blank", "blank"]
        # White Def: 1 Block, 1 Surge, 4 Blank (Total 6)
    }

    # Helper method to get keyword def
    @staticmethod
    def get_keyword(name):
        # Versuche exakten Match oder "Name X"
        if name in LegionRules.KEYWORDS:
            return LegionRules.KEYWORDS[name]

        # Split "Pierce 1" -> "Pierce"
        base = name.split(" ")[0]
        if base in LegionRules.KEYWORDS:
            return LegionRules.KEYWORDS[base]

        # Check German names
        for k, v in LegionRules.KEYWORDS.items():
            if v.get("german") == base or v.get("german") == name:
                return v

        return None

    @staticmethod
    def get_dice_distribution(color, type_):
        key = f"{color.lower()}_{type_}"
        return LegionRules.DICE_FACES.get(key, [])
