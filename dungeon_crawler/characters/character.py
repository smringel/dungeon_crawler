"""Base Character class for Dungeon Crawler"""

import pygame
import random
import math

class Character:
    """Base class for all characters in the game"""
    
    def __init__(self, game, size=15, speed=4, color=(255, 255, 255)):
        """Initialize the character
        
        Args:
            game: The Game instance this character belongs to
            size: The character's size in pixels
            speed: The character's movement speed
            color: The character's color (RGB tuple)
        """
        self.game = game
        self.size = size
        self.speed = speed
        self.color = color
        
        # Find a valid starting position
        self.pos = self._find_valid_start_position()
        
        # Track character's last movement direction
        self.last_direction = [0, 0]  # [dx, dy]
    
    def reset_position(self):
        """Reset the character's position to a valid starting position"""
        self.pos = self._find_valid_start_position()
        self.last_direction = [0, 0]
    
    def _find_valid_start_position(self):
        """Find a valid starting position for the character
        
        Returns:
            list: [x, y] position in pixels
        """
        # Start near the center of the map
        center_x = self.game.width // 2
        center_y = self.game.height // 2
        
        # Try positions in a spiral pattern around the center
        for radius in range(0, 200, 20):
            for angle in range(0, 360, 30):
                # Calculate position in a circle around the center
                x = center_x + int(radius * math.cos(math.radians(angle)))
                y = center_y + int(radius * math.sin(math.radians(angle)))
                
                # Check if this position is valid (not a wall)
                if not self.game.map.is_wall(x, y):
                    return [x, y]
        
        # Fallback: find any valid position
        for _ in range(100):
            x = random.randint(50, self.game.width - 50)
            y = random.randint(50, self.game.height - 50)
            if not self.game.map.is_wall(x, y):
                return [x, y]
        
        # Last resort: return the center and hope for the best
        return [center_x, center_y]
    
    def _move_off_portal(self, distance_multiplier=1.0):
        """Move the character off a portal after teleporting
        
        Args:
            distance_multiplier: Multiplier for the safe distance (default: 1.0)
        """
        # Get the safe distance from the map class and apply multiplier
        safe_distance = self.game.map.get_safe_distance_from_portal() * distance_multiplier
        
        # Try to move in the same direction the character was moving before teleporting
        if self.last_direction != [0, 0]:
            # Normalize the direction vector
            dx, dy = self.last_direction
            length = math.sqrt(dx*dx + dy*dy) if (dx*dx + dy*dy) > 0 else 1
            normalized_dx = dx / length
            normalized_dy = dy / length
            
            # Calculate the position using the safe distance
            new_x = self.pos[0] + normalized_dx * safe_distance
            new_y = self.pos[1] + normalized_dy * safe_distance
            
            # Check if this position is valid (not a wall)
            if not self.game.map.is_wall(new_x, new_y):
                self.pos = [new_x, new_y]
                return
        
        # If we can't move in the same direction, try all four directions
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]  # Up, Right, Down, Left
        random.shuffle(directions)  # Randomize to avoid bias
        
        # Try with the safe distance
        for dx, dy in directions:
            # Normalize the direction vector
            length = math.sqrt(dx*dx + dy*dy)
            normalized_dx = dx / length
            normalized_dy = dy / length
            
            new_x = self.pos[0] + normalized_dx * safe_distance
            new_y = self.pos[1] + normalized_dy * safe_distance
            
            # Check if this position is valid (not a wall)
            if not self.game.map.is_wall(new_x, new_y):
                self.pos = [new_x, new_y]
                return
                
        # If all else fails, try with a smaller distance
        for factor in [0.75, 0.5, 0.25]:
            reduced_distance = safe_distance * factor
            for dx, dy in directions:
                # Normalize the direction vector
                length = math.sqrt(dx*dx + dy*dy)
                normalized_dx = dx / length
                normalized_dy = dy / length
                
                new_x = self.pos[0] + normalized_dx * reduced_distance
                new_y = self.pos[1] + normalized_dy * reduced_distance
                
                # Check if this position is valid (not a wall)
                if not self.game.map.is_wall(new_x, new_y):
                    self.pos = [new_x, new_y]
                    return
    
    def render(self, screen):
        """Render the character
        
        Args:
            screen: Pygame screen to render on
        """
        # Draw character (simple circle)
        pygame.draw.circle(
            screen, 
            self.color, 
            (int(self.pos[0]), int(self.pos[1])), 
            self.size
        )
