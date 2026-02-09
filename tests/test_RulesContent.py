import unittest
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utilities.LegionRules import LegionRules

class TestLegionRulesExtended(unittest.TestCase):
    def test_phase_logic(self):
        """Test specific rule contents."""
        setup = LegionRules.PHASES["setup"]
        self.assertTrue(len(setup["steps"]) > 0)
        # Check if any step contains "Armeezusammenstellung"
        self.assertTrue(any("Armeezusammenstellung" in step for step in setup["steps"]))

    def test_action_descriptions(self):
        """Test that actions have descriptions."""
        move = LegionRules.ACTIONS["move"]
        self.assertTrue(len(move["description"]) > 5)


class TestLegionRulesKeywords(unittest.TestCase):
    """Tests for keyword definitions."""
    
    def test_keywords_exist(self):
        """Test that KEYWORDS dictionary exists and has content."""
        self.assertTrue(hasattr(LegionRules, 'KEYWORDS'))
        self.assertGreater(len(LegionRules.KEYWORDS), 0)
        
    def test_common_keywords_present(self):
        """Test that common keywords are defined (capitalized keys)."""
        # Keywords use capitalized names
        common_keywords = ["Pierce", "Impact", "Sharpshooter", "Deflect", "Cover"]
        
        for keyword in common_keywords:
            self.assertIn(keyword, LegionRules.KEYWORDS, 
                         f"Common keyword '{keyword}' should be in KEYWORDS")
            
    def test_keyword_structure(self):
        """Test that keywords have required fields."""
        for keyword_name, keyword_data in LegionRules.KEYWORDS.items():
            self.assertIn("german", keyword_data, 
                         f"Keyword '{keyword_name}' should have 'german' field")
            self.assertIn("effect", keyword_data, 
                         f"Keyword '{keyword_name}' should have 'effect' field")
            self.assertIn("timing", keyword_data, 
                         f"Keyword '{keyword_name}' should have 'timing' field")
            
    def test_get_keyword_method(self):
        """Test the get_keyword helper method."""
        # get_keyword needs capitalized name or German name
        pierce = LegionRules.get_keyword("Pierce")
        self.assertIsNotNone(pierce)
        self.assertEqual(pierce["german"], "Durchschlagen")
        
    def test_get_keyword_nonexistent(self):
        """Test get_keyword returns None for non-existent keywords."""
        result = LegionRules.get_keyword("nonexistent_keyword_xyz")
        self.assertIsNone(result)
        
    def test_search_keyword(self):
        """Test keyword search functionality."""
        results = LegionRules.search_keyword("Durchschlag")
        self.assertGreater(len(results), 0)


class TestLegionRulesTerrain(unittest.TestCase):
    """Tests for terrain types."""
    
    def test_terrain_exists(self):
        """Test that TERRAIN dictionary exists."""
        self.assertTrue(hasattr(LegionRules, 'TERRAIN'))
        
    def test_terrain_types(self):
        """Test that common terrain types are defined."""
        # Actual terrain types in LegionRules
        terrain_types = ["open", "difficult", "impassable"]
        
        for terrain in terrain_types:
            self.assertIn(terrain, LegionRules.TERRAIN,
                         f"Terrain type '{terrain}' should be defined")
            
    def test_sarlacc_pit_terrain(self):
        """Test sarlacc_pit dangerous terrain definition."""
        self.assertIn("sarlacc_pit", LegionRules.TERRAIN)
        sarlacc = LegionRules.TERRAIN["sarlacc_pit"]
        # Has special field instead of effect
        self.assertIn("special", sarlacc)
        
    def test_get_terrain_type(self):
        """Test get_terrain_type helper method."""
        difficult = LegionRules.get_terrain_type("difficult")
        self.assertIsNotNone(difficult)


