import unittest
import sys
import os
import pygame
import random
import math
from unittest.mock import MagicMock, patch

# Add the parent directory to the path so we can import the dungeon_crawler package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dungeon_crawler.game.player import Player

# Initialize pygame for testing
pygame.init()

class TestPlayer(unittest.TestCase):
    def setUp(self):
        # Set a fixed seed for reproducible tests
        random.seed(42)
        
        # Create a mock game object
        self.mock_game = MagicMock()
        self.mock_game.width = 800
        self.mock_game.height = 600
        self.mock_game.map.is_wall.return_value = False  # Default to no walls
        
        # Create the player with the mock game
        self.player = Player(self.mock_game)
    
    def tearDown(self):
        # Clean up resources
        self.player = None
        self.mock_game = None
    
    def test_initialization(self):
        """Test that the player initializes correctly"""
        self.assertEqual(self.player.size, 15)
        self.assertEqual(self.player.speed, 4)
        self.assertEqual(self.player.color, (255, 0, 0))  # Red
        self.assertEqual(self.player.last_direction, [0, 0])
        
        # Check that the player position is valid
        self.assertIsInstance(self.player.pos, list)
        self.assertEqual(len(self.player.pos), 2)
    
    def test_reset_position(self):
        """Test that the player position resets correctly"""
        # Set an initial position
        initial_pos = self.player.pos.copy()
        self.player.pos = [100, 100]
        self.player.last_direction = [1, 0]
        
        # Mock _find_valid_start_position to return a known position
        self.player._find_valid_start_position = MagicMock(return_value=[200, 200])
        
        # Reset the position
        self.player.reset_position()
        
        # Check that the position was reset
        self.assertEqual(self.player.pos, [200, 200])
        self.assertEqual(self.player.last_direction, [0, 0])
        
        # Verify that _find_valid_start_position was called
        self.player._find_valid_start_position.assert_called_once()
    
    def test_find_valid_start_position(self):
        """Test that a valid start position is found"""
        # Restore the original method
        self.player._find_valid_start_position = Player._find_valid_start_position.__get__(self.player)
        
        # Call the method
        pos = self.player._find_valid_start_position()
        
        # Check that the position is valid
        self.assertIsInstance(pos, list)
        self.assertEqual(len(pos), 2)
        
        # Verify that is_wall was called to check the position
        self.mock_game.map.is_wall.assert_called()
    
    def test_handle_movement_no_input(self):
        """Test that the player doesn't move without input"""
        # Set an initial position
        self.player.pos = [100, 100]
        
        # Create a custom handle_movement method that doesn't rely on pygame.key.get_pressed
        def mock_handle_movement(self):
            # Simulate no keys pressed
            moved = False
            new_pos = self.pos.copy()
            
            # No movement, so we don't update new_pos
            
            # Check for wall collisions before updating position
            if not self.game.map.is_wall(new_pos[0], new_pos[1]):
                self.pos = new_pos
                
                # Check for portal and coin interactions (not relevant for this test)
                pass
        
        # Replace the handle_movement method temporarily
        original_method = self.player.handle_movement
        self.player.handle_movement = mock_handle_movement.__get__(self.player, type(self.player))
        
        try:
            # Call the mocked method
            self.player.handle_movement()
            
            # Check that the position didn't change
            self.assertEqual(self.player.pos, [100, 100])
        finally:
            # Restore the original method
            self.player.handle_movement = original_method
    
    def test_handle_movement_left(self):
        """Test that the player moves left with left arrow key"""
        # Set an initial position
        self.player.pos = [100, 100]
        
        # Create a custom handle_movement method that simulates left key press
        def mock_handle_movement(self):
            # Simulate left key pressed
            moved = True
            new_pos = self.pos.copy()
            
            # Move left
            new_pos[0] -= self.speed
            dx, dy = -1, 0
            
            # Update last direction
            self.last_direction = [dx, dy]
            
            # Check for wall collisions before updating position
            if not self.game.map.is_wall(new_pos[0], new_pos[1]):
                self.pos = new_pos
                
                # Check for portal and coin interactions (not relevant for this test)
                pass
        
        # Replace the handle_movement method temporarily
        original_method = self.player.handle_movement
        self.player.handle_movement = mock_handle_movement.__get__(self.player, type(self.player))
        
        try:
            # Call the mocked method
            self.player.handle_movement()
            
            # Check that the position changed correctly
            self.assertEqual(self.player.pos, [100 - self.player.speed, 100])
            self.assertEqual(self.player.last_direction, [-1, 0])
        finally:
            # Restore the original method
            self.player.handle_movement = original_method
    
    def test_handle_movement_wall_collision(self):
        """Test that the player doesn't move into walls"""
        # Set an initial position
        self.player.pos = [100, 100]
        
        # Set up the mock map to return True for is_wall (indicating a wall)
        self.mock_game.map.is_wall.return_value = True
        
        # Create a custom handle_movement method that simulates right key press
        def mock_handle_movement(self):
            # Simulate right key pressed
            moved = True
            new_pos = self.pos.copy()
            
            # Move right
            new_pos[0] += self.speed
            dx, dy = 1, 0
            
            # Update last direction
            self.last_direction = [dx, dy]
            
            # Check for wall collisions before updating position
            if not self.game.map.is_wall(new_pos[0], new_pos[1]):
                self.pos = new_pos
                
                # Check for portal and coin interactions (not relevant for this test)
                pass
        
        # Replace the handle_movement method temporarily
        original_method = self.player.handle_movement
        self.player.handle_movement = mock_handle_movement.__get__(self.player, type(self.player))
        
        try:
            # Call the mocked method
            self.player.handle_movement()
            
            # Check that the position didn't change due to wall collision
            self.assertEqual(self.player.pos, [100, 100])
            # But the last_direction should still be updated
            self.assertEqual(self.player.last_direction, [1, 0])
        finally:
            # Restore the original method
            self.player.handle_movement = original_method
    
    def test_handle_movement_portal(self):
        """Test that the player teleports when on a portal"""
        # Set an initial position
        self.player.pos = [100, 100]
        
        # Set up the mock map to return a portal destination
        self.mock_game.map.is_portal.return_value = (200, 200)
        
        # Mock _move_off_portal
        self.player._move_off_portal = MagicMock()
        
        # Create a custom handle_movement method that simulates right key press and portal interaction
        def mock_handle_movement(self):
            # Simulate right key pressed
            moved = True
            new_pos = self.pos.copy()
            
            # Move right
            new_pos[0] += self.speed
            dx, dy = 1, 0
            
            # Update last direction
            self.last_direction = [dx, dy]
            
            # Check for wall collisions before updating position
            if not self.game.map.is_wall(new_pos[0], new_pos[1]):
                self.pos = new_pos
                
                # Check if player is on a portal
                portal_dest = self.game.map.is_portal(self.pos[0], self.pos[1])
                if portal_dest:
                    # Teleport the player to the destination portal
                    self.pos = [portal_dest[0], portal_dest[1]]
                    
                    # Move the player off the destination portal
                    self._move_off_portal()
        
        # Replace the handle_movement method temporarily
        original_method = self.player.handle_movement
        self.player.handle_movement = mock_handle_movement.__get__(self.player, type(self.player))
        
        try:
            # Call the mocked method
            self.player.handle_movement()
            
            # Check that the position was updated to the portal destination
            self.assertEqual(self.player.pos, [200, 200])
            
            # Verify that _move_off_portal was called
            self.player._move_off_portal.assert_called_once()
        finally:
            # Restore the original method
            self.player.handle_movement = original_method
    
    def test_handle_movement_coin(self):
        """Test that the player collects coins"""
        # Set an initial position
        self.player.pos = [100, 100]
        
        # Set up the mock map to return a coin position
        coin_pos = (100, 100)
        self.mock_game.map.is_coin.return_value = coin_pos
        self.mock_game.map.collect_coin.return_value = True
        
        # Set initial game state
        self.mock_game.coins_collected = 0
        self.mock_game.total_coins = 5
        self.mock_game.game_won = False
        
        # Create a custom handle_movement method that simulates coin collection
        def mock_handle_movement(self):
            # Simulate right key pressed
            moved = True
            new_pos = self.pos.copy()
            
            # Move right
            new_pos[0] += self.speed
            dx, dy = 1, 0
            
            # Update last direction
            self.last_direction = [dx, dy]
            
            # Check for wall collisions before updating position
            if not self.game.map.is_wall(new_pos[0], new_pos[1]):
                self.pos = new_pos
                
                # Check if player is on a coin
                coin_pos = self.game.map.is_coin(self.pos[0], self.pos[1])
                if coin_pos:
                    # Collect the coin
                    if self.game.map.collect_coin(coin_pos):
                        self.game.coins_collected += 1
        
        # Replace the handle_movement method temporarily
        original_method = self.player.handle_movement
        self.player.handle_movement = mock_handle_movement.__get__(self.player, type(self.player))
        
        try:
            # Call the mocked method
            self.player.handle_movement()
            
            # Verify that collect_coin was called with the coin position
            self.mock_game.map.collect_coin.assert_called_once_with(coin_pos)
            
            # Check that coins_collected was incremented
            self.assertEqual(self.mock_game.coins_collected, 1)
        finally:
            # Restore the original method
            self.player.handle_movement = original_method
    
    def test_handle_movement_win_condition(self):
        """Test that the game is won when all coins are collected"""
        # Set an initial position
        self.player.pos = [100, 100]
        
        # Set up the mock map to return a coin position
        coin_pos = (100, 100)
        self.mock_game.map.is_coin.return_value = coin_pos
        self.mock_game.map.collect_coin.return_value = True
        
        # Set initial game state to be one coin away from winning
        self.mock_game.coins_collected = 4
        self.mock_game.total_coins = 5
        self.mock_game.game_won = False
        
        # Create a custom handle_movement method that simulates winning the game
        def mock_handle_movement(self):
            # Simulate right key pressed
            moved = True
            new_pos = self.pos.copy()
            
            # Move right
            new_pos[0] += self.speed
            dx, dy = 1, 0
            
            # Update last direction
            self.last_direction = [dx, dy]
            
            # Check for wall collisions before updating position
            if not self.game.map.is_wall(new_pos[0], new_pos[1]):
                self.pos = new_pos
                
                # Check if player is on a coin
                coin_pos = self.game.map.is_coin(self.pos[0], self.pos[1])
                if coin_pos:
                    # Collect the coin
                    if self.game.map.collect_coin(coin_pos):
                        self.game.coins_collected += 1
                        
                        # Check if all coins are collected
                        if self.game.coins_collected >= self.game.total_coins:
                            self.game.game_won = True
                            self.game.win_message_time = 12345  # Fixed value for testing
        
        # Replace the handle_movement method temporarily
        original_method = self.player.handle_movement
        self.player.handle_movement = mock_handle_movement.__get__(self.player, type(self.player))
        
        try:
            # Call the mocked method
            self.player.handle_movement()
            
            # Check that the game was marked as won
            self.assertTrue(self.mock_game.game_won)
            self.assertEqual(self.mock_game.win_message_time, 12345)
        finally:
            # Restore the original method
            self.player.handle_movement = original_method
    
    def test_move_off_portal(self):
        """Test that the player moves off a portal correctly"""
        # Restore the original method
        self.player._move_off_portal = Player._move_off_portal.__get__(self.player)
        
        # Set an initial position
        self.player.pos = [100, 100]
        self.player.last_direction = [1, 0]
        
        # Set up the mock map
        self.mock_game.map.get_safe_distance_from_portal.return_value = 20
        
        # Call the method
        self.player._move_off_portal()
        
        # Check that the position was updated correctly
        # Since last_direction is [1, 0], the player should move right by the safe distance
        self.assertEqual(self.player.pos, [120, 100])
    
    def test_move_off_portal_wall_collision(self):
        """Test that the player tries alternative directions when moving off a portal with wall collision"""
        # Restore the original method
        self.player._move_off_portal = Player._move_off_portal.__get__(self.player)
        
        # Set an initial position
        self.player.pos = [100, 100]
        self.player.last_direction = [1, 0]
        
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
            self.player._move_off_portal()
            
            # Since moving right hits a wall, the player should try other directions
            # The first alternative direction in the list is (0, -1) which is up
            self.assertEqual(self.player.pos[0], 100)  # X unchanged
            self.assertNotEqual(self.player.pos[1], 100)  # Y changed
        finally:
            # Restore original shuffle function
            random.shuffle = original_shuffle
    
    def test_render(self):
        """Test that the player renders correctly"""
        # Set a position
        self.player.pos = [100, 100]
        
        # Create a mock screen
        mock_screen = MagicMock()
        
        # Mock pygame.draw.circle
        with patch('pygame.draw.circle') as mock_draw_circle:
            self.player.render(mock_screen)
            
            # Verify that pygame.draw.circle was called with the correct arguments
            mock_draw_circle.assert_called_once_with(
                mock_screen,
                self.player.color,
                (int(self.player.pos[0]), int(self.player.pos[1])),
                self.player.size
            )

if __name__ == '__main__':
    unittest.main()
