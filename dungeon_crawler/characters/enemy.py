"""Enemy class for Dungeon Crawler"""

import pygame
import random
import math
import time

from dungeon_crawler.characters.character import Character

class Enemy(Character):
    """Enemy character that chases the player"""
    
    def __init__(self, game, region=None):
        """Initialize the enemy
        
        Args:
            game: The Game instance this enemy belongs to
            region: The specific region this enemy should be placed in (optional)
        """
        # Set game reference first so we can access it before calling super().__init__
        self.game = game
        
        # Set detection radius before calling _find_valid_start_position via super().__init__
        self.detection_radius = game.map.portal_manager.portal_radius // 2  # Half of portal radius
        
        # Store the region this enemy belongs to
        self.region = region
        
        # Track sleep state
        self.sleep_until = time.time() + 5  # Sleep for 5 seconds
        self.is_sleeping = True
        
        # Track stun state
        self.is_stunned = False
        self.stun_until = 0
        self.last_hit_time = 0
        
        # Position history to detect and break out of loops
        self.position_history = []
        self.stuck_counter = 0
        
        # Initialize the base character with enemy-specific attributes
        super().__init__(
            game=game,
            size=15,
            speed=1,  # 1/4 the player's speed (player speed is 4)
            color=(255, 0, 0)  # Red
        )
    
    def _find_valid_start_position(self):
        """Find a valid starting position for the enemy
        
        Returns:
            list: [x, y] position in pixels
        """
        # Get all regions first
        regions = self.game.map._find_disconnected_regions()
        
        # If a specific region was provided, use it; otherwise, choose randomly
        if self.region:
            enemy_region = self.region
        else:
            # Can start in any region, including the player's region
            # Choose a random region
            # Filter regions to ensure they're large enough
            valid_regions = []
            for region in regions:
                if len(region) >= 6:  # Minimum size to ensure enough space for enemy movement
                    valid_regions.append(region)
            
            # If no valid regions, use all regions
            if not valid_regions:
                valid_regions = regions
            
            # Choose a random region
            enemy_region = random.choice(valid_regions)
        
        # Minimum safe distance from portals (3x the capture radius)
        min_portal_distance = self.detection_radius * 3
        
        # Try to find a position away from portals
        valid_positions = []
        for tile_x, tile_y in enemy_region:
            # Convert to pixel coordinates (center of tile)
            pos_x = tile_x * self.game.map.tile_size + self.game.map.tile_size // 2
            pos_y = tile_y * self.game.map.tile_size + self.game.map.tile_size // 2
            
            # Check distance from all portals
            far_enough = True
            for portal_x, portal_y in self.game.map.portal_manager.portals:
                distance = math.sqrt((pos_x - portal_x)**2 + (pos_y - portal_y)**2)
                if distance < min_portal_distance:
                    far_enough = False
                    break
            
            if far_enough:
                valid_positions.append((pos_x, pos_y))
            
        # If we found valid positions, choose one randomly
        if valid_positions:
            pos_x, pos_y = random.choice(valid_positions)
            return [pos_x, pos_y]
        
        # Fallback: choose any position in the region
        tile_x, tile_y = random.choice(list(enemy_region))
        return [
            tile_x * self.game.map.tile_size + self.game.map.tile_size // 2,
            tile_y * self.game.map.tile_size + self.game.map.tile_size // 2
        ]
        
        # Use the base class implementation as a last resort
        return super()._find_valid_start_position()
    
    def reset_position(self):
        """Reset the enemy's position to a valid starting position"""
        super().reset_position()
        self.sleep_until = time.time() + 5
        self.is_sleeping = True
    
    def update(self):
        """Update enemy state and position"""
        # Check if still sleeping
        if self.is_sleeping:
            if time.time() >= self.sleep_until:
                self.is_sleeping = False
            else:
                return  # Don't move while sleeping
        
        # Check if stunned
        current_time = pygame.time.get_ticks() / 1000.0
        if self.is_stunned:
            if current_time >= self.stun_until:
                self.is_stunned = False
            else:
                return  # Don't move while stunned
                
        # Track if we've just teleported to avoid getting stuck in portals
        just_teleported = False
        
        # Check if enemy and player are in the same region
        same_region = self._is_in_same_region_as_player()
        
        # If in different regions, try to find a portal
        if not same_region:
            # Find the nearest portal
            nearest_portal = self._find_nearest_portal()
            
            if nearest_portal:
                # Move towards the nearest portal
                dx = nearest_portal[0] - self.pos[0]
                dy = nearest_portal[1] - self.pos[1]
                
                # If very close to portal, move directly to it
                portal_distance = math.sqrt(dx*dx + dy*dy)
                if portal_distance < self.speed * 2:
                    self.pos = [nearest_portal[0], nearest_portal[1]]
                    just_teleported = True
            else:
                # No portal found, move towards player directly
                dx = self.game.player.pos[0] - self.pos[0]
                dy = self.game.player.pos[1] - self.pos[1]
        else:
            # In same region, move directly towards player
            dx = self.game.player.pos[0] - self.pos[0]
            dy = self.game.player.pos[1] - self.pos[1]
        
        # Only proceed with normal movement if we haven't just teleported
        if not just_teleported:
            # Normalize the direction vector
            distance = math.sqrt(dx*dx + dy*dy)
            if distance > 0:
                dx = dx / distance
                dy = dy / distance
            
            # Update last direction
            self.last_direction = [dx, dy]
            
            # Check if we're stuck in a loop by comparing current position to history
            current_pos_rounded = (round(self.pos[0]), round(self.pos[1]))
            
            # Keep history limited to last 10 positions
            if len(self.position_history) > 10:
                self.position_history.pop(0)
                
            # If we've been in this position recently, increment stuck counter
            if current_pos_rounded in self.position_history:
                self.stuck_counter += 1
            else:
                self.stuck_counter = 0
                
            # Add current position to history
            self.position_history.append(current_pos_rounded)
            
            # If stuck for too long, add randomness to movement
            if self.stuck_counter > 5:
                # Add significant randomness to break out of the loop
                dx += random.uniform(-0.5, 0.5)
                dy += random.uniform(-0.5, 0.5)
                # Normalize again after adding randomness
                length = math.sqrt(dx*dx + dy*dy)
                if length > 0:
                    dx /= length
                    dy /= length
                # Reset stuck counter
                self.stuck_counter = 0
            
            # Try to move in the exact direction toward the target
            new_pos = self.pos.copy()
            new_pos[0] += dx * self.speed
            new_pos[1] += dy * self.speed
            
            # Add a small random offset to help break out of loops
            if random.random() < 0.1:  # 10% chance to add randomness
                new_pos[0] += random.uniform(-0.5, 0.5)
                new_pos[1] += random.uniform(-0.5, 0.5)
            
            # Check for wall collisions
            if not self.game.map.is_wall(new_pos[0], new_pos[1]):
                self.pos = new_pos
            else:
                # If direct path is blocked, try moving horizontally or vertically
                # This helps the enemy navigate around corners
                
                # Try horizontal movement with slightly increased speed to help get around corners
                horizontal_pos = self.pos.copy()
                horizontal_pos[0] += dx * (self.speed * 1.2)
                
                # Try vertical movement with slightly increased speed to help get around corners
                vertical_pos = self.pos.copy()
                vertical_pos[1] += dy * (self.speed * 1.2)
                
                # Check which direction is valid
                horizontal_valid = not self.game.map.is_wall(horizontal_pos[0], horizontal_pos[1])
                vertical_valid = not self.game.map.is_wall(vertical_pos[0], vertical_pos[1])
                
                # Choose the better direction based on which gets us closer to the target
                if horizontal_valid and vertical_valid:
                    # Calculate which direction gets us closer to the target
                    horizontal_dist = math.sqrt((horizontal_pos[0] - (self.pos[0] + dx * 10))**2 + 
                                               (horizontal_pos[1] - (self.pos[1] + dy * 10))**2)
                    vertical_dist = math.sqrt((vertical_pos[0] - (self.pos[0] + dx * 10))**2 + 
                                             (vertical_pos[1] - (self.pos[1] + dy * 10))**2)
                    
                    if horizontal_dist <= vertical_dist:
                        self.pos = horizontal_pos
                    else:
                        self.pos = vertical_pos
                elif horizontal_valid:
                    self.pos = horizontal_pos
                elif vertical_valid:
                    self.pos = vertical_pos
                # If neither direction is valid, try diagonal movements to get unstuck
                if not horizontal_valid and not vertical_valid:
                    # Try diagonal movements
                    diag1_pos = self.pos.copy()
                    diag1_pos[0] += self.speed
                    diag1_pos[1] += self.speed
                    
                    diag2_pos = self.pos.copy()
                    diag2_pos[0] += self.speed
                    diag2_pos[1] -= self.speed
                    
                    diag3_pos = self.pos.copy()
                    diag3_pos[0] -= self.speed
                    diag3_pos[1] += self.speed
                    
                    diag4_pos = self.pos.copy()
                    diag4_pos[0] -= self.speed
                    diag4_pos[1] -= self.speed
                    
                    # Check which diagonals are valid
                    diag_positions = [diag1_pos, diag2_pos, diag3_pos, diag4_pos]
                    valid_diags = []
                    
                    for pos in diag_positions:
                        if not self.game.map.is_wall(pos[0], pos[1]):
                            valid_diags.append(pos)
                    
                    # If any diagonal is valid, choose one randomly
                    if valid_diags:
                        self.pos = random.choice(valid_diags)
        
        # Check if enemy is on a portal
        portal_dest = self.game.map.is_portal(self.pos[0], self.pos[1])
        if portal_dest:
            # Add a cooldown to prevent immediate teleportation back
            if not hasattr(self, 'last_teleport_time') or time.time() - self.last_teleport_time > 1.0:
                # Teleport the enemy to the destination portal
                self.pos = [portal_dest[0], portal_dest[1]]
                self.last_teleport_time = time.time()
                
                # Move the enemy off the portal with a larger distance
                self._move_off_portal(distance_multiplier=2.0)
    
    def _is_in_same_region_as_player(self):
        """Check if the enemy is in the same region as the player
        
        Returns:
            bool: True if in same region, False otherwise
        """
        # Get all regions
        regions = self.game.map._find_disconnected_regions()
        
        # Find which region the enemy is in
        enemy_tile_x = int(self.pos[0] // self.game.map.tile_size)
        enemy_tile_y = int(self.pos[1] // self.game.map.tile_size)
        
        # Find which region the player is in
        player_tile_x = int(self.game.player.pos[0] // self.game.map.tile_size)
        player_tile_y = int(self.game.player.pos[1] // self.game.map.tile_size)
        
        # Check if they're in the same region
        for region in regions:
            if (enemy_tile_x, enemy_tile_y) in region and (player_tile_x, player_tile_y) in region:
                return True
        
        return False
    
    def _find_nearest_portal(self):
        """Find the best portal to use to reach the player
        
        Returns:
            tuple or None: (x, y) of the best portal, or None if no portals
        """
        if not self.game.map.portal_manager.portals:
            return None
            
        # Get all regions in the map
        regions = self.game.map._find_disconnected_regions()
        
        # Find which region the enemy is in
        enemy_tile_x = int(self.pos[0] // self.game.map.tile_size)
        enemy_tile_y = int(self.pos[1] // self.game.map.tile_size)
        enemy_region = None
        
        # Find which region the player is in
        player_tile_x = int(self.game.player.pos[0] // self.game.map.tile_size)
        player_tile_y = int(self.game.player.pos[1] // self.game.map.tile_size)
        player_region = None
        
        # Identify the regions
        for region in regions:
            if (enemy_tile_x, enemy_tile_y) in region:
                enemy_region = region
            if (player_tile_x, player_tile_y) in region:
                player_region = region
        
        # If we couldn't identify the regions, fall back to nearest portal
        if not enemy_region or not player_region:
            return self._find_nearest_portal_in_same_region()
        
        # Get all portals in the enemy's region
        portals_in_enemy_region = []
        for portal_x, portal_y in self.game.map.portal_manager.portals:
            portal_tile_x = int(portal_x // self.game.map.tile_size)
            portal_tile_y = int(portal_y // self.game.map.tile_size)
            
            if (portal_tile_x, portal_tile_y) in enemy_region:
                portals_in_enemy_region.append((portal_x, portal_y))
        
        # If no portals in enemy region, return None
        if not portals_in_enemy_region:
            return None
        
        # Find the destination of each portal
        portal_destinations = {}
        for portal_x, portal_y in portals_in_enemy_region:
            dest = self.game.map.portal_manager.get_portal_destination((portal_x, portal_y))
            if dest:
                portal_destinations[(portal_x, portal_y)] = dest
        
        # Check if any portal leads directly to the player's region
        direct_portals = []
        for portal, dest in portal_destinations.items():
            dest_tile_x = int(dest[0] // self.game.map.tile_size)
            dest_tile_y = int(dest[1] // self.game.map.tile_size)
            
            if (dest_tile_x, dest_tile_y) in player_region:
                direct_portals.append(portal)
        
        # If we found portals that lead directly to the player's region, choose the nearest one
        if direct_portals:
            nearest_portal = None
            min_distance = float('inf')
            
            for portal_x, portal_y in direct_portals:
                dx = portal_x - self.pos[0]
                dy = portal_y - self.pos[1]
                distance = math.sqrt(dx*dx + dy*dy)
                
                if distance < min_distance:
                    nearest_portal = (portal_x, portal_y)
                    min_distance = distance
            
            return nearest_portal
        
        # If no direct path to player's region, fall back to nearest portal
        return self._find_nearest_portal_in_same_region()
    
    def _find_nearest_portal_in_same_region(self):
        """Find the nearest portal in the same region as the enemy
        
        Returns:
            tuple or None: (x, y) of nearest portal, or None if no portals
        """
        if not self.game.map.portal_manager.portals:
            return None
            
        # Find the nearest portal
        nearest_portal = None
        min_distance = float('inf')
        
        for portal_x, portal_y in self.game.map.portal_manager.portals:
            # Calculate distance to this portal
            dx = portal_x - self.pos[0]
            dy = portal_y - self.pos[1]
            distance = math.sqrt(dx*dx + dy*dy)
            
            # Check if this is the nearest portal so far
            if distance < min_distance:
                # Make sure this portal is in the same region as the enemy
                portal_tile_x = int(portal_x // self.game.map.tile_size)
                portal_tile_y = int(portal_y // self.game.map.tile_size)
                
                enemy_tile_x = int(self.pos[0] // self.game.map.tile_size)
                enemy_tile_y = int(self.pos[1] // self.game.map.tile_size)
                
                # Check if they're in the same region
                regions = self.game.map._find_disconnected_regions()
                for region in regions:
                    if (enemy_tile_x, enemy_tile_y) in region and (portal_tile_x, portal_tile_y) in region:
                        nearest_portal = (portal_x, portal_y)
                        min_distance = distance
                        break
        
        return nearest_portal
    
    def check_collision_with_player(self):
        """Check if the enemy has collided with the player
        
        Returns:
            bool: True if collision detected, False otherwise
        """
        # Calculate distance between enemy and player
        dx = self.pos[0] - self.game.player.pos[0]
        dy = self.pos[1] - self.game.player.pos[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Check if distance is less than the detection radius
        # Using the detection radius (half of portal radius) instead of sum of sizes
        return distance < self.detection_radius
    
    def render(self, screen):
        """Render the enemy
        
        Args:
            screen: Pygame screen to render on
        """
        # Determine color based on state
        if self.is_sleeping:
            color = (200, 100, 100)  # Lighter red when sleeping
        elif self.is_stunned:
            color = (150, 150, 150)  # Gray when stunned
        else:
            color = self.color  # Normal color (red)
            
        # Draw enemy (circle)
        pygame.draw.circle(
            screen, 
            color,
            (int(self.pos[0]), int(self.pos[1])), 
            self.size
        )
        
        # Draw a "Z" above the enemy if sleeping
        if self.is_sleeping:
            # Draw the Z on top of the circle
            font = pygame.font.SysFont(None, 24)
            z_text = font.render("Z", True, (255, 255, 255))
            # Center the Z on the enemy
            text_rect = z_text.get_rect(center=(int(self.pos[0]), int(self.pos[1])))
            screen.blit(z_text, text_rect)
            
        # Draw a "!" above the enemy if stunned
        elif self.is_stunned:
            # Draw the ! on top of the circle
            font = pygame.font.SysFont(None, 24)
            stun_text = font.render("!", True, (255, 255, 255))
            # Center the ! on the enemy
            text_rect = stun_text.get_rect(center=(int(self.pos[0]), int(self.pos[1])))
            screen.blit(stun_text, text_rect)
