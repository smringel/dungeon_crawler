#!/usr/bin/env python3

"""
Dungeon Crawler Game - Main Entry Point
"""

import sys
import pygame
from dungeon_crawler.game import Game  # This now imports from the game package


def main():
    """Main function to run the game"""
    # Initialize pygame
    pygame.init()
    
    # Create and run the game
    game = Game()
    game.run()
    
    # Clean up pygame
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
