# Dungeon Crawler

A 2D dungeon crawler game built in Python with procedurally generated dungeons, portals, coins to collect, and an enemy that hunts you down.

## Features

- **Procedurally Generated Maps**: Every game generates a unique dungeon layout
- **Portal System**: Colored portals connect different regions of the dungeon
- **Coin Collection**: Collect all 5 gold coins to win the game
- **Enemy AI**: Avoid the enemy that hunts you down (sleeps for 5 seconds at the start)
- **Multiple Regions**: Maps are divided into connected regions via portals

## Setup

### Prerequisites

- Python 3.13.2 or higher
- pip package manager

### Installation

It's recommended to use a virtual environment to avoid conflicts with other Python packages.

```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Running the Game

```bash
# Make sure your virtual environment is activated
python main.py
```

## How to Play

- **Arrow Keys**: Move the player (green circle)
- **Collect**: All 5 gold coins to win
- **Avoid**: The enemy (red circle) that chases you
- **Use**: Colored portals to navigate between dungeon regions
- **Press R**: Generate a new map or restart after winning/losing

## Project Structure

```
dungeon_crawler/
├── characters/
│   ├── character.py    # Base Character class
│   ├── player.py       # Player-specific behavior
│   └── enemy.py        # Enemy-specific behavior
├── game/
│   ├── game.py         # Main Game class
│   └── ui.py           # UI rendering
└── map/
    ├── map.py          # Core Map class
    ├── generation.py   # Map generation logic
    ├── portals.py      # Portal management
    └── coins.py        # Coin management
```

## Testing

The project includes comprehensive unit tests for all components:

```bash
# Run all tests
python -m unittest discover tests
```

```bash
# Make sure your virtual environment is activated
python main.py
```
- **R Key**: Generate a new random dungeon layout
- **Close Window**: Exit the game

### Game Rules

1. The game starts with a randomly generated dungeon
2. Your character is placed in a valid position (not inside a wall)
3. You cannot walk through walls (gray blocks)
4. Collect all 5 gold coins scattered throughout the dungeon to win
5. Blue and purple circles are portals that teleport you between disconnected areas of the dungeon
6. After winning, press R to generate a new dungeon and play again

### Map Generation

The game uses a cellular automata algorithm to create natural-looking cave systems. Each time you start the game or press R, you'll get a different dungeon layout to explore.

### Portal System

The game automatically creates at least two dungeon sections connected by portal pairs:

- **Blue portals** connect to **purple portals** and vice versa
- Walk into a portal to teleport to its paired portal in another part of the dungeon
- Portals have a pulsing white center to make them more visible
- The game guarantees at least two separate dungeon sections with portals, even if the natural generation would create just one connected region
- If needed, the game will intelligently split a large open area into two sections with a wall that has a single gap

## Troubleshooting

### Common Issues

- **'pygame' module not found**: Make sure you've activated your virtual environment and installed the requirements
- **Screen size issues**: The game is designed for a minimum resolution of 800x600
- **Performance issues**: If the game runs slowly, try closing other applications