class TestLegionRulesArmyBuilding(unittest.TestCase):
    """Tests for army building rules."""
    
    def test_army_building_exists(self):
        """Test that ARMY_BUILDING dictionary exists."""
        self.assertTrue(hasattr(LegionRules, 'ARMY_BUILDING'))
        
    def test_game_modes(self):
        """Test that different game modes are defined."""
        # Actual game mode keys in LegionRules
        modes = ["skirmish", "standard", "grand_army"]
        
        for mode in modes:
            self.assertIn(mode, LegionRules.ARMY_BUILDING,
                         f"Game mode '{mode}' should be defined")
            
    def test_army_building_structure(self):
        """Test army building rules have required fields."""
        for mode_name, mode_data in LegionRules.ARMY_BUILDING.items():
            self.assertIn("points", mode_data,
                         f"Mode '{mode_name}' should have 'points' field")
            # Have rank limits (commander, operative, corps, etc) not activations
            self.assertIn("commander", mode_data,
                         f"Mode '{mode_name}' should have 'commander' field")
            
    def test_get_army_requirements(self):
        """Test get_army_requirements helper method."""
        standard = LegionRules.get_army_requirements("standard")
        self.assertIsNotNone(standard)
        self.assertEqual(standard["points"], 800)


class TestLegionRulesDice(unittest.TestCase):
    """Tests for dice face definitions."""
    
    def test_dice_faces_exist(self):
        """Test that DICE_FACES dictionary exists."""
        self.assertTrue(hasattr(LegionRules, 'DICE_FACES'))
        
    def test_attack_dice_colors(self):
        """Test that attack dice colors are defined."""
        # Actual keys are red_attack, black_attack, white_attack
        self.assertIn("red_attack", LegionRules.DICE_FACES)
        self.assertIn("black_attack", LegionRules.DICE_FACES)
        self.assertIn("white_attack", LegionRules.DICE_FACES)
        
    def test_defense_dice_colors(self):
        """Test that defense dice colors are defined."""
        # Actual keys are red_defense, white_defense
        self.assertIn("red_defense", LegionRules.DICE_FACES)
        self.assertIn("white_defense", LegionRules.DICE_FACES)
        
    def test_dice_faces_have_faces(self):
        """Test that dice have faces information."""
        red_attack = LegionRules.DICE_FACES["red_attack"]
        self.assertIn("faces", red_attack)
        
        # Should have 8 faces for attack dice
        self.assertEqual(len(red_attack["faces"]), 8)


class TestLegionRulesBattleCards(unittest.TestCase):
    """Tests for battle card definitions."""
    
    def test_battle_cards_exist(self):
        """Test that BATTLE_CARDS dictionary exists."""
        self.assertTrue(hasattr(LegionRules, 'BATTLE_CARDS'))
        
    def test_battle_card_categories(self):
        """Test that battle card categories are defined."""
        categories = ["objectives", "deployments", "conditions"]
        
        for category in categories:
            self.assertIn(category, LegionRules.BATTLE_CARDS,
                         f"Battle card category '{category}' should be defined")
            
    def test_objectives_not_empty(self):
        """Test that objectives list is not empty."""
        objectives = LegionRules.BATTLE_CARDS.get("objectives", [])
        self.assertGreater(len(objectives), 0)


class TestLegionRulesConditions(unittest.TestCase):
    """Tests for unit conditions."""
    
    def test_conditions_exist(self):
        """Test that CONDITIONS dictionary exists."""
        self.assertTrue(hasattr(LegionRules, 'CONDITIONS'))
        
    def test_common_conditions(self):
        """Test that common conditions are defined."""
        # Actual condition keys are suppressed, panic (not panicked)
        conditions = ["suppressed", "panic", "poisoned", "immobilized"]
        
        for condition in conditions:
            self.assertIn(condition, LegionRules.CONDITIONS,
                         f"Condition '{condition}' should be defined")
            
    def test_get_condition(self):
        """Test get_condition helper method."""
        suppressed = LegionRules.get_condition("suppressed")
        self.assertIsNotNone(suppressed)


class TestLegionRulesCover(unittest.TestCase):
    """Tests for cover rules."""
    
    def test_cover_exists(self):
        """Test that COVER dictionary exists."""
        self.assertTrue(hasattr(LegionRules, 'COVER'))
        
    def test_cover_levels(self):
        """Test that cover levels are defined."""
        levels = ["none", "light", "heavy"]
        
        for level in levels:
            self.assertIn(level, LegionRules.COVER,
                         f"Cover level '{level}' should be defined")
            
    def test_cover_values(self):
        """Test that cover levels have correct values."""
        self.assertEqual(LegionRules.COVER["none"]["value"], 0)
        self.assertEqual(LegionRules.COVER["light"]["value"], 1)
        self.assertEqual(LegionRules.COVER["heavy"]["value"], 2)


if __name__ == '__main__':
    unittest.main()
