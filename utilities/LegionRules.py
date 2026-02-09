class LegionRules:
    """
    Zentrale Datenbank für Star Wars: Legion Regeln.
    Basiert auf dem offiziellen Regelwerk (Stand: November 2025).
    """

    # =========================================================================
    # 1. PHASEN & ABLAUF
    # =========================================================================
    PHASES = {
        "setup": {
            "name": "Spielvorbereitung",
            "steps": [
                "1. Armeezusammenstellung (gemäß Ranglimits)",
                "2. Schlachtfeld & Material bereitstellen",
                "3. Gelände festlegen & platzieren",
                "4. Blauen Spieler bestimmen (Würfeln)",
                "5. Missionsparameter festlegen (Schlachtkarten)",
                "6. Spielaufbau-Effekte abhandeln",
                "7. Aufstellung der Einheiten",
                "8. Prepared Positions / Infiltrate Einheiten",
                "9. Scout-Bewegungen durchführen"
            ]
        },
        "command": {
            "name": "Kommandophase",
            "steps": [
                "1. Kommandokarten verdeckt auswählen",
                "2. Kommandokarten gleichzeitig aufdecken",
                "3. Karteneffekte abhandeln (niedrigste Pips zuerst)",
                "4. Priorität ermitteln (weniger Pips = Priorität)",
                "5. Bei Gleichstand: Prioritätsspieler der Vorrunde entscheidet",
                "6. Befehle an Einheiten erteilen (Befehlsmarker)",
                "7. Befehlspool bilden (nicht befohlene Einheiten)",
                "8. Passen-Pool bilden"
            ]
        },
        "activation": {
            "name": "Aktivierungsphase",
            "steps": [
                "1. Rundenbeginn-Effekte abhandeln",
                "2. Spieler mit Priorität beginnt (oder passt)",
                "3. Einheit zur Aktivierung wählen:",
                "   - Befohlene Einheit (Befehlsmarker) ODER",
                "   - Befehlsmarker ziehen (aus Pool)",
                "4. Einheit aktivieren:",
                "   a) Start-Effekte der Einheit",
                "   b) Sammeln (Rally) - Würfeln gegen Suppression",
                "   c) 2 Aktionen durchführen",
                "   d) End-Effekte der Einheit",
                "   e) Befehlsmarker umdrehen/ablegen",
                "5. Gegnerischer Spieler aktiviert (oder passt)",
                "6. Wiederholen bis alle aktiviert haben",
                "7. Aktivierungsende-Effekte"
            ]
        },
        "end": {
            "name": "Endphase",
            "steps": [
                "1. Endphasen-Start-Effekte",
                "2. Siegpunkte werten (gemäß Missionsziel)",
                "3. Kommandokarten ablegen",
                "4. Marker entfernen (Aim, Dodge, Standby)",
                "5. 1 Suppression pro Einheit entfernen",
                "6. Befördernde Einheiten prüfen",
                "7. Befehlspool aktualisieren",
                "8. End-Effekte abhandeln",
                "9. Rundenzähler um 1 erhöhen",
                "10. Spielende prüfen (nach Runde 6)"
            ]
        }
    }

    # =========================================================================
    # 2. AKTIONEN
    # =========================================================================
    ACTIONS = {
        "move": {
            "name": "Bewegung",
            "description": "Führe eine Standardbewegung durch. Nutze das Bewegungslineal entsprechend der Geschwindigkeit.",
            "rules": [
                "Bewegungslineal an Basis anlegen",
                "Gelände kann Bewegung blockieren oder verlangsamen",
                "Schwieriges Gelände: halbe Bewegung",
                "Unpassierbares Gelände: keine Bewegung",
                "Klettern: 1 zusätzliche Aktion pro Höhenstufe"
            ]
        },
        "attack": {
            "name": "Angriff",
            "description": "Greife eine feindliche Einheit mit Waffen an.",
            "rules": [
                "1. Ziel deklarieren (Reichweite & Sichtlinie prüfen)",
                "2. Angriffswürfelpool bilden (Waffen addieren)",
                "3. Würfeln & Modifikationen anwenden",
                "4. Deckung bestimmen (leicht/schwer)",
                "5. Verteidigung würfeln",
                "6. Treffer vergleichen & Wunden zuweisen",
                "7. Suppression hinzufügen (1 pro Angriff)"
            ]
        },
        "aim": {
            "name": "Zielen",
            "description": "Erhalte 1 Zielmarker (Aim Token).",
            "rules": [
                "Beim Angriff ausgeben: 2 Würfel neu würfeln",
                "Mehrere Aims können kombiniert werden",
                "Verfällt am Ende der Runde"
            ]
        },
        "dodge": {
            "name": "Ausweichen",
            "description": "Erhalte 1 Ausweichmarker (Dodge Token).",
            "rules": [
                "Bei Verteidigung ausgeben: 1 Treffer negieren",
                "Muss vor dem Würfeln deklariert werden",
                "Verfällt am Ende der Runde"
            ]
        },
        "standby": {
            "name": "Bereitschaft",
            "description": "Erhalte 1 Bereitschaftsmarker.",
            "rules": [
                "Auslöser: Feindliche Einheit bewegt sich oder greift an in R2",
                "Reaktion: Bewegung ODER Angriff durchführen",
                "Verliert Standby bei eigenem Angriff/Bewegung",
                "Verfällt am Ende der Runde"
            ]
        },
        "recover": {
            "name": "Erholung",
            "description": "Entferne alle Suppression-Marker und regeneriere Karten.",
            "rules": [
                "Alle Suppression-Marker entfernen",
                "Alle erschöpften Upgrade-Karten regenerieren",
                "Erschöpfte Waffenkarten regenerieren"
            ]
        },
        "card_action": {
            "name": "Kartenaktion",
            "description": "Führe eine Aktion von einer Karte aus (-> Symbol).",
            "rules": [
                "Upgrade-Karten können Aktionen haben",
                "Einheitenkarten können Aktionen haben",
                "Einige kosten eine freie Aktion"
            ]
        },
        "free_action": {
            "name": "Freie Aktion",
            "description": "Eine zusätzliche Aktion die nicht von den 2 Standardaktionen abzieht.",
            "rules": [
                "Wird durch Keywords wie Relentless, Charge gewährt",
                "Zählt nicht gegen das Aktionslimit",
                "Kann nur einmal pro Trigger genutzt werden"
            ]
        }
    }

    # =========================================================================
    # 3. BEDINGUNGEN (SUPPRESSION / PANIK / DAMAGE)
    # =========================================================================
    CONDITIONS = {
        "suppressed": {
            "name": "Niedergehalten (Suppressed)",
            "trigger": "Suppression >= Courage (Mut)",
            "effect": "Einheit hat nur 1 Aktion statt 2.",
            "additional": "Erhält +1 zur Deckung (leichte -> schwere)"
        },
        "panic": {
            "name": "Panik",
            "trigger": "Suppression >= 2 × Courage",
            "effect": [
                "Kann keine Aktionen durchführen",
                "Wirft getragene Zielobjekte ab",
                "Bewegt sich Speed 1 zum nächsten Tischrand",
                "Am Ende: Suppression = Courage setzen"
            ]
        },
        "damaged": {
            "name": "Beschädigt (Fahrzeug)",
            "trigger": "Wunden >= Robustheit (Resilience)",
            "effect": "Erhält Beschädigt-Marker. Muss würfeln.",
            "damage_table": {
                "1-3": "Kein Effekt",
                "4-5": "Verliert 1 Aktion",
                "6": "Verliert 1 Aktion, Waffe beschädigt"
            }
        },
        "disabled": {
            "name": "Kampfunfähig (Disabled)",
            "trigger": "Fahrzeug erhält weitere Damage-Marker wenn bereits Damaged",
            "effect": "Einheit wird sofort zerstört"
        },
        "immobilized": {
            "name": "Immobilisiert",
            "trigger": "Durch Ionisierung oder Effekte",
            "effect": "Kann sich nicht bewegen bis Zustand entfernt"
        },
        "poisoned": {
            "name": "Vergiftet",
            "trigger": "Durch Poison Keyword",
            "effect": "Würfelt weniger Verteidigungswürfel"
        }
    }

    # =========================================================================
    # 4. DECKUNG (COVER)
    # =========================================================================
    COVER = {
        "none": {
            "name": "Keine Deckung",
            "value": 0,
            "description": "Einheit steht im Freien"
        },
        "light": {
            "name": "Leichte Deckung",
            "value": 1,
            "description": "Einheit steht hinter niedrigem Gelände oder Barrikaden",
            "effect": "Fügt 1 Block zum Deckungspool hinzu"
        },
        "heavy": {
            "name": "Schwere Deckung",
            "value": 2,
            "description": "Einheit steht hinter hohem Gelände oder in Gebäuden",
            "effect": "Fügt 2 Blocks zum Deckungspool hinzu"
        }
    }

    # =========================================================================
    # 5. GELÄNDE-TYPEN
    # =========================================================================
    TERRAIN = {
        "open": {
            "name": "Offenes Gelände",
            "movement": "Normal",
            "cover": "none",
            "los": "Keine Blockierung"
        },
        "difficult": {
            "name": "Schwieriges Gelände",
            "movement": "Halbe Geschwindigkeit",
            "cover": "light",
            "los": "Keine Blockierung"
        },
        "impassable": {
            "name": "Unpassierbares Gelände",
            "movement": "Blockiert",
            "cover": "heavy",
            "los": "Blockiert Sichtlinie"
        },
        "barricade": {
            "name": "Barrikade",
            "movement": "Muss drumherum",
            "cover": "heavy",
            "height": "Höhe 1"
        },
        "area_terrain": {
            "name": "Flächengelände",
            "movement": "Schwierig wenn drin",
            "cover": "Für Einheiten darin",
            "los": "Blockiert wenn Linie durchgeht"
        },
        "water": {
            "name": "Wasser/Sumpf",
            "movement": "Schwieriges Gelände",
            "cover": "none",
            "special": "Einige Einheiten können schneller passieren"
        },
        "lava": {
            "name": "Lava",
            "movement": "Gefährlich",
            "cover": "none",
            "special": "Einheiten erleiden Wunden"
        },
        "sarlacc_pit": {
            "name": "Sarlacc Pit",
            "movement": "Unpassierbar in Mitte",
            "cover": "none",
            "special": "Einheiten die hineinfallen werden verschlungen"
        }
    }

    # =========================================================================
    # 6. KEYWORDS (VOLLSTÄNDIG)
    # =========================================================================
    KEYWORDS = {
        # --- MOVEMENT KEYWORDS ---
        "Jump": {
            "name": "Jump X",
            "german": "Springen",
            "timing": "movement",
            "effect": "Ignoriere Gelände und Einheiten bis Höhe X bei Bewegung."
        },
        "Speeder": {
            "name": "Speeder X",
            "german": "Gleiter",
            "timing": "movement",
            "effect": "Muss sich jede Runde bewegen. Ignoriert schwieriges Gelände. Kompensationsbewegung am Ende."
        },
        "Climbing Vehicle": {
            "name": "Climbing Vehicle",
            "german": "Kletterfahrzeug",
            "timing": "movement",
            "effect": "Kann klettern ohne zusätzliche Aktion."
        },
        "Hover: Ground/Air": {
            "name": "Hover",
            "german": "Schweben",
            "timing": "movement",
            "effect": "Kann Bodenkontakt oder schwebend sein. Ändert Interaktionen."
        },
        "Reposition": {
            "name": "Reposition",
            "german": "Neupositionierung",
            "timing": "movement",
            "effect": "Darf nach Angriff eine Speed-1 Bewegung durchführen."
        },
        "Scale": {
            "name": "Scale",
            "german": "Erklettern",
            "timing": "movement",
            "effect": "Kann als Teil der Bewegung klettern ohne extra Aktion."
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
            "effect": "Aufstellung überall jenseits von Reichweite 3 zu Gegnern."
        },
        "Prepared Positions": {
            "name": "Prepared Positions",
            "german": "Vorbereitete Stellungen",
            "timing": "setup",
            "effect": "Erhält nach Aufstellung 1 Dodge-Token."
        },
        "Stationary": {
            "name": "Stationary",
            "german": "Stationär",
            "timing": "movement",
            "effect": "Kann keine Bewegungsaktionen durchführen."
        },
        "Unhindered": {
            "name": "Unhindered",
            "german": "Ungehindert",
            "timing": "movement",
            "effect": "Ignoriert schwieriges Gelände."
        },

        # --- ATTACK KEYWORDS ---
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
            "effect": "Nach Bewegung: Freie Attacke (Nah- oder Fernkampf)."
        },
        "Steady": {
            "name": "Steady",
            "german": "Beständig",
            "timing": "after_move",
            "effect": "Nach Bewegung: Freie Fernkampf-Attacke."
        },
        "Gunslinger": {
            "name": "Gunslinger",
            "german": "Revolverheld",
            "timing": "attack_declare",
            "effect": "Nach Fernkampfangriff: Zusätzlicher Angriff gegen anderes Ziel."
        },
        "Versatile": {
            "name": "Versatile",
            "german": "Vielseitig",
            "timing": "attack",
            "effect": "Kann Nahkampfwaffen im Fernkampf nutzen und umgekehrt."
        },
        "Arsenal": {
            "name": "Arsenal X",
            "german": "Arsenal",
            "timing": "attack",
            "effect": "Kann bis zu X verschiedene Waffen in einem Angriff nutzen."
        },
        "Sharpshooter": {
            "name": "Sharpshooter X",
            "german": "Scharfschütze",
            "timing": "attack_cover",
            "effect": "Reduziere Deckung des Verteidigers um X."
        },
        "Marksman": {
            "name": "Marksman",
            "german": "Meisterschütze",
            "timing": "attack",
            "effect": "Kann Attack-Surge in Crit umwandeln."
        },
        "Precise": {
            "name": "Precise X",
            "german": "Präzise",
            "timing": "reroll",
            "effect": "Wenn Aim ausgegeben: Reroll X zusätzliche Würfel."
        },
        "Tactical": {
            "name": "Tactical X",
            "german": "Taktisch",
            "timing": "movement",
            "effect": "Erhalte X Aim-Marker nach Standardbewegung."
        },
        "Target": {
            "name": "Target X",
            "german": "Ziel",
            "timing": "attack",
            "effect": "Erhalte X Aim-Tokens beim Angriff auf markierte Einheit."
        },
        "Lethal": {
            "name": "Lethal X",
            "german": "Tödlich",
            "timing": "attack",
            "effect": "Wenn Aim ausgegeben: Wandle X Surges in Crits."
        },
        "Ram": {
            "name": "Ram X",
            "german": "Rammen",
            "timing": "movement",
            "effect": "Nach Bewegung durch feindliche Einheit: Verursache X Wunden."
        },
        "Coordinate": {
            "name": "Coordinate",
            "german": "Koordinieren",
            "timing": "command",
            "effect": "Beim Erhalt eines Befehls: Erteile Befehl an befreundete Einheit in R1."
        },

        # --- DEFENSE KEYWORDS ---
        "Deflect": {
            "name": "Deflect",
            "german": "Ablenken",
            "timing": "defense_roll",
            "effect": "Wenn Dodge ausgegeben: Surge->Block. Angreifer erleidet 1 Wunde pro nicht blockiertem Surge."
        },
        "Nimble": {
            "name": "Nimble",
            "german": "Flink",
            "timing": "after_defense",
            "effect": "Wenn Dodge ausgegeben: Erhalte 1 Dodge zurück."
        },
        "Danger Sense": {
            "name": "Danger Sense X",
            "german": "Gefahrensinn",
            "timing": "defense_roll",
            "effect": "Wirf +1 Verteidigungswürfel pro Suppression (max X)."
        },
        "Low Profile": {
            "name": "Low Profile",
            "german": "Unauffällig",
            "timing": "defense_cover",
            "effect": "1 Würfel weniger werfen, +1 Block zum Deckungspool."
        },
        "Uncanny Luck": {
            "name": "Uncanny Luck X",
            "german": "Unglaubliches Glück",
            "timing": "defense",
            "effect": "Darf bis zu X Verteidigungswürfel neu würfeln."
        },
        "Impervious": {
            "name": "Impervious",
            "german": "Unverwundbar",
            "timing": "defense",
            "effect": "Pierce hat keine Wirkung auf diese Einheit."
        },
        "Armor": {
            "name": "Armor",
            "german": "Panzerung",
            "timing": "defense_modify",
            "effect": "Normale Treffer werden zu Blocks. Nur Crits verursachen Schaden."
        },
        "Armor X": {
            "name": "Armor X",
            "german": "Panzerung",
            "timing": "defense_modify",
            "effect": "Blockiere X Treffer automatisch. Crits umgehen dies."
        },
        "Cover": {
            "name": "Cover X",
            "german": "Deckung",
            "timing": "defense",
            "effect": "Behandle Einheit als hätte sie Deckung X."
        },
        "Outmaneuver": {
            "name": "Outmaneuver",
            "german": "Ausmanövrieren",
            "timing": "defense",
            "effect": "Behalte leichte Deckung auch wenn bewegt."
        },
        "Soresu Mastery": {
            "name": "Soresu Mastery",
            "german": "Soresu-Meisterschaft",
            "timing": "defense",
            "effect": "Erhält Dodge und Aim wenn angegriffen und Dodge hat."
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
            "effect": "Ändere bis zu X Treffer zu Crits gegen Panzerung."
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
            "effect": "Verteidiger erhält mindestens 1 Suppression."
        },
        "Blast": {
            "name": "Blast",
            "german": "Explosion",
            "timing": "attack_cover",
            "effect": "Ignoriere Deckung komplett."
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
            "effect": "Addiere Würfel für jede Mini in der Zieleinheit."
        },
        "Beam": {
            "name": "Beam X",
            "german": "Strahl",
            "timing": "attack",
            "effect": "Trifft bis zu X Einheiten in einer Linie."
        },
        "Fixed": {
            "name": "Fixed: Front/Rear",
            "german": "Fixiert",
            "timing": "attack",
            "effect": "Kann nur in eine Richtung feuern."
        },
        "Cumbersome": {
            "name": "Cumbersome",
            "german": "Sperrig",
            "timing": "attack",
            "effect": "Kann nicht genutzt werden wenn bewegt wurde."
        },
        "Immobilize": {
            "name": "Immobilize X",
            "german": "Immobilisieren",
            "timing": "attack_effect",
            "effect": "Ziel erhält X Immobilisierungs-Marker."
        },
        "Ion": {
            "name": "Ion X",
            "german": "Ion",
            "timing": "attack_effect",
            "effect": "Ziel erhält X Ion-Marker. Fahrzeuge verlieren Aktionen."
        },
        "Poison": {
            "name": "Poison X",
            "german": "Gift",
            "timing": "attack_effect",
            "effect": "Ziel erhält X Gift-Marker. Reduziert Verteidigung."
        },
        "Scatter": {
            "name": "Scatter",
            "german": "Streuen",
            "timing": "attack",
            "effect": "Angriff trifft alle Einheiten in einem Bereich."
        },

        # --- FORCE KEYWORDS ---
        "Deflect": {
            "name": "Deflect",
            "german": "Ablenken",
            "timing": "defense",
            "effect": "Surge=Block wenn Dodge ausgegeben. Reflektiert Treffer."
        },
        "Force Push": {
            "name": "Force Push",
            "german": "Machtstoß",
            "timing": "action",
            "effect": "Bewege feindliche Einheit."
        },
        "Force Leap": {
            "name": "Force Leap",
            "german": "Machtsprung",
            "timing": "movement",
            "effect": "Kann nach Bewegung zusätzlich springen."
        },
        "Master of the Force": {
            "name": "Master of the Force X",
            "german": "Meister der Macht",
            "timing": "end_phase",
            "effect": "Regeneriere X Machtfähigkeits-Karten."
        },
        "Immune: Force": {
            "name": "Immune: Force",
            "german": "Immun: Macht",
            "timing": "passive",
            "effect": "Kann nicht von Machtfähigkeiten beeinflusst werden."
        },

        # --- SPECIAL KEYWORDS ---
        "AI: Action": {
            "name": "AI: Action",
            "german": "KI",
            "timing": "activation",
            "effect": "Führt automatische Aktion aus wenn ohne Befehl aktiviert."
        },
        "Programmed": {
            "name": "Programmed",
            "german": "Programmiert",
            "timing": "activation",
            "effect": "Muss in bestimmter Reihenfolge handeln."
        },
        "Droid Trooper": {
            "name": "Droid Trooper",
            "german": "Droidentrupp",
            "timing": "passive",
            "effect": "Keine Courage. Immune: Panik."
        },
        "Creature Trooper": {
            "name": "Creature Trooper",
            "german": "Kreaturentrupp",
            "timing": "passive",
            "effect": "Kann nicht auf Fahrzeugen transportiert werden."
        },
        "Compel": {
            "name": "Compel",
            "german": "Befehlen",
            "timing": "command",
            "effect": "Befohle Einheiten müssen freie Bewegung durchführen."
        },
        "Direct": {
            "name": "Direct: Type",
            "german": "Anweisen",
            "timing": "command",
            "effect": "Nach Erteilen eines Befehls: Erteile Befehl an Typ in R2."
        },
        "Inspire": {
            "name": "Inspire X",
            "german": "Inspirieren",
            "timing": "end_activation",
            "effect": "Entferne X Suppression von befreundeten Einheiten in R2."
        },
        "Take Cover": {
            "name": "Take Cover X",
            "german": "In Deckung",
            "timing": "command",
            "effect": "Erteile X Dodge-Token an befreundete Einheiten."
        },
        "Pulling the Strings": {
            "name": "Pulling the Strings",
            "german": "Fäden Ziehen",
            "timing": "action",
            "effect": "Befreundete Einheit führt Standardbewegung oder Angriff durch."
        },
        "Secret Mission": {
            "name": "Secret Mission",
            "german": "Geheime Mission",
            "timing": "scoring",
            "effect": "Erziele Siegpunkte wenn in feindlicher Aufstellzone."
        },
        "Bounty": {
            "name": "Bounty",
            "german": "Kopfgeld",
            "timing": "setup",
            "effect": "Markiere feindliche Kommandanten. Erziele Siegpunkt bei Eliminierung."
        },
        "Detachment": {
            "name": "Detachment: Type",
            "german": "Abteilung",
            "timing": "setup",
            "effect": "Wird mit anderer Einheit aufgestellt."
        },
        "Guardian": {
            "name": "Guardian X",
            "german": "Beschützer",
            "timing": "defense",
            "effect": "Übernimm bis zu X Treffer von befreundeter Einheit in R1."
        },
        "Sentinel": {
            "name": "Sentinel",
            "german": "Wächter",
            "timing": "standby",
            "effect": "Größere Standby-Reichweite (R3)."
        },
        "Transport": {
            "name": "Transport: Open/Closed X",
            "german": "Transport",
            "timing": "movement",
            "effect": "Kann bis zu X Einheiten transportieren."
        },
        "Tow Cable": {
            "name": "Tow Cable",
            "german": "Abschleppseil",
            "timing": "attack",
            "effect": "Kann Pivot bei Fahrzeugen erzwingen."
        },
        "Repair": {
            "name": "Repair X",
            "german": "Reparatur",
            "timing": "action",
            "effect": "Entferne bis zu X Wunden/Ion-Marker von Fahrzeugen."
        },
        "Treat": {
            "name": "Treat X",
            "german": "Behandlung",
            "timing": "action",
            "effect": "Entferne bis zu X Wunden/Gift-Marker von Truppen."
        },
        "Leader": {
            "name": "Leader",
            "german": "Anführer",
            "timing": "passive",
            "effect": "Mini ist Einheitenführer. Wenn entfernt: Befördern."
        },
        "Spur": {
            "name": "Spur",
            "german": "Antreiben",
            "timing": "movement",
            "effect": "Kann zusätzliche Bewegung durchführen, erhält Suppression."
        },
        "Entourage": {
            "name": "Entourage: Unit",
            "german": "Gefolge",
            "timing": "command",
            "effect": "Beim Erteilen von Befehlen: Gefolge-Einheit erhält auch Befehl."
        },
        "Retinue": {
            "name": "Retinue: Unit",
            "german": "Eskorte",
            "timing": "activation",
            "effect": "Darf sich zu Anführer-Einheit bewegen und erhält Aim/Dodge."
        },
        "Regenerate": {
            "name": "Regenerate X",
            "german": "Regenerieren",
            "timing": "end_phase",
            "effect": "Stelle bis zu X entfernte Minis wieder her."
        },
        "Detonate": {
            "name": "Detonate X",
            "german": "Detonieren",
            "timing": "action",
            "effect": "Löse X Ladungen in Reichweite aus."
        },
        "Arm": {
            "name": "Arm X",
            "german": "Bewaffnen",
            "timing": "action",
            "effect": "Platziere X Ladungen."
        },
        "Grounded": {
            "name": "Grounded",
            "german": "Geerdet",
            "timing": "passive",
            "effect": "Erhält Deckung von Fahrzeugen."
        }
    }

    # =========================================================================
    # 7. WÜRFEL-VERTEILUNG
    # =========================================================================
    DICE_FACES = {
        "red_attack": {
            "faces": ["hit", "hit", "hit", "hit", "hit", "crit", "surge", "blank"],
            "hit_chance": 0.625,
            "crit_chance": 0.125,
            "surge_chance": 0.125,
            "blank_chance": 0.125
        },
        "black_attack": {
            "faces": ["hit", "hit", "hit", "crit", "surge", "blank", "blank", "blank"],
            "hit_chance": 0.375,
            "crit_chance": 0.125,
            "surge_chance": 0.125,
            "blank_chance": 0.375
        },
        "white_attack": {
            "faces": ["hit", "crit", "surge", "blank", "blank", "blank", "blank", "blank"],
            "hit_chance": 0.125,
            "crit_chance": 0.125,
            "surge_chance": 0.125,
            "blank_chance": 0.625
        },
        "red_defense": {
            "faces": ["block", "block", "block", "surge", "blank", "blank"],
            "block_chance": 0.5,
            "surge_chance": 0.167,
            "blank_chance": 0.333
        },
        "white_defense": {
            "faces": ["block", "surge", "blank", "blank", "blank", "blank"],
            "block_chance": 0.167,
            "surge_chance": 0.167,
            "blank_chance": 0.666
        }
    }

    # =========================================================================
    # 8. ARMEEZUSAMMENSTELLUNG
    # =========================================================================
    ARMY_BUILDING = {
        "standard": {
            "name": "Standard (800 Punkte)",
            "points": 800,
            "commander": {"min": 1, "max": 2},
            "operative": {"min": 0, "max": 2},
            "corps": {"min": 3, "max": 6},
            "special_forces": {"min": 0, "max": 3},
            "support": {"min": 0, "max": 3},
            "heavy": {"min": 0, "max": 2}
        },
        "grand_army": {
            "name": "Große Armee (1600 Punkte)",
            "points": 1600,
            "commander": {"min": 2, "max": 4},
            "operative": {"min": 0, "max": 4},
            "corps": {"min": 6, "max": 12},
            "special_forces": {"min": 0, "max": 6},
            "support": {"min": 0, "max": 6},
            "heavy": {"min": 0, "max": 4}
        },
        "recon": {
            "name": "Aufklärung (500 Punkte)",
            "points": 500,
            "commander": {"min": 1, "max": 1},
            "operative": {"min": 0, "max": 1},
            "corps": {"min": 2, "max": 4},
            "special_forces": {"min": 0, "max": 2},
            "support": {"min": 0, "max": 2},
            "heavy": {"min": 0, "max": 1}
        },
        "skirmish": {
            "name": "Gefecht (400 Punkte)",
            "points": 400,
            "commander": {"min": 1, "max": 1},
            "operative": {"min": 0, "max": 1},
            "corps": {"min": 2, "max": 3},
            "special_forces": {"min": 0, "max": 1},
            "support": {"min": 0, "max": 1},
            "heavy": {"min": 0, "max": 0}
        }
    }

    # =========================================================================
    # 9. SCHLACHTKARTEN-KATEGORIEN
    # =========================================================================
    BATTLE_CARDS = {
        "objectives": [
            "Schlüsselpositionen (Key Positions)",
            "Durchbruch (Breakthrough)",
            "Abfangen (Intercept)",
            "Vorräte bergen (Recover Supplies)",
            "Sabotage",
            "Hostage Exchange",
            "Bombing Run"
        ],
        "deployments": [
            "Battle Lines",
            "Advanced Positions",
            "Disarray",
            "The Long March",
            "Major Offensive",
            "Roll Out"
        ],
        "conditions": [
            "Clear Conditions",
            "Hostile Environment",
            "Limited Visibility",
            "Minefield",
            "Supply Drop",
            "War Weary"
        ]
    }

    # =========================================================================
    # HELPER METHODS
    # =========================================================================
    @staticmethod
    def get_keyword(name):
        """Hole Keyword-Definition nach Name (EN oder DE)."""
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
        """Hole Würfelverteilung."""
        key = f"{color.lower()}_{type_}"
        return LegionRules.DICE_FACES.get(key, {})

    @staticmethod
    def get_action(action_name):
        """Hole Aktionsbeschreibung."""
        return LegionRules.ACTIONS.get(action_name.lower(), None)

    @staticmethod
    def get_phase(phase_name):
        """Hole Phasenbeschreibung."""
        return LegionRules.PHASES.get(phase_name.lower(), None)

    @staticmethod
    def get_condition(condition_name):
        """Hole Zustandsbeschreibung."""
        return LegionRules.CONDITIONS.get(condition_name.lower(), None)

    @staticmethod
    def get_terrain_type(terrain_name):
        """Hole Geländetyp-Beschreibung."""
        return LegionRules.TERRAIN.get(terrain_name.lower(), None)

    @staticmethod
    def get_army_requirements(game_type="standard"):
        """Hole Armeezusammenstellungs-Anforderungen."""
        return LegionRules.ARMY_BUILDING.get(game_type.lower(), None)

    @staticmethod
    def get_all_keywords():
        """Hole alle Keywords als Liste."""
        return list(LegionRules.KEYWORDS.keys())

    @staticmethod
    def search_keyword(search_term):
        """Suche Keywords nach Begriff."""
        results = []
        search_lower = search_term.lower()
        for key, value in LegionRules.KEYWORDS.items():
            if search_lower in key.lower() or search_lower in value.get("german", "").lower():
                results.append({key: value})
        return results
