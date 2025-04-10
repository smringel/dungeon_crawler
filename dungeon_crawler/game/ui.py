"""UI functionality for Dungeon Crawler"""

import pygame
import math

class UIManager:
    """Handles UI rendering and interactions"""
    
    def __init__(self, game):
        """Initialize the UI manager
        
        Args:
            game: The Game instance this manager belongs to
        """
        self.game = game
        self.header_height = 40
    
    def render(self, screen):
        """Render the UI elements
        
        Args:
            screen: Pygame screen to render on
        """
        # Create a semi-transparent header bar for instructions
        header = pygame.Surface((self.game.width, self.header_height), pygame.SRCALPHA)
        header.fill((0, 0, 0, 180))  # Black with transparency
        screen.blit(header, (0, 0))
        
        # Draw UI text in the header
        font = pygame.font.SysFont(None, 24)
        title_text = font.render('Dungeon Crawler - Press R to generate new map', True, self.game.WHITE)
        screen.blit(title_text, (20, 10))  # Left aligned in header
        
        # Draw coin counter in the header
        coin_text = font.render(f'Coins: {self.game.coins_collected}/{self.game.total_coins}', True, self.game.GOLD)
        screen.blit(coin_text, (self.game.width - 150, 10))  # Right aligned in header
        
        # Draw win message if game is won
        if self.game.game_won:
            self._render_win_screen(screen)
            
        # Draw lose message if game is lost
        elif self.game.game_lost:
            self._render_lose_screen(screen)
    
    def _render_win_screen(self, screen):
        """Render the win screen
        
        Args:
            screen: Pygame screen to render on
        """
        # Create a semi-transparent overlay that covers the entire game area
        # but preserves our header
        overlay = pygame.Surface((self.game.width, self.game.height - self.header_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))  # Black with transparency
        screen.blit(overlay, (0, self.header_height))  # Position below header
        
        # Calculate pulsing effect for the win message
        elapsed = pygame.time.get_ticks() - self.game.win_message_time
        pulse = 0.5 + 0.5 * math.sin(elapsed / 200)  # Value between 0 and 1
        
        # Draw win message
        big_font = pygame.font.SysFont(None, 72)
        win_text = big_font.render('YOU WIN!', True, (int(255 * pulse), 255, int(100 * pulse)))
        text_rect = win_text.get_rect(center=(self.game.width // 2, self.game.height // 2 - 40))
        screen.blit(win_text, text_rect)
        
        # Draw instructions to continue
        small_font = pygame.font.SysFont(None, 36)
        continue_text = small_font.render('Press R to play again', True, self.game.WHITE)
        continue_rect = continue_text.get_rect(center=(self.game.width // 2, self.game.height // 2 + 40))
        screen.blit(continue_text, continue_rect)
        
        # Draw a trophy icon
        trophy_x = self.game.width // 2
        trophy_y = self.game.height // 2 - 120
        
        # Draw trophy base
        pygame.draw.rect(
            screen,
            self.game.GOLD,
            pygame.Rect(trophy_x - 20, trophy_y + 25, 40, 10)
        )
        
        # Draw trophy stem
        pygame.draw.rect(
            screen,
            self.game.GOLD,
            pygame.Rect(trophy_x - 5, trophy_y, 10, 30)
        )
        
        # Draw trophy cup
        pygame.draw.arc(
            screen,
            self.game.GOLD,
            pygame.Rect(trophy_x - 20, trophy_y - 25, 40, 40),
            math.pi, 2 * math.pi,
            5  # Width
        )
    
    def _render_lose_screen(self, screen):
        """Render the lose screen
        
        Args:
            screen: Pygame screen to render on
        """
        # Create a semi-transparent overlay that covers the entire game area
        # but preserves our header
        overlay = pygame.Surface((self.game.width, self.game.height - self.header_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))  # Black with transparency
        screen.blit(overlay, (0, self.header_height))  # Position below header
        
        # Calculate pulsing effect for the lose message
        elapsed = pygame.time.get_ticks() - self.game.lose_message_time
        pulse = 0.5 + 0.5 * math.sin(elapsed / 200)  # Value between 0 and 1
        
        # Draw lose message
        big_font = pygame.font.SysFont(None, 72)
        lose_text = big_font.render('GAME OVER', True, (255, int(100 * pulse), int(100 * pulse)))
        text_rect = lose_text.get_rect(center=(self.game.width // 2, self.game.height // 2 - 40))
        screen.blit(lose_text, text_rect)
        
        # Draw instructions to continue
        small_font = pygame.font.SysFont(None, 36)
        continue_text = small_font.render('Press R to try again', True, self.game.WHITE)
        continue_rect = continue_text.get_rect(center=(self.game.width // 2, self.game.height // 2 + 40))
        screen.blit(continue_text, continue_rect)
        
        # Draw a skull icon
        skull_x = self.game.width // 2
        skull_y = self.game.height // 2 - 120
        
        # Draw skull (simplified)
        # Draw skull circle
        pygame.draw.circle(
            screen,
            self.game.WHITE,
            (skull_x, skull_y),
            25
        )
        
        # Draw eye sockets
        pygame.draw.circle(
            screen,
            (0, 0, 0),
            (skull_x - 8, skull_y - 5),
            5
        )
        pygame.draw.circle(
            screen,
            (0, 0, 0),
            (skull_x + 8, skull_y - 5),
            5
        )
        
        # Draw nose
        pygame.draw.polygon(
            screen,
            (0, 0, 0),
            [(skull_x, skull_y), (skull_x - 5, skull_y + 5), (skull_x + 5, skull_y + 5)]
        )
        
        # Draw teeth
        for i in range(-2, 3):
            pygame.draw.line(
                screen,
                (0, 0, 0),
                (skull_x + i * 5, skull_y + 10),
                (skull_x + i * 5, skull_y + 15),
                2
            )
