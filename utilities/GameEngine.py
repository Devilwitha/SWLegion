"""
GameEngine.py - Star Wars Legion Spielmechanik-Engine
Verwaltet alle Regeln, Würfelmechaniken und Spielablauf gemäß offiziellem Regelwerk.
"""

import random
import logging
from typing import Dict, List, Optional, Tuple, Any

try:
    from .LegionRules import LegionRules
except ImportError:
    try:
        from utilities.LegionRules import LegionRules
    except ImportError:
        from LegionRules import LegionRules


class DiceRoller:
    """Würfelmechanik gemäß Star Wars Legion Regeln."""
    
    # Würfelseiten-Definitionen
    RED_ATTACK = ["hit", "hit", "hit", "hit", "hit", "crit", "surge", "blank"]
    BLACK_ATTACK = ["hit", "hit", "hit", "crit", "surge", "blank", "blank", "blank"]
    WHITE_ATTACK = ["hit", "crit", "surge", "blank", "blank", "blank", "blank", "blank"]
    
    RED_DEFENSE = ["block", "block", "block", "surge", "blank", "blank"]
    WHITE_DEFENSE = ["block", "surge", "blank", "blank", "blank", "blank"]
    
    @classmethod
    def roll_attack(cls, red: int = 0, black: int = 0, white: int = 0) -> Dict[str, int]:
        """Würfelt Angriffswürfel und gibt Ergebnisse zurück."""
        results = {"hit": 0, "crit": 0, "surge": 0, "blank": 0}
        
        for _ in range(red):
            result = random.choice(cls.RED_ATTACK)
            results[result] += 1
            
        for _ in range(black):
            result = random.choice(cls.BLACK_ATTACK)
            results[result] += 1
            
        for _ in range(white):
            result = random.choice(cls.WHITE_ATTACK)
            results[result] += 1
            
        return results
    
    @classmethod
    def roll_defense(cls, red: int = 0, white: int = 0) -> Dict[str, int]:
        """Würfelt Verteidigungswürfel und gibt Ergebnisse zurück."""
        results = {"block": 0, "surge": 0, "blank": 0}
        
        for _ in range(red):
            result = random.choice(cls.RED_DEFENSE)
            results[result] += 1
            
        for _ in range(white):
            result = random.choice(cls.WHITE_DEFENSE)
            results[result] += 1
            
        return results
    
    @classmethod
    def roll_rally(cls, suppression_count: int) -> int:
        """
        Würfelt Rally-Würfel (weiße Verteidigungswürfel).
        Gibt die Anzahl der entfernten Suppression-Marker zurück.
        """
        removed = 0
        for _ in range(suppression_count):
            result = random.choice(cls.WHITE_DEFENSE)
            if result in ["block", "surge"]:
                removed += 1
        return removed
    
    @classmethod
    def reroll(cls, dice_results: Dict[str, int], count: int, dice_type: str = "attack") -> Dict[str, int]:
        """Würfelt Würfel neu (z.B. durch Aim-Marker)."""
        # Sammle alle negativen Ergebnisse zum Neuwürfeln
        rerollable = []
        if dice_type == "attack":
            if dice_results.get("blank", 0) > 0:
                rerollable.extend(["blank"] * dice_results["blank"])
            if dice_results.get("surge", 0) > 0:
                rerollable.extend(["surge"] * dice_results["surge"])
        else:
            if dice_results.get("blank", 0) > 0:
                rerollable.extend(["blank"] * dice_results["blank"])
                
        # Begrenzen auf verfügbare Würfel
        count = min(count, len(rerollable))
        
        # Würfel neu würfeln (hier vereinfacht mit White Attack)
        new_results = dice_results.copy()
        for i in range(count):
            old_result = rerollable[i]
            new_results[old_result] -= 1
            
            if dice_type == "attack":
                new_result = random.choice(cls.WHITE_ATTACK)
            else:
                new_result = random.choice(cls.WHITE_DEFENSE)
            new_results[new_result] = new_results.get(new_result, 0) + 1
            
        return new_results


