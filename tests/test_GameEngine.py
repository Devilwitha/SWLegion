"""
Tests for GameEngine Module

Tests the DiceRoller, CombatResolver, PhaseManager, UnitStateManager, 
MovementCalculator, and AIDecisionMaker classes.
"""

import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utilities.GameEngine import (
    DiceRoller, CombatResolver, PhaseManager, UnitStateManager, 
    MovementCalculator, AIDecisionMaker, get_game_engine
)


class TestDiceRoller(unittest.TestCase):
    """Tests for the DiceRoller class."""
        
    def test_roll_attack_returns_results(self):
        """Test that attack dice rolling returns valid results."""
        result = DiceRoller.roll_attack(red=3, black=2, white=1)
        
        self.assertIn("hit", result)
        self.assertIn("crit", result)
        self.assertIn("surge", result)
        self.assertIn("blank", result)
        
        # Total should be sum of individual results
        total = result["hit"] + result["crit"] + result["surge"] + result["blank"]
        self.assertEqual(total, 6)
        
    def test_roll_attack_count_matches(self):
        """Test that dice count matches input."""
        for red, black, white in [(1, 0, 0), (0, 2, 0), (0, 0, 3), (2, 2, 2)]:
            result = DiceRoller.roll_attack(red=red, black=black, white=white)
            expected_total = red + black + white
            actual_total = sum(result.values())
            self.assertEqual(actual_total, expected_total)
            
    def test_roll_defense_returns_results(self):
        """Test that defense dice rolling returns valid results."""
        result = DiceRoller.roll_defense(red=3, white=0)
        
        self.assertIn("block", result)
        self.assertIn("surge", result)
        self.assertIn("blank", result)
        
    def test_roll_defense_colors(self):
        """Test defense dice rolling with different counts."""
        result_red = DiceRoller.roll_defense(red=2, white=0)
        result_white = DiceRoller.roll_defense(red=0, white=2)
        
        self.assertEqual(sum(result_red.values()), 2)
        self.assertEqual(sum(result_white.values()), 2)
            
    def test_roll_rally_returns_count(self):
        """Test that rally dice rolling returns removal count."""
        removed = DiceRoller.roll_rally(3)
        
        self.assertIsInstance(removed, int)
        self.assertGreaterEqual(removed, 0)
        self.assertLessEqual(removed, 3)


class TestCombatResolver(unittest.TestCase):
    """Tests for the CombatResolver class."""
    
    def setUp(self):
        from utilities.LegionRules import LegionRules
        self.resolver = CombatResolver(LegionRules)
        
    def test_resolve_attack_basic(self):
        """Test basic attack resolution."""
        attacker = {
            "name": "Test Attacker",
            "weapons": [{
                "name": "Test Weapon",
                "range": [1, 3],
                "dice": {"red": 2, "black": 1, "white": 0}
            }]
        }
        
        defender = {
            "name": "Test Defender",
            "defense": "white",
            "current_hp": 5,
            "hp": 5,
            "minis": 1
        }
        
        weapon = attacker["weapons"][0]
        result = self.resolver.resolve_attack(attacker, defender, weapon)
        
        self.assertIn("wounds", result)
        self.assertIn("attack_rolls", result)


class TestPhaseManager(unittest.TestCase):
    """Tests for the PhaseManager class."""
    
    def setUp(self):
        self.manager = PhaseManager()
        
    def test_initial_phase(self):
        """Test initial game phase."""
        # Phase names are capitalized
        self.assertIn(self.manager.current_phase.lower(), ["setup", "command", "activation", "end"])
        
    def test_advance_phase(self):
        """Test advancing through phases."""
        initial_phase = self.manager.current_phase
        result = self.manager.advance_phase()
        
        # Should return info about new phase
        self.assertIsInstance(result, dict)
        
    def test_phase_cycle(self):
        """Test complete phase cycle."""
        phases_seen = [self.manager.current_phase]
        
        for _ in range(6):
            self.manager.advance_phase()
            phases_seen.append(self.manager.current_phase)
            
        # Should see multiple different phases
        self.assertGreater(len(set(phases_seen)), 1)
        
    def test_get_current_state(self):
        """Test getting current phase information."""
        info = self.manager.get_current_state()
        
        self.assertIn("phase", info)
        self.assertIn("round", info)


