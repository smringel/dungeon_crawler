"""Coin functionality for Dungeon Crawler"""

import pygame
import random
import math

class CoinManager:
    """Handles the creation and management of coins"""
    
    def __init__(self, map_instance):
        """Initialize the coin manager
        
        Args:
            map_instance: The Map instance this manager belongs to
        """
        self.map = map_instance
        
        # Coin data
        self.coins = []  # List of (x, y) coin positions
        self.coin_radius = self.map.tile_size // 4  # Radius for coin detection
        self.total_coins = 5  # Total number of coins to collect
        self.coin_color = (255, 215, 0)  # Gold
    
    def clear(self):
        """Clear all coin data"""
        self.coins = []
    
    def add_coins(self):
        """Add coins to the map in valid floor positions that don't overlap with portals"""
        # Find all disconnected regions
        regions = self.map._find_disconnected_regions()
        
        # If there are no regions, return
        if not regions:
            return
            
        # Sort regions by size (largest first)
        regions.sort(key=len, reverse=True)
        
        # Calculate safe distance from portals (portal radius + coin radius + small buffer)
        safe_distance = self.map.portal_manager.portal_radius + self.coin_radius + 5
        
        # Distribute coins across regions
        coins_added = 0
        region_index = 0
        
        while coins_added < self.total_coins and region_index < len(regions):
            region = regions[region_index]
            
            # Convert region to list for random selection
            region_tiles = list(region)
            random.shuffle(region_tiles)  # Shuffle to avoid bias
            
            # Determine how many coins to place in this region
            coins_for_region = min(
                max(1, len(region) // 20),  # At least 1 coin, more for larger regions
                self.total_coins - coins_added  # Don't exceed total coins
            )
            
            # Try to place coins in this region
            attempts = 0
            max_attempts = len(region_tiles)  # Don't try more times than we have tiles
            
            while coins_added < self.total_coins and coins_for_region > 0 and attempts < max_attempts:
                if not region_tiles:
                    break
                    
                # Pick a tile from the region
                tile_x, tile_y = region_tiles.pop(0)  # Take from the front since we shuffled
                attempts += 1
                
                # Skip wall tiles - ensure coins are only placed on floor tiles
                if self.map.layout[tile_y][tile_x] == 1:  # 1 represents a wall
                    continue
                
                # Convert to pixel coordinates (center of tile)
                coin_x = tile_x * self.map.tile_size + self.map.tile_size // 2
                coin_y = tile_y * self.map.tile_size + self.map.tile_size // 2
                
                # Check if this position is too close to any portal
                too_close_to_portal = False
                for portal_x, portal_y in self.map.portal_manager.portals:
                    distance = ((coin_x - portal_x) ** 2 + (coin_y - portal_y) ** 2) ** 0.5
                    if distance < safe_distance:
                        too_close_to_portal = True
                        break
                
                # Also check if too close to other coins
                too_close_to_coin = False
                for existing_coin_x, existing_coin_y in self.coins:
                    distance = ((coin_x - existing_coin_x) ** 2 + (coin_y - existing_coin_y) ** 2) ** 0.5
                    if distance < self.coin_radius * 4:  # Increase separation between coins
                        too_close_to_coin = True
                        break
                
                # If position is valid, add the coin
                if not too_close_to_portal and not too_close_to_coin:
                    self.coins.append((coin_x, coin_y))
                    coins_added += 1
                    coins_for_region -= 1
            
            region_index += 1
        
        # If we still need more coins, try again with relaxed constraints
        if coins_added < self.total_coins:
            # Combine all regions into one pool of tiles
            all_tiles = []
            for region in regions:
                all_tiles.extend(list(region))
            
            random.shuffle(all_tiles)
            
            # Try to place remaining coins with only checking portal overlap
            while coins_added < self.total_coins and all_tiles:
                tile_x, tile_y = all_tiles.pop(0)
                
                # Skip wall tiles - ensure coins are only placed on floor tiles
                if self.map.layout[tile_y][tile_x] == 1:  # 1 represents a wall
                    continue
                    
                # Convert to pixel coordinates (center of tile)
                coin_x = tile_x * self.map.tile_size + self.map.tile_size // 2
                coin_y = tile_y * self.map.tile_size + self.map.tile_size // 2
                
                # Check if this position is too close to any portal
                too_close_to_portal = False
                for portal_x, portal_y in self.map.portal_manager.portals:
                    distance = ((coin_x - portal_x) ** 2 + (coin_y - portal_y) ** 2) ** 0.5
                    if distance < safe_distance:
                        too_close_to_portal = True
                        break
                        
                # Also check if too close to other coins (even in fallback mode)
                too_close_to_coin = False
                for existing_coin_x, existing_coin_y in self.coins:
                    distance = ((coin_x - existing_coin_x) ** 2 + (coin_y - existing_coin_y) ** 2) ** 0.5
                    if distance < self.coin_radius * 4:  # Same separation as above
                        too_close_to_coin = True
                        break
                
                # If position is valid, add the coin
                if not too_close_to_portal and not too_close_to_coin:
                    self.coins.append((coin_x, coin_y))
                    coins_added += 1
                    
        # Final fallback: If we still don't have enough coins, place them anywhere valid
        if coins_added < self.total_coins:
            print(f"Warning: Only placed {coins_added}/{self.total_coins} coins with normal constraints. Using emergency placement.")
            
            # Create a list of all floor tiles
            all_floor_tiles = []
            for y in range(len(self.map.layout)):
                for x in range(len(self.map.layout[0])):
                    # Only consider floor tiles (not walls)
                    if self.map.layout[y][x] == 0:
                        all_floor_tiles.append((x, y))
            
            # Shuffle to avoid bias
            random.shuffle(all_floor_tiles)
            
            # Place remaining coins with minimal constraints
            while coins_added < self.total_coins and all_floor_tiles:
                tile_x, tile_y = all_floor_tiles.pop(0)
                
                # Convert to pixel coordinates (center of tile)
                coin_x = tile_x * self.map.tile_size + self.map.tile_size // 2
                coin_y = tile_y * self.map.tile_size + self.map.tile_size // 2
                
                # Only check if directly on top of another coin
                too_close_to_coin = False
                for existing_coin_x, existing_coin_y in self.coins:
                    distance = ((coin_x - existing_coin_x) ** 2 + (coin_y - existing_coin_y) ** 2) ** 0.5
                    if distance < self.coin_radius * 2:  # Minimal separation
                        too_close_to_coin = True
                        break
                
                # If position is valid, add the coin
                if not too_close_to_coin:
                    self.coins.append((coin_x, coin_y))
                    coins_added += 1
    
    def is_coin(self, x, y):
        """Check if the given position contains a coin
        
        Args:
            x: X position in pixels
            y: Y position in pixels
            
        Returns:
            tuple or None: The coin coordinates if a coin exists, None otherwise
        """
        # Check if the position is near any coin
        for coin_x, coin_y in self.coins:
            # Use a distance check to see if player is on the coin
            distance = ((x - coin_x) ** 2 + (y - coin_y) ** 2) ** 0.5
            if distance < self.coin_radius:
                return (coin_x, coin_y)
        return None
    
    def collect_coin(self, coin_pos):
        """Remove a coin from the map
        
        Args:
            coin_pos: (x, y) position of the coin to remove
            
        Returns:
            bool: True if the coin was removed, False otherwise
        """
        if coin_pos in self.coins:
            self.coins.remove(coin_pos)
            return True
        return False
    
    def render(self, screen):
        """Render all coins
        
        Args:
            screen: Pygame screen to render on
        """
        # Draw coins
        for coin_x, coin_y in self.coins:
            # Draw coin as a circle
            pygame.draw.circle(
                screen,
                self.coin_color,
                (int(coin_x), int(coin_y)),
                self.coin_radius
            )
            
            # Draw a spinning effect (inner highlight)
            spin = (pygame.time.get_ticks() % 1000) / 1000.0  # Value between 0 and 1
            # Calculate position of the inner highlight
            highlight_radius = self.coin_radius * 0.6
            highlight_offset_x = math.cos(spin * 2 * math.pi) * (self.coin_radius * 0.3)
            highlight_offset_y = math.sin(spin * 2 * math.pi) * (self.coin_radius * 0.3)
            
            # Draw the highlight
            pygame.draw.circle(
                screen,
                (255, 255, 200),  # Light yellow
                (int(coin_x + highlight_offset_x), int(coin_y + highlight_offset_y)),
                int(highlight_radius * 0.5)
            )