class CombatResolver:
    """Kampf-Auflösung gemäß Star Wars Legion Regeln."""
    
    def __init__(self, rules: LegionRules):
        self.rules = rules
        self.dice_roller = DiceRoller()
    
    def resolve_attack(self, attacker: Dict, defender: Dict, 
                       weapon: Dict, distance: str = "range_3") -> Dict:
        """
        Führt einen kompletten Angriff durch.
        
        Returns:
            Dict mit Ergebnis: wounds, suppression, special_effects
        """
        result = {
            "wounds": 0,
            "suppression": 1,  # Jeder Angriff verursacht mindestens 1 Suppression
            "crits": 0,
            "blocked": 0,
            "effects": [],
            "attack_rolls": {},
            "defense_rolls": {}
        }
        
        # 1. ANGRIFFSWÜRFEL SAMMELN
        attack_pool = self._build_attack_pool(attacker, weapon)
        
        # 2. WÜRFELN
        attack_results = self.dice_roller.roll_attack(
            red=attack_pool.get("red", 0),
            black=attack_pool.get("black", 0),
            white=attack_pool.get("white", 0)
        )
        result["attack_rolls"] = attack_results.copy()
        
        # 3. MODIFIKATIONEN ANWENDEN
        
        # Aim-Marker nutzen (2 Würfel pro Aim neu würfeln)
        aim_tokens = attacker.get("aim", 0)
        if aim_tokens > 0:
            reroll_count = aim_tokens * 2
            
            # Precise X Keyword prüfen
            precise_x = self._get_keyword_value(attacker, "Precise")
            if precise_x:
                reroll_count += precise_x
                
            attack_results = self.dice_roller.reroll(attack_results, reroll_count, "attack")
            attacker["aim"] = 0  # Aims verbraucht
            result["effects"].append(f"Aim verwendet: {reroll_count} Würfel neu gewürfelt")
        
        # Lethal X Keyword prüfen (Surges in Crits umwandeln)
        lethal_x = self._get_keyword_value(attacker, "Lethal")
        if lethal_x and attacker.get("aim", 0) > 0:
            surges_to_convert = min(attack_results.get("surge", 0), lethal_x)
            attack_results["surge"] -= surges_to_convert
            attack_results["crit"] += surges_to_convert
            result["effects"].append(f"Lethal: {surges_to_convert} Surges zu Crits")
        
        # Critical X Keyword prüfen
        critical_x = self._get_keyword_value(weapon, "Critical")
        if critical_x:
            surges_to_convert = min(attack_results.get("surge", 0), critical_x)
            attack_results["surge"] -= surges_to_convert
            attack_results["crit"] += surges_to_convert
        
        # Attack Surge Conversion
        surge_to_hit = attacker.get("surge_to_hit", False) or weapon.get("surge_to_hit", False)
        if surge_to_hit:
            attack_results["hit"] += attack_results.get("surge", 0)
            attack_results["surge"] = 0
        
        # Treffer zählen
        total_hits = attack_results.get("hit", 0) + attack_results.get("crit", 0)
        result["crits"] = attack_results.get("crit", 0)
        
        if total_hits == 0:
            result["effects"].append("Keine Treffer!")
            return result
        
        # 4. DECKUNG BERECHNEN
        cover_value = self._calculate_cover(attacker, defender, weapon)
        
        # Sharpshooter X reduziert Deckung
        sharpshooter_x = self._get_keyword_value(attacker, "Sharpshooter")
        if sharpshooter_x:
            cover_value = max(0, cover_value - sharpshooter_x)
            result["effects"].append(f"Sharpshooter: Deckung -{sharpshooter_x}")
        
        # Blast ignoriert Deckung komplett
        if self._has_keyword(weapon, "Blast"):
            cover_value = 0
            result["effects"].append("Blast: Deckung ignoriert!")
        
        # 5. VERTEIDIGUNG WÜRFELN
        defense_pool = self._build_defense_pool(defender, total_hits)
        defense_results = self.dice_roller.roll_defense(
            red=defense_pool.get("red", 0),
            white=defense_pool.get("white", 0)
        )
        result["defense_rolls"] = defense_results.copy()
        
        # Danger Sense X: Extra Würfel pro Suppression
        danger_sense_x = self._get_keyword_value(defender, "Danger Sense")
        if danger_sense_x:
            extra_dice = min(defender.get("suppression", 0), danger_sense_x)
            if extra_dice > 0:
                extra_results = self.dice_roller.roll_defense(white=extra_dice)
                for key, val in extra_results.items():
                    defense_results[key] = defense_results.get(key, 0) + val
                result["effects"].append(f"Danger Sense: +{extra_dice} Verteidigungswürfel")
        
        # Defense Surge Conversion
        surge_to_block = defender.get("surge_to_block", False)
        if surge_to_block:
            defense_results["block"] += defense_results.get("surge", 0)
            defense_results["surge"] = 0
        
        # Deflect: Wenn Dodge ausgegeben, Surge -> Block
        if self._has_keyword(defender, "Deflect") and defender.get("dodge", 0) > 0:
            defense_results["block"] += defense_results.get("surge", 0)
            surges_reflected = defense_results.get("surge", 0)
            defense_results["surge"] = 0
            # Angreifer erleidet Wunden für jeden Surge
            if surges_reflected > 0:
                result["effects"].append(f"Deflect: {surges_reflected} Wunden reflektiert!")
        
        # Dodge-Marker nutzen
        if defender.get("dodge", 0) > 0:
            # High Velocity verhindert Dodge
            if not self._has_keyword(weapon, "High Velocity"):
                dodges_used = min(defender["dodge"], total_hits)
                total_hits -= dodges_used
                defender["dodge"] -= dodges_used
                result["effects"].append(f"Dodge: {dodges_used} Treffer negiert")
                
                # Nimble: Dodge zurückerhalten
                if self._has_keyword(defender, "Nimble") and dodges_used > 0:
                    defender["dodge"] += 1
                    result["effects"].append("Nimble: 1 Dodge zurückerhalten")
        
        # Deckung anwenden
        total_blocks = defense_results.get("block", 0) + cover_value
        result["blocked"] = total_blocks
        
        # 6. PIERCE ANWENDEN
        pierce_x = self._get_keyword_value(weapon, "Pierce")
        if pierce_x:
            # Immune: Pierce prüfen
            if not self._has_keyword(defender, "Immune: Pierce") and not self._has_keyword(defender, "Impervious"):
                blocks_negated = min(total_blocks, pierce_x)
                total_blocks -= blocks_negated
                result["effects"].append(f"Pierce: {blocks_negated} Blocks negiert")
        
        # 7. ARMOR PRÜFEN
        has_armor = self._has_keyword(defender, "Armor")
        armor_x = self._get_keyword_value(defender, "Armor")
        
        wounds = 0
        if has_armor and not armor_x:
            # Armor (ohne X): Nur Crits verursachen Schaden
            wounds = result["crits"]
            result["effects"].append("Armor: Nur Crits verursachen Schaden")
        elif armor_x:
            # Armor X: Blockiert X normale Treffer
            normal_hits = attack_results.get("hit", 0)
            blocked_by_armor = min(normal_hits, armor_x)
            wounds = max(0, total_hits - total_blocks - blocked_by_armor)
            result["effects"].append(f"Armor {armor_x}: {blocked_by_armor} Treffer blockiert")
        else:
            # Keine Armor
            wounds = max(0, total_hits - total_blocks)
        
        # Impact X: Hits zu Crits gegen Armor
        if has_armor or armor_x:
            impact_x = self._get_keyword_value(weapon, "Impact")
            if impact_x:
                hits_to_convert = min(attack_results.get("hit", 0), impact_x)
                result["effects"].append(f"Impact: {hits_to_convert} Hits zu Crits")
                wounds += hits_to_convert  # Diese umgehen jetzt Armor
        
        result["wounds"] = wounds
        
        # 8. SUPPRESSIVE KEYWORD
        if self._has_keyword(weapon, "Suppressive"):
            result["suppression"] = max(1, result["suppression"])
            result["effects"].append("Suppressive: Mindestens 1 Suppression")
        
        # 9. ION KEYWORD
        ion_x = self._get_keyword_value(weapon, "Ion")
        if ion_x:
            result["ion_tokens"] = ion_x
            result["effects"].append(f"Ion: {ion_x} Ion-Marker")
        
        # 10. POISON KEYWORD
        poison_x = self._get_keyword_value(weapon, "Poison")
        if poison_x:
            result["poison_tokens"] = poison_x
            result["effects"].append(f"Poison: {poison_x} Gift-Marker")
        
        return result
    
    def _build_attack_pool(self, attacker: Dict, weapon: Dict) -> Dict[str, int]:
        """Baut den Angriffswürfelpool."""
        pool = {"red": 0, "black": 0, "white": 0}
        
        # Würfel aus Waffe
        dice_str = weapon.get("dice", "")
        if isinstance(dice_str, str):
            # Parse "2R 1B 1W" format
            for part in dice_str.split():
                if "R" in part.upper():
                    pool["red"] += int(part[:-1]) if part[:-1].isdigit() else 1
                elif "B" in part.upper() and "L" not in part.upper():
                    pool["black"] += int(part[:-1]) if part[:-1].isdigit() else 1
                elif "W" in part.upper():
                    pool["white"] += int(part[:-1]) if part[:-1].isdigit() else 1
        elif isinstance(dice_str, dict):
            pool["red"] = dice_str.get("red", 0)
            pool["black"] = dice_str.get("black", 0)
            pool["white"] = dice_str.get("white", 0)
        
        return pool
    
    def _build_defense_pool(self, defender: Dict, hits: int) -> Dict[str, int]:
        """Baut den Verteidigungswürfelpool."""
        pool = {"red": 0, "white": 0}
        
        defense_type = defender.get("defense", "white").lower()
        
        # Miniaturen in der Einheit bestimmen Würfelanzahl
        minis = defender.get("minis", 1)
        
        if "red" in defense_type:
            pool["red"] = minis
        else:
            pool["white"] = minis
        
        # Low Profile: 1 Würfel weniger
        if self._has_keyword(defender, "Low Profile"):
            if pool["red"] > 0:
                pool["red"] = max(0, pool["red"] - 1)
            elif pool["white"] > 0:
                pool["white"] = max(0, pool["white"] - 1)
        
        return pool
    
    def _calculate_cover(self, attacker: Dict, defender: Dict, weapon: Dict) -> int:
        """Berechnet den Deckungswert."""
        cover = defender.get("cover", 0)
        
        # Cover X Keyword
        cover_x = self._get_keyword_value(defender, "Cover")
        if cover_x:
            cover = max(cover, cover_x)
        
        # Low Profile: +1 Block
        if self._has_keyword(defender, "Low Profile"):
            cover += 1
        
        return cover
    
    def _has_keyword(self, entity: Dict, keyword: str) -> bool:
        """Prüft ob eine Einheit/Waffe ein Keyword hat."""
        keywords = entity.get("keywords", [])
        if isinstance(keywords, list):
            for kw in keywords:
                if isinstance(kw, str) and keyword.lower() in kw.lower():
                    return True
        return False
    
    def _get_keyword_value(self, entity: Dict, keyword: str) -> Optional[int]:
        """Extrahiert den numerischen Wert eines Keywords (z.B. Pierce 2 -> 2)."""
        keywords = entity.get("keywords", [])
        if isinstance(keywords, list):
            for kw in keywords:
                if isinstance(kw, str) and keyword.lower() in kw.lower():
                    # Parse "Keyword X" format
                    parts = kw.split()
                    if len(parts) >= 2 and parts[-1].isdigit():
                        return int(parts[-1])
                    return 1  # Keyword vorhanden aber ohne Wert
        return None