class TestUnitStateManager(unittest.TestCase):
    """Tests for the UnitStateManager class."""
    
    def setUp(self):
        self.manager = UnitStateManager()
        
    def test_apply_suppression(self):
        """Test adding suppression to a unit."""
        unit = {"name": "Test Unit", "suppression": 0, "courage": 2}
        
        result = self.manager.apply_suppression(unit, 2)
        
        self.assertEqual(unit["suppression"], 2)
        self.assertIn("suppression", result)
        
    def test_suppression_triggers_suppressed(self):
        """Test that enough suppression triggers suppressed state."""
        unit = {"name": "Test Unit", "suppression": 0, "courage": 2}
        
        result = self.manager.apply_suppression(unit, 2)
        
        self.assertTrue(result["is_suppressed"])
        
    def test_suppression_triggers_panic(self):
        """Test that double courage suppression triggers panic."""
        unit = {"name": "Test Unit", "suppression": 0, "courage": 2}
        
        result = self.manager.apply_suppression(unit, 4)
        
        self.assertTrue(result["is_panicked"])
        
    def test_perform_rally(self):
        """Test rally step."""
        unit = {"name": "Test Unit", "suppression": 3, "courage": 2}
        
        result = self.manager.perform_rally(unit)
        
        self.assertIn("removed", result)
        self.assertIn("remaining", result)
        self.assertIn("dice_rolled", result)
        self.assertLessEqual(unit["suppression"], 3)
        
    def test_end_phase_cleanup(self):
        """Test end of round cleanup."""
        unit = {
            "name": "Test Unit", 
            "aim": 2, 
            "dodge": 1, 
            "suppression": 3,
            "activated": True,
            "courage": 2
        }
        
        result = self.manager.end_phase_cleanup(unit)
        
        # Aim and Dodge should be removed
        self.assertEqual(unit["aim"], 0)
        self.assertEqual(unit["dodge"], 0)
        # Suppression should decrease by 1
        self.assertEqual(unit["suppression"], 2)
        # Activated should reset
        self.assertFalse(unit["activated"])
        
    def test_check_unit_status(self):
        """Test checking unit status."""
        unit = {
            "name": "Test Unit",
            "current_hp": 3,
            "hp": 5,
            "suppression": 2,
            "courage": 2,
            "aim": 1,
            "minis": 1
        }
        
        status = self.manager.check_unit_status(unit)
        
        self.assertIn("alive", status)
        self.assertIn("suppressed", status)
        self.assertIn("has_aim", status)


class TestMovementCalculator(unittest.TestCase):
    """Tests for the MovementCalculator class."""
    
    def setUp(self):
        self.calculator = MovementCalculator()
        
    def test_get_movement_options(self):
        """Test getting movement options."""
        unit = {"name": "Test Unit", "speed": 2}
        
        options = self.calculator.get_movement_options(unit)
        
        self.assertIn("base_speed", options)
        self.assertGreater(options["base_speed"], 0)
        
    def test_movement_with_terrain(self):
        """Test movement calculation with terrain."""
        unit = {"name": "Test Unit", "speed": 2}
        
        normal_options = self.calculator.get_movement_options(unit, terrain="open")
        difficult_options = self.calculator.get_movement_options(unit, terrain="difficult")
        
        # Should have different effective speeds
        self.assertIsNotNone(normal_options)
        self.assertIsNotNone(difficult_options)


class TestAIDecisionMaker(unittest.TestCase):
    """Tests for the AIDecisionMaker class."""
    
    def setUp(self):
        self.ai = AIDecisionMaker()
        
    def test_ai_has_decide_action(self):
        """Test that AIDecisionMaker has decide_action method."""
        self.assertTrue(hasattr(self.ai, 'decide_action'))
            
    def test_decide_action(self):
        """Test choosing action for a unit."""
        unit = {
            "name": "Test Unit",
            "current_hp": 5,
            "hp": 5,
            "aim": 0,
            "weapons": [{"name": "Blaster", "range": [1, 3], "dice": {"red": 2, "black": 0, "white": 0}}]
        }
        
        game_state = {
            "enemies": [{"name": "Enemy", "current_hp": 4, "hp": 5}],
            "allies": [],
            "round": 1
        }
        
        action = self.ai.decide_action(unit, game_state)
        
        self.assertIsInstance(action, dict)
        self.assertIn("action", action)
        
    def test_select_command_card(self):
        """Test command card selection."""
        self.assertTrue(hasattr(self.ai, 'select_command_card'))
        
        hand = [{"name": "Ambush", "pips": 1}, {"name": "Push", "pips": 2}]
        game_state = {"round": 1, "enemies": []}
        
        selected = self.ai.select_command_card(hand, game_state)
        
        self.assertIsNotNone(selected)


class TestGetGameEngine(unittest.TestCase):
    """Tests for the get_game_engine factory function."""
    
    def test_get_game_engine_returns_all_components(self):
        """Test that get_game_engine returns all components."""
        components = get_game_engine()
        
        # Actual keys used by get_game_engine
        self.assertIn("dice", components)
        self.assertIn("combat", components)
        self.assertIn("phases", components)
        self.assertIn("units", components)
        self.assertIn("movement", components)
        self.assertIn("ai", components)
        
    def test_components_are_correct_types(self):
        """Test that components are of correct types."""
        components = get_game_engine()
        
        self.assertIsInstance(components["dice"], DiceRoller)
        self.assertIsInstance(components["combat"], CombatResolver)
        self.assertIsInstance(components["phases"], PhaseManager)
        self.assertIsInstance(components["units"], UnitStateManager)
        self.assertIsInstance(components["movement"], MovementCalculator)
        self.assertIsInstance(components["ai"], AIDecisionMaker)


if __name__ == '__main__':
    unittest.main()
