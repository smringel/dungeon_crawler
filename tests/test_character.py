import unittest
import sys
import os
import pygame
import random
import math
from unittest.mock import MagicMock, patch

# Add the parent directory to the path so we can import the dungeon_crawler package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dungeon_crawler.characters.character import Character

# Initialize pygame for testing
pygame.init()

class TestCharacter(unittest.TestCase):
    def setUp(self):
        # Set a fixed seed for reproducible tests
        random.seed(42)
        
        # Create a mock game object
        self.mock_game = MagicMock()
        self.mock_game.width = 800
        self.mock_game.height = 600
        self.mock_game.map.is_wall.return_value = False  # Default to no walls
        
        # Create a character with the mock game
        self.character = Character(
            game=self.mock_game,
            size=15,
            speed=4,
            color=(255, 255, 255)  # White
        )
    
    def tearDown(self):
        # Clean up resources
        self.character = None
        self.mock_game = None
    
    def test_initialization(self):
        """Test that the character initializes correctly"""
        self.assertEqual(self.character.size, 15)
        self.assertEqual(self.character.speed, 4)
        self.assertEqual(self.character.color, (255, 255, 255))  # White
        self.assertEqual(self.character.last_direction, [0, 0])
        
        # Check that the character position is valid
        self.assertIsInstance(self.character.pos, list)
        self.assertEqual(len(self.character.pos), 2)
    
    def test_reset_position(self):
        """Test that the character position resets correctly"""
        # Set an initial position
        initial_pos = self.character.pos.copy()
        self.character.pos = [100, 100]
        self.character.last_direction = [1, 0]
        
        # Mock _find_valid_start_position to return a known position
        self.character._find_valid_start_position = MagicMock(return_value=[200, 200])
        
        # Reset the position
        self.character.reset_position()
        
        # Check that the position was reset
        self.assertEqual(self.character.pos, [200, 200])
        self.assertEqual(self.character.last_direction, [0, 0])
        
        # Verify that _find_valid_start_position was called
        self.character._find_valid_start_position.assert_called_once()
    
    def test_find_valid_start_position(self):
        """Test that a valid start position is found"""
        # Call the method
        pos = self.character._find_valid_start_position()
        
        # Check that the position is valid
        self.assertIsInstance(pos, list)
        self.assertEqual(len(pos), 2)
        
        # Verify that is_wall was called to check the position
        self.mock_game.map.is_wall.assert_called()
    
    def test_find_valid_start_position_with_walls(self):
        """Test finding a valid start position when there are walls"""
        # Make all positions walls except for one specific position
        def is_wall_side_effect(x, y):
            return not (x == 300 and y == 300)
        
        self.mock_game.map.is_wall.side_effect = is_wall_side_effect
        
        # Call the method
        pos = self.character._find_valid_start_position()
        
        # Since we've mocked is_wall to only return False for (300, 300),
        # the method should eventually find this position
        self.assertEqual(pos, [300, 300])
    
    def test_move_off_portal(self):
        """Test that the character moves off a portal correctly"""
        # Set an initial position
        self.character.pos = [100, 100]
        self.character.last_direction = [1, 0]
        
        # Set up the mock map
        self.mock_game.map.get_safe_distance_from_portal.return_value = 20
        
        # Call the method
        self.character._move_off_portal()
        
        # Check that the position was updated correctly
        # Since last_direction is [1, 0], the character should move right by the safe distance
        self.assertEqual(self.character.pos, [120, 100])
    
    def test_move_off_portal_with_distance_multiplier(self):
        """Test moving off a portal with a custom distance multiplier"""
        # Set an initial position
        self.character.pos = [100, 100]
        self.character.last_direction = [1, 0]
        
        # Set up the mock map
        self.mock_game.map.get_safe_distance_from_portal.return_value = 10
        
        # Call the method with a multiplier of 2.0
        self.character._move_off_portal(distance_multiplier=2.0)
        
        # Check that the position was updated correctly with the multiplier
        # Safe distance is 10, multiplier is 2.0, so character should move right by 20
        self.assertEqual(self.character.pos, [120, 100])
    
    def test_move_off_portal_wall_collision(self):
        """Test that the character tries alternative directions when moving off a portal with wall collision"""
        # Set an initial position
        self.character.pos = [100, 100]
        self.character.last_direction = [1, 0]
        
        # Set up the mock map to return True for is_wall in the preferred direction
        # but False for other directions
        def is_wall_side_effect(x, y):
            # Return True (wall) if moving right, False otherwise
            return x > 100
        
        self.mock_game.map.is_wall.side_effect = is_wall_side_effect
        self.mock_game.map.get_safe_distance_from_portal.return_value = 20
        
        # Mock random.shuffle to ensure predictable direction order
        original_shuffle = random.shuffle
        random.shuffle = lambda x: x  # Do nothing, preserve order
        
        try:
            # Call the method
            self.character._move_off_portal()
            
            # Since moving right hits a wall, the character should try other directions
            # The first alternative direction in the list is (0, -1) which is up
            self.assertEqual(self.character.pos[0], 100)  # X unchanged
            self.assertNotEqual(self.character.pos[1], 100)  # Y changed
        finally:
            # Restore original shuffle function
            random.shuffle = original_shuffle
    
    def test_move_off_portal_all_directions_blocked(self):
        """Test behavior when all directions are blocked by walls"""
        # Set an initial position
        self.character.pos = [100, 100]
        self.character.last_direction = [1, 0]
        
        # Set up the mock map to return True for is_wall in all directions
        self.mock_game.map.is_wall.return_value = True
        self.mock_game.map.get_safe_distance_from_portal.return_value = 20
        
        # Call the method
        self.character._move_off_portal()
        
        # Since all directions are blocked, the character should stay in place
        self.assertEqual(self.character.pos, [100, 100])
    
    def test_render(self):
        """Test that the character renders correctly"""
        # Set a position
        self.character.pos = [100, 100]
        
        # Create a mock screen
        mock_screen = MagicMock()
        
        # Mock pygame.draw.circle
        with patch('pygame.draw.circle') as mock_draw_circle:
            self.character.render(mock_screen)
            
            # Verify that pygame.draw.circle was called with the correct arguments
            mock_draw_circle.assert_called_once_with(
                mock_screen,
                self.character.color,
                (int(self.character.pos[0]), int(self.character.pos[1])),
                self.character.size
            )

if __name__ == '__main__':
    unittest.main()