class PhaseManager:
    """Verwaltet den Spielphasenablauf gemäß Regeln."""
    
    PHASES = ["Setup", "Command", "Activation", "End"]
    MAX_ROUNDS = 6
    
    def __init__(self):
        self.current_phase = "Setup"
        self.current_round = 0
        self.phase_index = 0
        self.rules = LegionRules
    
    def start_game(self) -> Dict:
        """Startet ein neues Spiel."""
        self.current_round = 1
        self.current_phase = "Command"
        self.phase_index = 1
        
        return {
            "round": self.current_round,
            "phase": self.current_phase,
            "steps": self.rules.PHASES["command"]["steps"]
        }
    
    def advance_phase(self) -> Dict:
        """Wechselt zur nächsten Phase."""
        self.phase_index += 1
        
        if self.phase_index >= len(self.PHASES):
            # Neue Runde
            self.phase_index = 1  # Skip Setup
            self.current_round += 1
            
            if self.current_round > self.MAX_ROUNDS:
                return {"game_over": True, "round": self.current_round}
        
        self.current_phase = self.PHASES[self.phase_index]
        phase_key = self.current_phase.lower()
        
        return {
            "round": self.current_round,
            "phase": self.current_phase,
            "steps": self.rules.PHASES.get(phase_key, {}).get("steps", [])
        }
    
    def get_current_state(self) -> Dict:
        """Gibt den aktuellen Spielstand zurück."""
        phase_key = self.current_phase.lower()
        return {
            "round": self.current_round,
            "phase": self.current_phase,
            "phase_name": self.rules.PHASES.get(phase_key, {}).get("name", self.current_phase),
            "steps": self.rules.PHASES.get(phase_key, {}).get("steps", [])
        }


