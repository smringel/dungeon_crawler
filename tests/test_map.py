import unittest
import sys
import os
import pygame
import random

# Add the parent directory to the path so we can import the dungeon_crawler package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dungeon_crawler.map import Map

# Initialize pygame for testing
pygame.init()

class TestMap(unittest.TestCase):
    def setUp(self):
        # Set a fixed seed for reproducible tests
        random.seed(42)
        # Create a test map with fixed dimensions
        self.map = Map(800, 600)
    
    def tearDown(self):
        # Clean up resources
        self.map = None
    
    def test_initialization(self):
        """Test that the map initializes correctly"""
        self.assertEqual(self.map.width, 800)
        self.assertEqual(self.map.height, 600)
        self.assertEqual(self.map.tile_size, 40)
        self.assertEqual(len(self.map.layout), self.map.grid_height)
        self.assertEqual(len(self.map.layout[0]), self.map.grid_width)
    
    def test_portal_generation(self):
        """Test that portals are generated correctly"""
        # Check that we have at least one portal pair
        self.assertGreaterEqual(len(self.map.portal_manager.portals), 2)
        
        # Check that we have an even number of portals
        self.assertEqual(len(self.map.portal_manager.portals) % 2, 0)
        
        # Check that each portal has a paired portal
        for portal in self.map.portal_manager.portals:
            paired_portal = self.map.portal_manager.portal_pairs.get(portal)
            self.assertIsNotNone(paired_portal)
            self.assertIn(paired_portal, self.map.portal_manager.portals)
            
            # Check that the paired portal points back to this portal
            self.assertEqual(self.map.portal_manager.portal_pairs.get(paired_portal), portal)
            
            # Check that both portals have the same color
            self.assertEqual(
                self.map.portal_manager.portal_colors_map.get(portal),
                self.map.portal_manager.portal_colors_map.get(paired_portal)
            )
    
    def test_coin_generation(self):
        """Test that coins are generated correctly"""
        # Check that we have the correct number of coins
        self.assertEqual(len(self.map.coin_manager.coins), self.map.coin_manager.total_coins)
        
        # Check that coins don't overlap with portals
        for coin_x, coin_y in self.map.coin_manager.coins:
            # Check minimum distance from any portal
            for portal_x, portal_y in self.map.portal_manager.portals:
                distance = ((coin_x - portal_x) ** 2 + (coin_y - portal_y) ** 2) ** 0.5
                min_distance = self.map.portal_manager.portal_radius + self.map.coin_manager.coin_radius + 5
                self.assertGreaterEqual(distance, min_distance)
    
    def test_is_wall(self):
        """Test the is_wall method"""
        # Test out of bounds (should be a wall)
        self.assertTrue(self.map.is_wall(-10, -10))
        self.assertTrue(self.map.is_wall(1000, 1000))
        
        # Find a wall and a floor tile for testing
        wall_found = False
        floor_found = False
        wall_pos = None
        floor_pos = None
        
        for y in range(len(self.map.layout)):
            for x in range(len(self.map.layout[0])):
                if self.map.layout[y][x] == 1 and not wall_found:
                    wall_pos = (x * self.map.tile_size + self.map.tile_size // 2, 
                               y * self.map.tile_size + self.map.tile_size // 2)
                    wall_found = True
                elif self.map.layout[y][x] == 0 and not floor_found:
                    floor_pos = (x * self.map.tile_size + self.map.tile_size // 2, 
                                y * self.map.tile_size + self.map.tile_size // 2)
                    floor_found = True
                
                if wall_found and floor_found:
                    break
            if wall_found and floor_found:
                break
        
        # Test a wall position
        if wall_pos:
            self.assertTrue(self.map.is_wall(wall_pos[0], wall_pos[1]))
        
        # Test a floor position
        if floor_pos:
            self.assertFalse(self.map.is_wall(floor_pos[0], floor_pos[1]))
    
    def test_is_portal(self):
        """Test the is_portal method"""
        # Test a non-portal position
        self.assertIsNone(self.map.is_portal(-10, -10))
        
        # Test an actual portal position
        if self.map.portal_manager.portals:
            portal_x, portal_y = self.map.portal_manager.portals[0]
            paired_portal = self.map.portal_manager.portal_pairs[(portal_x, portal_y)]
            result = self.map.is_portal(portal_x, portal_y)
            self.assertEqual(result, paired_portal)
    
    def test_is_coin(self):
        """Test the is_coin method"""
        # Test a non-coin position
        self.assertIsNone(self.map.is_coin(-10, -10))
        
        # Test an actual coin position
        if self.map.coin_manager.coins:
            coin_x, coin_y = self.map.coin_manager.coins[0]
            result = self.map.is_coin(coin_x, coin_y)
            self.assertEqual(result, (coin_x, coin_y))
    
    def test_collect_coin(self):
        """Test the collect_coin method"""
        # Test collecting a non-existent coin
        self.assertFalse(self.map.collect_coin((-10, -10)))
        
        # Test collecting an actual coin
        if self.map.coin_manager.coins:
            coin_pos = self.map.coin_manager.coins[0]
            initial_count = len(self.map.coin_manager.coins)
            result = self.map.collect_coin(coin_pos)
            self.assertTrue(result)
            self.assertEqual(len(self.map.coin_manager.coins), initial_count - 1)
            self.assertNotIn(coin_pos, self.map.coin_manager.coins)
    
    def test_multiple_regions(self):
        """Test that the map has multiple disconnected regions"""
        regions = self.map._find_disconnected_regions()
        self.assertGreaterEqual(len(regions), 2)

if __name__ == '__main__':
    unittest.main()
