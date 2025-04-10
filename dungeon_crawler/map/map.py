"""Main Map class for Dungeon Crawler"""

import pygame
import random
from collections import deque

from dungeon_crawler.map.generation import MapGenerator
from dungeon_crawler.map.portals import PortalManager
from dungeon_crawler.map.coins import CoinManager

class Map:
    """Map class that handles the dungeon layout and rendering"""
    
    def __init__(self, width, height):
        """Initialize the map
        
        Args:
            width: Screen width
            height: Screen height
        """
        self.width = width
        self.height = height
        self.tile_size = 40
        self.wall_color = (100, 100, 100)  # Gray
        self.floor_color = (50, 50, 50)    # Dark gray
        
        # Calculate grid dimensions based on screen size and tile size
        self.grid_width = width // self.tile_size
        self.grid_height = height // self.tile_size
        
        # Initialize the layout
        self.layout = []
        
        # Create managers for different aspects of the map
        self.portal_manager = PortalManager(self)
        self.coin_manager = CoinManager(self)
        self.generator = MapGenerator(self)
        
        # Generate a random map
        self.generate_random_map()
    
    def generate_random_map(self):
        """Generate a random dungeon map using cellular automata"""
        # Clear existing portals and coins
        self.portal_manager.clear()
        self.coin_manager.clear()
        
        # Generate the base layout
        self.generator.generate_layout()
        
        # Add portals between disconnected regions
        self.portal_manager.add_portals_between_regions()
        
        # Add coins to the map
        self.coin_manager.add_coins()
    
    def is_wall(self, x, y):
        """Check if the given position is a wall
        
        Args:
            x: X position in pixels
            y: Y position in pixels
            
        Returns:
            bool: True if position is a wall, False otherwise
        """
        # Convert pixel coordinates to tile coordinates
        tile_x = int(x // self.tile_size)
        tile_y = int(y // self.tile_size)
        
        # Check bounds
        if tile_y < 0 or tile_y >= len(self.layout) or tile_x < 0 or tile_x >= len(self.layout[0]):
            return True  # Out of bounds is considered a wall
        
        return self.layout[tile_y][tile_x] == 1
    
    def is_portal(self, x, y):
        """Check if the given position contains a portal
        
        Args:
            x: X position in pixels
            y: Y position in pixels
            
        Returns:
            tuple or None: The destination portal coordinates if a portal exists, None otherwise
        """
        return self.portal_manager.is_portal(x, y)
    
    def is_coin(self, x, y):
        """Check if the given position contains a coin
        
        Args:
            x: X position in pixels
            y: Y position in pixels
            
        Returns:
            tuple or None: The coin coordinates if a coin exists, None otherwise
        """
        return self.coin_manager.is_coin(x, y)
    
    def collect_coin(self, coin_pos):
        """Remove a coin from the map
        
        Args:
            coin_pos: (x, y) position of the coin to remove
            
        Returns:
            bool: True if the coin was removed, False otherwise
        """
        return self.coin_manager.collect_coin(coin_pos)
    
    def get_safe_distance_from_portal(self):
        """Get a safe distance to move away from a portal to avoid re-triggering
        
        Returns:
            int: Safe distance in pixels to move away from a portal
        """
        return self.portal_manager.get_safe_distance()
    
    def _find_disconnected_regions(self):
        """Find all disconnected regions in the map
        
        Returns:
            list: List of sets, where each set contains (x, y) coordinates of tiles in a region
        """
        # Create a grid to track visited cells
        visited = [[False for _ in range(len(self.layout[0]))] for _ in range(len(self.layout))]
        regions = []
        
        # Find all regions
        for y in range(len(self.layout)):
            for x in range(len(self.layout[0])):
                # If this is a floor tile and we haven't visited it yet
                if self.layout[y][x] == 0 and not visited[y][x]:
                    # Do a BFS to find all connected floor tiles
                    region = set()
                    queue = deque([(x, y)])
                    visited[y][x] = True
                    
                    while queue:
                        cx, cy = queue.popleft()
                        region.add((cx, cy))
                        
                        # Check all adjacent tiles
                        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                            nx, ny = cx + dx, cy + dy
                            if 0 <= nx < len(self.layout[0]) and 0 <= ny < len(self.layout):
                                if self.layout[ny][nx] == 0 and not visited[ny][nx]:
                                    visited[ny][nx] = True
                                    queue.append((nx, ny))
                    
                    # Add this region to our list
                    if region:
                        regions.append(region)
        
        return regions
    
    def render(self, screen):
        """Render the map
        
        Args:
            screen: Pygame screen to render on
        """
        # Draw the base map (walls and floors)
        for y in range(len(self.layout)):
            for x in range(len(self.layout[y])):
                rect = pygame.Rect(
                    x * self.tile_size,
                    y * self.tile_size,
                    self.tile_size,
                    self.tile_size
                )
                
                if self.layout[y][x] == 1:
                    pygame.draw.rect(screen, self.wall_color, rect)
                else:
                    pygame.draw.rect(screen, self.floor_color, rect)
        
        # Draw portals
        self.portal_manager.render(screen)
        
        # Draw coins
        self.coin_manager.render(screen)