class UnitStateManager:
    """Verwaltet Einheitenzustände gemäß Regeln."""
    
    def __init__(self):
        self.rules = LegionRules
    
    def apply_suppression(self, unit: Dict, amount: int = 1) -> Dict:
        """Fügt Suppression hinzu und prüft Status."""
        unit["suppression"] = unit.get("suppression", 0) + amount
        
        courage = self._get_courage(unit)
        suppression = unit["suppression"]
        
        status = {
            "suppression": suppression,
            "is_suppressed": False,
            "is_panicked": False,
            "actions_lost": 0
        }
        
        if suppression >= courage * 2:
            status["is_panicked"] = True
            status["actions_lost"] = 2
            unit["panic"] = True
        elif suppression >= courage:
            status["is_suppressed"] = True
            status["actions_lost"] = 1
            unit["suppressed"] = True
        
        return status
    
    def perform_rally(self, unit: Dict) -> Dict:
        """Führt Rally-Schritt durch."""
        suppression = unit.get("suppression", 0)
        
        if suppression == 0:
            return {"removed": 0, "remaining": 0}
        
        removed = DiceRoller.roll_rally(suppression)
        unit["suppression"] = max(0, suppression - removed)
        
        # Status aktualisieren
        courage = self._get_courage(unit)
        if unit["suppression"] < courage:
            unit.pop("suppressed", None)
            unit.pop("panic", None)
        elif unit["suppression"] < courage * 2:
            unit.pop("panic", None)
        
        return {
            "removed": removed,
            "remaining": unit["suppression"],
            "dice_rolled": suppression
        }
    
    def end_phase_cleanup(self, unit: Dict) -> Dict:
        """Führt End-Phasen-Aufräumung durch."""
        changes = []
        
        # Marker entfernen
        if unit.get("aim", 0) > 0:
            changes.append(f"Aim entfernt: {unit['aim']}")
            unit["aim"] = 0
            
        if unit.get("dodge", 0) > 0:
            changes.append(f"Dodge entfernt: {unit['dodge']}")
            unit["dodge"] = 0
            
        if unit.get("standby", False):
            changes.append("Standby entfernt")
            unit["standby"] = False
        
        # 1 Suppression entfernen
        if unit.get("suppression", 0) > 0:
            unit["suppression"] -= 1
            changes.append("1 Suppression entfernt")
        
        # Aktivierungsstatus zurücksetzen
        unit["activated"] = False
        unit["order_token"] = False
        
        return {"changes": changes}
    
    def check_unit_status(self, unit: Dict) -> Dict:
        """Prüft den aktuellen Status einer Einheit."""
        courage = self._get_courage(unit)
        suppression = unit.get("suppression", 0)
        
        hp = unit.get("current_hp", unit.get("hp", 1))
        max_hp = unit.get("hp", 1)
        minis = unit.get("minis", 1)
        
        status = {
            "alive": hp > 0,
            "wounded": hp < max_hp,
            "suppressed": suppression >= courage,
            "panicked": suppression >= courage * 2,
            "has_aim": unit.get("aim", 0) > 0,
            "has_dodge": unit.get("dodge", 0) > 0,
            "has_standby": unit.get("standby", False),
            "activated": unit.get("activated", False),
            "has_order": unit.get("order_token", False)
        }
        
        # Keywords-basierte Status
        keywords = unit.get("keywords", [])
        status["is_droid"] = any("Droid" in str(kw) for kw in keywords)
        status["has_armor"] = any("Armor" in str(kw) for kw in keywords)
        status["is_vehicle"] = unit.get("unit_type", "").lower() in ["vehicle", "heavy", "repulsor"]
        
        # Droiden können nicht paniken
        if status["is_droid"]:
            status["panicked"] = False
        
        return status
    
    def _get_courage(self, unit: Dict) -> int:
        """Extrahiert Mut-Wert."""
        courage = unit.get("courage", 1)
        if courage in ["-", "", None]:
            return 999  # Droiden haben effektiv unendlichen Mut
        try:
            return int(courage)
        except (ValueError, TypeError):
            return 1


