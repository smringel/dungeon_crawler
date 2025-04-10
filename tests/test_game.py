import unittest
import sys
import os
import pygame
import random
from unittest.mock import MagicMock, patch

# Add the parent directory to the path so we can import the dungeon_crawler package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dungeon_crawler.game import Game
from dungeon_crawler.map import Map

# Initialize pygame for testing
pygame.init()

class TestGame(unittest.TestCase):
    def setUp(self):
        # Set a fixed seed for reproducible tests
        random.seed(42)
        
        # Create a mock for pygame.display.set_mode to avoid creating a window
        with patch('pygame.display.set_mode', return_value=pygame.Surface((800, 600))):
            self.game = Game()
    
    def tearDown(self):
        # Clean up resources
        self.game = None
    
    def test_initialization(self):
        """Test that the game initializes correctly"""
        self.assertEqual(self.game.width, 800)
        self.assertEqual(self.game.height, 600)
        self.assertEqual(self.game.fps, 60)
        self.assertTrue(self.game.running)
        self.assertFalse(self.game.game_won)
        self.assertEqual(self.game.coins_collected, 0)
        self.assertEqual(self.game.total_coins, 5)
        
        # Check that the map was created
        self.assertIsInstance(self.game.map, Map)
        
        # Check that the player was created
        self.assertIsNotNone(self.game.player)
        
        # Check that the UI manager was created
        self.assertIsNotNone(self.game.ui_manager)
    
    def test_reset_game(self):
        """Test that the game resets correctly"""
        # Set up initial state
        self.game.coins_collected = 3
        self.game.game_won = True
        
        # Mock the map and player to verify they're reset
        self.game.map.generate_random_map = MagicMock()
        self.game.player.reset_position = MagicMock()
        
        # Reset the game
        self.game.reset_game()
        
        # Check that the game state was reset
        self.assertEqual(self.game.coins_collected, 0)
        self.assertFalse(self.game.game_won)
        
        # Verify that the map and player were reset
        self.game.map.generate_random_map.assert_called_once()
        self.game.player.reset_position.assert_called_once()
    
    def test_handle_events_quit(self):
        """Test that the game handles quit events"""
        # Create a mock event queue with a QUIT event
        quit_event = pygame.event.Event(pygame.QUIT)
        
        # Mock pygame.event.get to return our quit event
        with patch('pygame.event.get', return_value=[quit_event]):
            self.game.handle_events()
        
        # Check that the game is no longer running
        self.assertFalse(self.game.running)
    
    def test_handle_events_reset(self):
        """Test that the game handles reset events"""
        # Create a mock event queue with a KEYDOWN event for R key
        reset_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_r)
        
        # Mock the reset_game method
        self.game.reset_game = MagicMock()
        
        # Mock pygame.event.get to return our reset event
        with patch('pygame.event.get', return_value=[reset_event]):
            self.game.handle_events()
        
        # Verify that reset_game was called
        self.game.reset_game.assert_called_once()
    
    def test_handle_events_game_won(self):
        """Test that player movement is not handled when game is won"""
        # Set game_won to True
        self.game.game_won = True
        
        # Mock the player's handle_movement method
        self.game.player.handle_movement = MagicMock()
        
        # Handle events
        with patch('pygame.event.get', return_value=[]):
            self.game.handle_events()
        
        # Verify that handle_movement was not called
        self.game.player.handle_movement.assert_not_called()
    
    def test_handle_events_normal(self):
        """Test that player movement is handled during normal gameplay"""
        # Set game_won to False
        self.game.game_won = False
        
        # Mock the player's handle_movement method
        self.game.player.handle_movement = MagicMock()
        
        # Handle events
        with patch('pygame.event.get', return_value=[]):
            self.game.handle_events()
        
        # Verify that handle_movement was called
        self.game.player.handle_movement.assert_called_once()
    
    def test_render(self):
        """Test that the game renders correctly"""
        # Create a new mock screen instead of trying to mock the fill method
        original_screen = self.game.screen
        mock_screen = MagicMock()
        self.game.screen = mock_screen
        
        try:
            # Mock the map, player, and UI manager render methods
            self.game.map.render = MagicMock()
            self.game.player.render = MagicMock()
            self.game.ui_manager.render = MagicMock()
            
            # Render the game
            self.game.render()
            
            # Verify that fill and render methods were called
            mock_screen.fill.assert_called_once_with(self.game.BLACK)
            self.game.map.render.assert_called_once_with(mock_screen)
            self.game.player.render.assert_called_once_with(mock_screen)
            self.game.ui_manager.render.assert_called_once_with(mock_screen)
        finally:
            # Restore the original screen
            self.game.screen = original_screen

if __name__ == '__main__':
    unittest.main()
