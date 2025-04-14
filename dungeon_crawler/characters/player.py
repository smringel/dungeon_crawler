"""Player class for Dungeon Crawler"""

import pygame
import math
from pygame.locals import *

from dungeon_crawler.characters.character import Character

class Player(Character):
    """Player character that can be controlled by the user"""
    
    def __init__(self, game):
        """Initialize the player
        
        Args:
            game: The Game instance this player belongs to
        """
        # Initialize the base character with player-specific attributes
        super().__init__(
            game=game,
            size=15,
            speed=4,
            color=(0, 255, 0)  # Green
        )
        
        # Weapon properties
        self.weapon_active = False
        self.weapon_radius = game.map.portal_manager.portal_radius * 3  # Triple the portal capture radius
        self.weapon_angle = 0  # Current angle of the weapon (in radians)
        self.weapon_speed = 0.2  # Rotation speed in radians per frame
        self.weapon_color = (200, 200, 255)  # Light blue
        self.weapon_width = 5  # Width of the weapon line
        
        # Weapon cooldown
        self.weapon_cooldown = 1.0  # Seconds between weapon activations
        self.last_weapon_use = 0  # Time of last weapon use
    
    def handle_movement(self):
        """Handle player movement with arrow keys"""
        # Handle player movement with arrow keys
        keys = pygame.key.get_pressed()
        new_pos = self.pos.copy()
        moved = False
        
        # Track direction of movement
        dx, dy = 0, 0
        
        if keys[K_LEFT]:
            new_pos[0] -= self.speed
            dx = -1
            moved = True
        if keys[K_RIGHT]:
            new_pos[0] += self.speed
            dx = 1
            moved = True
        if keys[K_UP]:
            new_pos[1] -= self.speed
            dy = -1
            moved = True
        if keys[K_DOWN]:
            new_pos[1] += self.speed
            dy = 1
            moved = True
        
        # Update last direction if player moved
        if moved:
            self.last_direction = [dx, dy]
        
        # Handle weapon activation with spacebar
        if keys[K_SPACE]:
            self.activate_weapon()
            
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
            
            # Check if player is on a coin
            coin_pos = self.game.map.is_coin(self.pos[0], self.pos[1])
            if coin_pos:
                # Collect the coin
                if self.game.map.collect_coin(coin_pos):
                    self.game.coins_collected += 1
                    
                    # Check if all coins are collected
                    if self.game.coins_collected >= self.game.total_coins:
                        self.game.game_won = True
                        self.game.win_message_time = pygame.time.get_ticks()
    
    def activate_weapon(self):
        """Activate the player's weapon if cooldown has elapsed"""
        current_time = pygame.time.get_ticks() / 1000.0  # Convert to seconds
        
        # Check if cooldown has elapsed
        if current_time - self.last_weapon_use >= self.weapon_cooldown:
            self.weapon_active = True
            self.last_weapon_use = current_time
            
            # Reset weapon angle to point in the direction of movement or default to right
            if self.last_direction != [0, 0]:
                self.weapon_angle = math.atan2(self.last_direction[1], self.last_direction[0])
            else:
                self.weapon_angle = 0  # Default to pointing right
                
            # Store the starting angle to track rotation progress
            self.start_angle = self.weapon_angle
            self.rotation_complete = False
    
    def update_weapon(self):
        """Update the weapon state and check for collisions with enemies"""
        if not self.weapon_active:
            return
            
        # Update weapon angle (rotate clockwise)
        self.weapon_angle += self.weapon_speed
        
        # Check if we've completed a full 360-degree rotation
        # We need to account for the starting angle to ensure a full circle
        if not hasattr(self, 'rotation_complete'):
            self.rotation_complete = False
            
        if not self.rotation_complete and self.weapon_angle >= self.start_angle + math.pi * 2:
            self.rotation_complete = True
            
        # Deactivate after completing the full rotation
        if self.rotation_complete:
            self.weapon_active = False
            self.weapon_angle = 0
            return
            
        # Calculate weapon endpoint
        weapon_end_x = self.pos[0] + math.cos(self.weapon_angle) * self.weapon_radius
        weapon_end_y = self.pos[1] + math.sin(self.weapon_angle) * self.weapon_radius
        
        # Check for collisions with all enemies
        for enemy in self.game.enemies:
            # Calculate distance from weapon endpoint to enemy
            dx = weapon_end_x - enemy.pos[0]
            dy = weapon_end_y - enemy.pos[1]
            distance = math.sqrt(dx*dx + dy*dy)
            
            # Check if weapon hit the enemy (within enemy size)
            if distance <= enemy.size:
                # Only count a hit if enough time has passed since the last hit
                current_time = pygame.time.get_ticks() / 1000.0
                if current_time - enemy.last_hit_time >= 0.5:  # Prevent multiple hits in quick succession
                    enemy.last_hit_time = current_time
                    
                    # Stun the enemy for 1 second
                    enemy.is_stunned = True
                    enemy.stun_until = current_time + 1.0
    
    def render(self, screen):
        """Render the player and weapon
        
        Args:
            screen: Pygame screen to render on
        """
        # Draw player (simple circle)
        pygame.draw.circle(
            screen, 
            self.color, 
            (int(self.pos[0]), int(self.pos[1])), 
            self.size
        )
        
        # Draw weapon if active
        if self.weapon_active:
            # Calculate weapon endpoint
            weapon_end_x = self.pos[0] + math.cos(self.weapon_angle) * self.weapon_radius
            weapon_end_y = self.pos[1] + math.sin(self.weapon_angle) * self.weapon_radius
            
            # Draw the weapon as a line
            pygame.draw.line(
                screen,
                self.weapon_color,
                (int(self.pos[0]), int(self.pos[1])),
                (int(weapon_end_x), int(weapon_end_y)),
                self.weapon_width
            )