class MovementCalculator:
    """Berechnet Bewegung gemäß Regeln."""
    
    SPEED_VALUES = {
        "1": 1,
        "2": 2,
        "3": 3,
        "-": 0
    }
    
    def __init__(self):
        self.rules = LegionRules
    
    def get_movement_options(self, unit: Dict, terrain: str = "open") -> Dict:
        """Berechnet verfügbare Bewegungsoptionen."""
        speed = str(unit.get("speed", "2"))
        speed_value = self.SPEED_VALUES.get(speed, 2)
        
        options = {
            "base_speed": speed_value,
            "effective_speed": speed_value,
            "can_climb": False,
            "can_jump": False,
            "jump_height": 0,
            "modifiers": []
        }
        
        # Terrain-Modifikatoren
        terrain_info = self.rules.TERRAIN.get(terrain.lower(), {})
        if terrain_info.get("movement") == "Halbe Geschwindigkeit":
            options["effective_speed"] = max(1, speed_value // 2)
            options["modifiers"].append("Schwieriges Gelände: halbe Bewegung")
        elif terrain_info.get("movement") == "Blockiert":
            options["effective_speed"] = 0
            options["modifiers"].append("Unpassierbares Gelände!")
        
        # Keywords prüfen
        keywords = unit.get("keywords", [])
        
        for kw in keywords:
            kw_str = str(kw)
            
            # Jump X
            if "Jump" in kw_str:
                options["can_jump"] = True
                parts = kw_str.split()
                if len(parts) >= 2 and parts[-1].isdigit():
                    options["jump_height"] = int(parts[-1])
                else:
                    options["jump_height"] = 1
                options["modifiers"].append(f"Jump: Kann bis Höhe {options['jump_height']} springen")
            
            # Scale
            if "Scale" in kw_str:
                options["can_climb"] = True
                options["modifiers"].append("Scale: Kann als Teil der Bewegung klettern")
            
            # Unhindered
            if "Unhindered" in kw_str:
                if "Schwieriges Gelände" in str(options["modifiers"]):
                    options["effective_speed"] = speed_value
                    options["modifiers"].append("Unhindered: Ignoriert schwieriges Gelände")
            
            # Speeder
            if "Speeder" in kw_str:
                options["must_move"] = True
                options["modifiers"].append("Speeder: Muss sich jede Runde bewegen")
            
            # Stationary
            if "Stationary" in kw_str:
                options["effective_speed"] = 0
                options["modifiers"].append("Stationary: Kann sich nicht bewegen")
        
        return options


class AIDecisionMaker:
    """KI-Entscheidungslogik basierend auf Regeln."""
    
    def __init__(self):
        self.rules = LegionRules
        self.combat = CombatResolver(self.rules)
        self.movement = MovementCalculator()
    
    def decide_action(self, unit: Dict, game_state: Dict) -> Dict:
        """Entscheidet die beste Aktion für eine Einheit."""
        actions_remaining = game_state.get("actions_remaining", 2)
        enemies = game_state.get("enemies", [])
        allies = game_state.get("allies", [])
        
        decision = {
            "action": None,
            "target": None,
            "reasoning": []
        }
        
        # Status prüfen
        status = UnitStateManager().check_unit_status(unit)
        
        if status["panicked"]:
            decision["action"] = "flee"
            decision["reasoning"].append("Einheit ist in Panik - muss fliehen")
            return decision
        
        # Taktische Entscheidung
        unit_role = self._determine_unit_role(unit)
        
        if unit_role == "ranged":
            decision = self._decide_ranged_action(unit, enemies, actions_remaining)
        elif unit_role == "melee":
            decision = self._decide_melee_action(unit, enemies, actions_remaining)
        elif unit_role == "support":
            decision = self._decide_support_action(unit, allies, enemies, actions_remaining)
        else:
            decision = self._decide_generic_action(unit, enemies, actions_remaining)
        
        return decision
    
    def _determine_unit_role(self, unit: Dict) -> str:
        """Bestimmt die Rolle einer Einheit."""
        weapons = unit.get("weapons", [])
        keywords = unit.get("keywords", [])
        
        has_melee = any(w.get("range", "") == "Melee" for w in weapons)
        has_ranged = any(w.get("range", "") not in ["Melee", ""] for w in weapons)
        
        # Keywords analysieren
        for kw in keywords:
            kw_str = str(kw)
            if "Charge" in kw_str:
                return "melee"
            if "Sharpshooter" in kw_str or "Sniper" in kw_str:
                return "ranged"
            if "Treat" in kw_str or "Repair" in kw_str:
                return "support"
        
        if has_melee and not has_ranged:
            return "melee"
        elif has_ranged:
            return "ranged"
        
        return "generic"
    
    def _decide_ranged_action(self, unit: Dict, enemies: List, actions: int) -> Dict:
        """Entscheidung für Fernkampf-Einheit."""
        decision = {"action": None, "target": None, "reasoning": []}
        
        # Beste Ziele finden
        best_target = None
        best_score = 0
        
        for enemy in enemies:
            if enemy.get("current_hp", 0) <= 0:
                continue
            
            score = self._calculate_target_priority(enemy)
            if score > best_score:
                best_score = score
                best_target = enemy
        
        if best_target:
            # Aim + Attack Combo
            if actions >= 2 and unit.get("aim", 0) == 0:
                decision["action"] = "aim"
                decision["next_action"] = "attack"
                decision["target"] = best_target
                decision["reasoning"].append(f"Ziele auf {best_target.get('name', 'Feind')} für bessere Trefferchance")
            else:
                decision["action"] = "attack"
                decision["target"] = best_target
                decision["reasoning"].append(f"Angriff auf {best_target.get('name', 'Feind')}")
        else:
            # Keine Ziele - Dodge oder Standby
            if unit.get("dodge", 0) == 0:
                decision["action"] = "dodge"
                decision["reasoning"].append("Keine Ziele in Reichweite - Ausweichen")
            else:
                decision["action"] = "standby"
                decision["reasoning"].append("Bereitschaft für Reaktion")
        
        return decision
    
    def _decide_melee_action(self, unit: Dict, enemies: List, actions: int) -> Dict:
        """Entscheidung für Nahkampf-Einheit."""
        decision = {"action": None, "target": None, "reasoning": []}
        
        # Nächsten Feind finden
        closest_enemy = None
        for enemy in enemies:
            if enemy.get("current_hp", 0) > 0:
                closest_enemy = enemy
                break
        
        if closest_enemy:
            # Charge: Bewegung + freier Nahkampf
            has_charge = any("Charge" in str(kw) for kw in unit.get("keywords", []))
            
            if has_charge and actions >= 1:
                decision["action"] = "move_charge"
                decision["target"] = closest_enemy
                decision["reasoning"].append("Charge zum Feind!")
            elif actions >= 2:
                decision["action"] = "move"
                decision["next_action"] = "attack"
                decision["target"] = closest_enemy
                decision["reasoning"].append("Bewegen und angreifen")
            else:
                decision["action"] = "attack"
                decision["target"] = closest_enemy
        else:
            decision["action"] = "move"
            decision["reasoning"].append("Keine Feinde in Reichweite - vorwärts!")
        
        return decision
    
    def _decide_support_action(self, unit: Dict, allies: List, enemies: List, actions: int) -> Dict:
        """Entscheidung für Support-Einheit."""
        decision = {"action": None, "target": None, "reasoning": []}
        
        # Verwundete Verbündete finden
        wounded_allies = [a for a in allies if a.get("current_hp", 0) < a.get("hp", 1)]
        
        if wounded_allies:
            decision["action"] = "treat"
            decision["target"] = wounded_allies[0]
            decision["reasoning"].append(f"Heile {wounded_allies[0].get('name', 'Verbündeten')}")
        else:
            # Keine Verwundeten - normale Aktion
            decision = self._decide_ranged_action(unit, enemies, actions)
        
        return decision
    
    def _decide_generic_action(self, unit: Dict, enemies: List, actions: int) -> Dict:
        """Generische Entscheidung."""
        decision = {"action": None, "target": None, "reasoning": []}
        
        if enemies and actions >= 1:
            decision["action"] = "attack"
            decision["target"] = enemies[0] if enemies[0].get("current_hp", 0) > 0 else None
            decision["reasoning"].append("Angriff auf nächsten Feind")
        else:
            decision["action"] = "dodge"
            decision["reasoning"].append("Defensiv: Ausweichen")
        
        return decision
    
    def _calculate_target_priority(self, enemy: Dict) -> int:
        """Berechnet Priorität eines Ziels."""
        score = 0
        
        # Niedrige HP = hohe Priorität
        hp_percent = enemy.get("current_hp", 1) / max(enemy.get("hp", 1), 1)
        if hp_percent < 0.3:
            score += 50
        elif hp_percent < 0.6:
            score += 30
        
        # Commander = hohe Priorität
        rank = enemy.get("rank", "").lower()
        if "commander" in rank:
            score += 40
        elif "operative" in rank:
            score += 30
        elif "special" in rank:
            score += 20
        
        # Gefährliche Keywords
        keywords = enemy.get("keywords", [])
        dangerous_keywords = ["Sharpshooter", "Pierce", "Impact", "Lethal"]
        for kw in keywords:
            for dk in dangerous_keywords:
                if dk in str(kw):
                    score += 10
        
        return score
    
    def select_command_card(self, hand: List[Dict], game_state: Dict) -> Dict:
        """Wählt die beste Kommandokarte aus."""
        round_number = game_state.get("round", 1)
        enemy_threat = game_state.get("enemy_threat_level", "medium")
        
        # Strategie basierend auf Runde
        if round_number <= 2:
            # Frühe Runde: Hohe Pip-Karten für Positionierung
            target_pips = 3
        elif round_number <= 4:
            # Mitte: Ausgewogen
            target_pips = 2
        else:
            # Späte Runde: Niedrige Pips für Priorität
            target_pips = 1
        
        # Beste Karte finden
        best_card = None
        best_score = -1
        
        for card in hand:
            pips = card.get("pips", 4)
            score = 10 - abs(pips - target_pips)
            
            # Kartentext analysieren für Bonus
            text = card.get("text", "").lower()
            if "attack" in text or "damage" in text:
                if enemy_threat == "high":
                    score += 5
            if "dodge" in text or "cover" in text:
                if enemy_threat == "high":
                    score += 3
            
            if score > best_score:
                best_score = score
                best_card = card
        
        return best_card if best_card else (hand[0] if hand else None)


# Utility-Funktion zum Exportieren
def get_game_engine():
    """Factory-Funktion für Game-Engine-Komponenten."""
    return {
        "dice": DiceRoller(),
        "combat": CombatResolver(LegionRules),
        "phases": PhaseManager(),
        "units": UnitStateManager(),
        "movement": MovementCalculator(),
        "ai": AIDecisionMaker()
    }
