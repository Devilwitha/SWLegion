class LegionRules:
    def __init__(self):
        # ---------------------------------------------------------------------
        # SPIELSTRUKTUR (Rundenablauf nach 2.5)
        # ---------------------------------------------------------------------
        self.game_structure = {
            "1. Kommandophase": [
                "1. Kommandokarte wählen: Jeder Spieler wählt verdeckt eine Kommandokarte.",
                "2. Aufdecken: Karten werden aufgedeckt. Der Spieler mit weniger Pips (Punkten) hat Priorität (bei Gleichstand Wurf).",
                "3. Befehle erteilen: Der Kommandeur der gespielten Karte erteilt Befehle an Einheiten in Reichweite (Range 1-3 für Commander/Operative, Range 4+ mit best. Upgrades)."
            ],
            "2. Aktivierungsphase": [
                "1. Start: Der Spieler mit Priorität beginnt.",
                "2. Aktivierung: Wähle eine Einheit mit offenem Befehlsmarker ODER ziehe einen zufälligen Marker aus dem Pool.",
                "3. Sammeln (Rally): Wenn die Einheit Niederhalten-Marker (Suppression) hat, würfle weißen Verteidigungswürfel pro Marker. Bei Block/Surge entferne 1 Marker.",
                "4. Aktionen: Die Einheit führt 2 Aktionen durch (Bewegen, Angreifen, Zielen, Ausweichen, etc.).",
                "   - Standard: Bewegen, Angreifen, Zielen, Ausweichen, Bereitschaft (Standby), Erholen (Recover), Karte.",
                "   - Beschränkung: Nur 1 Angriff pro Aktivierung (außer spezielle Regeln).",
                "5. Ende der Aktivierung: Entferne alle Zielen-, Ausweichen- und Bereitschaftsmarker (außer sie bleiben durch Regeln). Drehe Befehlsmarker um."
            ],
            "3. Endphase": [
                "1. Marker aufräumen: Entferne alle nicht verwendeten Zielen-, Ausweichen-, Bereitschafts- und Surge-Marker.",
                "2. Niederhalten: Entferne von jeder Einheit 1 Niederhalten-Marker (Suppression).",
                "3. Kommandokarten: Lege gespielte Kommandokarten ab (außer 'Permanent').",
                "4. Rundenmarker: Erhöhe den Rundenzeiger. Wenn Runde 6 vorbei -> Spielende."
            ]
        }

        # ---------------------------------------------------------------------
        # KEYWORDS (Wichtige Begriffe 2.5)
        # ---------------------------------------------------------------------
        self.keywords = {
            "Arsenal X": "Die Einheit kann X Waffen für einen Angriffspool wählen (statt nur 1).",
            "Deckung (Cover)": "Leicht: Zieht 1 Treffer (Hit) ab. Schwer: Zieht 2 Treffer ab. Deckung gilt nicht gegen Kritische Treffer.",
            "Durchschlagen X (Pierce)": "Ändert bis zu X Block-Ergebnisse des Verteidigers zu Blanks.",
            "Wucht X (Impact)": "Ändert beim Angriff bis zu X Treffer (Hits) zu Kritischen Treffern (Crits), wenn das Ziel Rüstung (Armor) hat.",
            "Kritisch X (Critical)": "Wandle bis zu X Surges in Kritische Treffer um.",
            "Scharfschütze X (Sharpshooter)": "Ignoriere X Stufen von Deckung beim Angriff.",
            "Unverwüstlich (Impervious)": "Wenn Rüstungswürfe durch 'Durchschlagen' negiert würden, würfle trotzdem X zusätzliche Verteidigungswürfel.",
            "Niedrighalten (Suppressive)": "Gibt dem Verteidiger nach dem Angriff 1 Niederhalten-Marker, auch wenn kein Schaden entsteht. (Zusätzlich zum Standard-Marker bei Treffer).",
            "Diszipliniert X (Disciplined)": "Wenn ein Commander in Reichweite X ist, darfst du bei Panik-Tests dessen Mut-Wert nutzen.",
            "Flink (Nimble)": "Wenn du einen oder mehr Ausweichen-Marker (Dodge) ausgibst, erhalte 1 Ausweichen-Marker zurück.",
            "Feuerunterstützung (Fire Support)": "Wenn eine andere freundliche Einheit angreift, darf diese Einheit ihren Fernkampf-Pool hinzufügen und ihren Befehlsmarker umdrehen.",
            "Panik": "Wenn Niederhalten-Marker >= doppelter Mut-Wert -> Einheit ist in Panik. (Bei 2.5: Einheit kann keine Aktionen durchführen und flieht zum Spielfeldrand).",
            "Niederhalten (Suppressed)": "Wenn Niederhalten-Marker >= Mut-Wert -> Einheit hat 1 Aktion weniger."
        }

        # ---------------------------------------------------------------------
        # AKTIONEN
        # ---------------------------------------------------------------------
        self.actions = {
            "Bewegen": "Führe eine Bewegung mit dem Geschwindigkeits-Tool durch. (Maximal Bewegungs-Wert der Einheit).",
            "Angreifen": "Wähle Waffe(n) und Ziel, bilde Pool, würfle. (Nur 1x pro Aktivierung).",
            "Zielen (Aim)": "Erhalte 1 Zielen-Marker. (Kann ausgegeben werden, um 2 Würfel neu zu werfen).",
            "Ausweichen (Dodge)": "Erhalte 1 Ausweichen-Marker. (Kann ausgegeben werden, um 1 Treffer zu negieren).",
            "Bereitschaft (Standby)": "Erhalte 1 Bereitschafts-Marker. Kann ausgegeben werden, um eine Aktion durchzuführen, wenn Gegner in Reichweite 1-2 agiert.",
            "Erholen (Recover)": "Entferne alle Niederhalten-Marker und mache erschöpfte Upgrade-Karten wieder bereit."
        }

    def search_rule(self, query):
        """Sucht nach Regeln, Keywords oder Phasen."""
        results = []
        q = query.lower()

        # Suche in Phasen
        for phase, steps in self.game_structure.items():
            if q in phase.lower():
                results.append(f"PHASE: {phase}\n" + "\n".join(steps))
            else:
                for step in steps:
                    if q in step.lower():
                        results.append(f"PHASE {phase} (Teil): {step}")

        # Suche in Keywords
        for kw, desc in self.keywords.items():
            if q in kw.lower():
                results.append(f"KEYWORD {kw}: {desc}")

        # Suche in Aktionen
        for act, desc in self.actions.items():
            if q in act.lower():
                results.append(f"AKTION {act}: {desc}")

        return results

    def get_phase_info(self, phase_name):
        return self.game_structure.get(phase_name, [])
