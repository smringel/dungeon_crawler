"""Player class for Dungeon Crawler"""

import pygame
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
