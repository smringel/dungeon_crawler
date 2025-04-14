"""Main Game class for Dungeon Crawler"""

import pygame
from pygame.locals import *
from dungeon_crawler.map import Map
from dungeon_crawler.characters import Player, Enemy
from dungeon_crawler.game.ui import UIManager

class Game:
    """Main game class that handles the game loop and logic"""
    
    def __init__(self):
        """Initialize the game"""
        # Set up display
        self.width, self.height = 800, 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('Dungeon Crawler')
        
        # Set up clock for controlling frame rate
        self.clock = pygame.time.Clock()
        self.fps = 60
        
        # Game state
        self.running = True
        self.game_won = False
        self.game_lost = False
        self.coins_collected = 0
        self.total_coins = 5  # Must match the value in Map class
        self.win_message_time = 0
        self.lose_message_time = 0
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.GOLD = (255, 215, 0)
        
        # Create the map
        self.map = Map(self.width, self.height)
        
        # Create the player
        self.player = Player(self)
        
        # Create multiple enemies (one per region)
        self.enemies = []
        self._create_enemies()
        
        # Create the UI manager
        self.ui_manager = UIManager(self)
    
    def run(self):
        """Main game loop"""
        while self.running:
            # Handle events
            self.handle_events()
            
            # Update game state
            self.update()
            
            # Render the game
            self.render()
            
            # Control frame rate
            self.clock.tick(self.fps)
            
            # Update the display
            pygame.display.flip()  # Update the screen with what we've drawn
    
    def update(self):
        """Update game state"""
        # Skip updates if game is over
        if self.game_won or self.game_lost:
            return
            
        # Update player's weapon
        self.player.update_weapon()
        
        # Update all enemies
        for enemy in self.enemies:
            enemy.update()
            
            # Check for collision with any enemy
            if enemy.check_collision_with_player():
                self.game_lost = True
                self.lose_message_time = pygame.time.get_ticks()
                break
    
    def _create_enemies(self):
        """Create one enemy per region"""
        # Clear existing enemies
        self.enemies = []
        
        # Get all regions
        regions = self.map._find_disconnected_regions()
        
        # Create one enemy per region
        for region in regions:
            enemy = Enemy(self, region)
            self.enemies.append(enemy)
    
    def reset_game(self):
        """Reset the game state and generate a new map"""
        self.map.generate_random_map()
        self.player.reset_position()
        
        # Recreate enemies for the new map
        self._create_enemies()
        
        self.game_won = False
        self.game_lost = False
        self.coins_collected = 0
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
            # Add R key to regenerate the map
            elif event.type == KEYDOWN and event.key == K_r:
                self.reset_game()
        
        # If game is won or lost, only handle quit events
        if self.game_won or self.game_lost:
            return
        
        # Handle player movement
        self.player.handle_movement()
    
    def render(self):
        """Render the game"""
        # Clear the screen
        self.screen.fill(self.BLACK)
        
        # Draw the map
        self.map.render(self.screen)
        
        # Draw player
        self.player.render(self.screen)
        
        # Draw all enemies
        for enemy in self.enemies:
            enemy.render(self.screen)
        
        # Draw UI elements
        self.ui_manager.render(self.screen)
