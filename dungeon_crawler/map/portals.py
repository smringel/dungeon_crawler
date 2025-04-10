"""Portal functionality for Dungeon Crawler"""

import pygame
import math
import random

class PortalManager:
    """Handles the creation and management of portals"""
    
    def __init__(self, map_instance):
        """Initialize the portal manager
        
        Args:
            map_instance: The Map instance this manager belongs to
        """
        self.map = map_instance
        
        # Define a list of distinct portal colors
        self.portal_colors = [
            (0, 191, 255),    # Deep Sky Blue
            (138, 43, 226),   # Blue Violet
            (255, 105, 180),  # Hot Pink
            (50, 205, 50),    # Lime Green
            (255, 165, 0),    # Orange
            (255, 0, 0),      # Red
            (0, 255, 255),    # Cyan
            (255, 255, 0)     # Yellow
        ]
        
        # Portal data
        self.portals = []  # List of (x, y) portal positions
        self.portal_pairs = {}  # Maps portal position to its paired portal
        self.portal_colors_map = {}  # Maps portal position to its color index
        self.portal_radius = self.map.tile_size // 3  # Radius for portal detection
    
    def clear(self):
        """Clear all portal data"""
        self.portals = []
        self.portal_pairs = {}
        self.portal_colors_map = {}
    
    def add_portals_between_regions(self):
        """Find disconnected regions and add portals to connect them"""
        # Clear any existing portals first
        self.clear()
        
        # Find all disconnected regions
        regions = self.map._find_disconnected_regions()
        
        # Sort regions by size (largest first)
        regions.sort(key=len, reverse=True)
        
        # If there's only one natural region, artificially create a second region by splitting the main one
        if len(regions) <= 1 and regions:
            main_region = regions[0]
            
            # Try to create an artificial region - this returns True if successful
            success = self.map.generator._create_artificial_region(main_region)
            
            # Re-find regions after modification
            if success:
                regions = self.map._find_disconnected_regions()
                regions.sort(key=len, reverse=True)
            
            # If we still have only one region, try a more aggressive approach
            if len(regions) <= 1:
                # Create a simple maze-like pattern in the center of the map
                self.map.generator._create_maze_pattern()
                
                # Re-find regions again
                regions = self.map._find_disconnected_regions()
                regions.sort(key=len, reverse=True)
        
        # If we still don't have at least 2 regions, force create a second region
        if len(regions) < 2:
            self.map.generator._force_create_second_region()
            regions = self.map._find_disconnected_regions()
            regions.sort(key=len, reverse=True)
            
            # If we STILL don't have at least 2 regions, give up and regenerate the map
            if len(regions) < 2:
                # Regenerate the layout but don't call generate_random_map to avoid infinite recursion
                self.map.generator._regenerate_layout()
                regions = self.map._find_disconnected_regions()
                regions.sort(key=len, reverse=True)
        
        # For each region (except the largest), create a portal pair connecting to the largest region
        if len(regions) >= 2:
            main_region = regions[0]
            portal_pairs_added = 0
            
            for i in range(1, len(regions)):
                region = regions[i]
                
                # Find a suitable location for a portal in this region
                portal1_pos = self._find_portal_location(region)
                
                # Find a suitable location for the paired portal in the main region
                portal2_pos = self._find_portal_location(main_region)
                
                # If we found valid positions for both portals
                if portal1_pos and portal2_pos:
                    # Convert to pixel coordinates (center of tile)
                    px1, py1 = portal1_pos[0] * self.map.tile_size + self.map.tile_size // 2, portal1_pos[1] * self.map.tile_size + self.map.tile_size // 2
                    px2, py2 = portal2_pos[0] * self.map.tile_size + self.map.tile_size // 2, portal2_pos[1] * self.map.tile_size + self.map.tile_size // 2
                    
                    # Add the portal pair
                    self.portals.append((px1, py1))
                    self.portals.append((px2, py2))
                    
                    # Create bidirectional mapping between portals
                    self.portal_pairs[(px1, py1)] = (px2, py2)
                    self.portal_pairs[(px2, py2)] = (px1, py1)
                    
                    # Assign a color to this portal pair
                    # Use the portal_pairs_added counter to ensure consistent color indexing
                    color_index = portal_pairs_added % len(self.portal_colors)
                    self.portal_colors_map[(px1, py1)] = color_index
                    self.portal_colors_map[(px2, py2)] = color_index
                    
                    portal_pairs_added += 1
            
            # Verify that all portals have a pair
            self._verify_portal_pairs()
    
    def _find_portal_location(self, region):
        """Find a suitable location for a portal in the given region"""
        # Try to find a position that has some empty space around it
        candidates = []
        
        for x, y in region:
            # Check if this position has at least 2 adjacent floor tiles
            adjacent_floors = 0
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < len(self.map.layout[0]) and 0 <= ny < len(self.map.layout):
                    if self.map.layout[ny][nx] == 0:  # Floor
                        adjacent_floors += 1
            
            if adjacent_floors >= 2:
                candidates.append((x, y))
        
        # Return a random candidate if any exist
        if candidates:
            return random.choice(candidates)
        # Fallback: return any position in the region
        elif region:
            return random.choice(list(region))
        return None
    
    def _verify_portal_pairs(self):
        """Verify that all portals have a paired portal and fix any issues"""
        # Check if we have an odd number of portals (which would indicate an unpaired portal)
        if len(self.portals) % 2 != 0:
            # Find the unpaired portal
            unpaired_portals = []
            for portal in self.portals:
                if portal not in self.portal_pairs:
                    unpaired_portals.append(portal)
            
            # Remove any unpaired portals
            for portal in unpaired_portals:
                if portal in self.portals:
                    self.portals.remove(portal)
                if portal in self.portal_colors_map:
                    del self.portal_colors_map[portal]
        
        # Verify each portal has a valid pair
        valid_portals = []
        valid_pairs = {}
        valid_colors = {}
        
        for portal in self.portals:
            paired_portal = self.portal_pairs.get(portal)
            
            # If this portal has a valid pair that exists in the portals list
            if paired_portal and paired_portal in self.portals:
                valid_portals.append(portal)
                valid_pairs[portal] = paired_portal
                
                # Ensure both portals have the same color
                if portal in self.portal_colors_map:
                    color = self.portal_colors_map[portal]
                    valid_colors[portal] = color
                    valid_colors[paired_portal] = color
        
        # Update the portal data with only valid portals and pairs
        self.portals = valid_portals
        self.portal_pairs = valid_pairs
        self.portal_colors_map = valid_colors
    
    def is_portal(self, x, y):
        """Check if the given position contains a portal
        
        Args:
            x: X position in pixels
            y: Y position in pixels
            
        Returns:
            tuple or None: The destination portal coordinates if a portal exists, None otherwise
        """
        # Check if the position is near any portal
        for portal_x, portal_y in self.portals:
            # Use a distance check to see if player is on the portal
            distance = ((x - portal_x) ** 2 + (y - portal_y) ** 2) ** 0.5
            if distance < self.portal_radius:  # Use the defined portal radius
                # Return the paired portal's position if it exists
                paired_portal = self.portal_pairs.get((portal_x, portal_y))
                if paired_portal and paired_portal in self.portals:
                    return paired_portal
        return None
    
    def get_safe_distance(self):
        """Get a safe distance to move away from a portal to avoid re-triggering
        
        Returns:
            int: Safe distance in pixels to move away from a portal
        """
        # Return a distance that's guaranteed to be outside the portal radius
        # Add a small buffer to ensure we're completely clear
        return self.portal_radius + 5
    
    def get_portal_destination(self, portal_pos):
        """Get the destination portal for a given portal position
        
        Args:
            portal_pos: (x, y) position of the portal
            
        Returns:
            tuple or None: The paired portal coordinates if it exists, None otherwise
        """
        # Check if the portal exists and has a valid pair
        if portal_pos in self.portal_pairs and self.portal_pairs[portal_pos] in self.portals:
            return self.portal_pairs[portal_pos]
        return None
    
    def render(self, screen):
        """Render all portals
        
        Args:
            screen: Pygame screen to render on
        """
        # Draw portals
        for portal_x, portal_y in self.portals:
            # Get the color for this portal
            color_index = self.portal_colors_map.get((portal_x, portal_y), 0)
            color = self.portal_colors[color_index]
            
            # Draw portal as a circle
            pygame.draw.circle(
                screen,
                color,
                (int(portal_x), int(portal_y)),
                self.portal_radius  # Slightly smaller than a tile
            )
            
            # Draw a pulsing effect (inner circle)
            pulse = (pygame.time.get_ticks() % 1000) / 1000.0  # Value between 0 and 1
            pulse_size = int(self.map.tile_size // 4 * (0.5 + 0.5 * pulse))
            pygame.draw.circle(
                screen,
                (255, 255, 255),  # White
                (int(portal_x), int(portal_y)),
                pulse_size
            )
