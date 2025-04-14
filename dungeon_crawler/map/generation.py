"""Map generation functionality for Dungeon Crawler"""

import random

class MapGenerator:
    """Handles the generation of random dungeon maps"""
    
    def __init__(self, map_instance):
        """Initialize the map generator
        
        Args:
            map_instance: The Map instance this generator belongs to
        """
        self.map = map_instance
    
    def generate_layout(self):
        """Generate a random dungeon layout using cellular automata"""
        # Initialize with random walls (1) and floors (0)
        # Start with a higher probability of walls to create more interesting caves
        self.map.layout = []
        for y in range(self.map.grid_height):
            row = []
            for x in range(self.map.grid_width):
                # Always have walls around the edges
                if x == 0 or y == 0 or x == self.map.grid_width - 1 or y == self.map.grid_height - 1:
                    row.append(1)  # Wall
                else:
                    # Random wall or floor with 45% chance of being a wall
                    row.append(1 if random.random() < 0.45 else 0)
            self.map.layout.append(row)
        
        # Apply cellular automata rules to smooth the map
        # This creates more natural-looking caverns
        self._smooth_map(5)  # Apply smoothing 5 times
        
        # Ensure there's a clear path for the player to move
        self._ensure_playable()
        
        # Check if all regions are large enough, if not regenerate
        attempts = 0
        max_attempts = 10  # Increase max attempts to find a good map
        while not self._check_regions_size() and attempts < max_attempts:
            # Try again with different parameters
            self._regenerate_layout()
            attempts += 1
            
        # If we still don't have valid regions, force merge small regions
        if not self._check_regions_size():
            self._merge_small_regions()
    
    def _count_wall_neighbors(self, x, y):
        """Count the number of walls in the 8 neighboring cells"""
        count = 0
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:  # Skip the cell itself
                    continue
                nx, ny = x + i, y + j
                # Count out-of-bounds as walls
                if nx < 0 or ny < 0 or nx >= len(self.map.layout[0]) or ny >= len(self.map.layout):
                    count += 1
                elif self.map.layout[ny][nx] == 1:
                    count += 1
        return count
    
    def _smooth_map(self, iterations):
        """Apply cellular automata smoothing rules"""
        for _ in range(iterations):
            new_layout = [row[:] for row in self.map.layout]  # Create a copy
            
            for y in range(1, len(self.map.layout) - 1):
                for x in range(1, len(self.map.layout[0]) - 1):
                    neighbors = self._count_wall_neighbors(x, y)
                    
                    # Apply the cellular automata rules
                    # If a cell has more than 4 wall neighbors, it becomes a wall
                    # If a cell has fewer than 3 wall neighbors, it becomes a floor
                    if neighbors > 4:
                        new_layout[y][x] = 1
                    elif neighbors < 3:
                        new_layout[y][x] = 0
            
            self.map.layout = new_layout
    
    def _ensure_playable(self):
        """Make sure the map is playable by creating some guaranteed paths"""
        # Create a path from the center to a few random points
        center_x = len(self.map.layout[0]) // 2
        center_y = len(self.map.layout) // 2
        
        # Ensure the center is a floor
        if 0 < center_x < len(self.map.layout[0]) - 1 and 0 < center_y < len(self.map.layout) - 1:
            self.map.layout[center_y][center_x] = 0
        
        # Create a few random destinations
        destinations = []
        for _ in range(3):  # Create 3 random destinations
            dest_x = random.randint(5, len(self.map.layout[0]) - 5)
            dest_y = random.randint(5, len(self.map.layout) - 5)
            destinations.append((dest_x, dest_y))
        
        # Create paths from center to each destination
        for dest_x, dest_y in destinations:
            self._create_path(center_x, center_y, dest_x, dest_y)
    
    def _create_path(self, start_x, start_y, end_x, end_y):
        """Create a path from start to end by carving through walls"""
        current_x, current_y = start_x, start_y
        
        # Simple algorithm: move in the direction of the end point
        while current_x != end_x or current_y != end_y:
            # Decide whether to move in x or y direction
            if random.random() < 0.5 and current_x != end_x:
                # Move in x direction
                current_x += 1 if current_x < end_x else -1
            elif current_y != end_y:
                # Move in y direction
                current_y += 1 if current_y < end_y else -1
            
            # Carve out this position (make it a floor)
            if 1 <= current_x < len(self.map.layout[0]) - 1 and 1 <= current_y < len(self.map.layout) - 1:
                self.map.layout[current_y][current_x] = 0  # Floor
    
    def _create_artificial_region(self, main_region):
        """Create an artificial second region by adding a wall to split the main region"""
        if not main_region:
            return False  # Return False to indicate failure
            
        # Convert the set to a list for easier manipulation
        region_tiles = list(main_region)
        
        # If the region is too small, don't try to split it
        if len(region_tiles) < 20:
            return False  # Return False to indicate failure
            
        # Find the approximate center of the region
        sum_x = sum(x for x, y in region_tiles)
        sum_y = sum(y for x, y in region_tiles)
        center_x = sum_x // len(region_tiles)
        center_y = sum_y // len(region_tiles)
        
        # Determine if the region is more horizontal or vertical
        min_x = min(x for x, y in region_tiles)
        max_x = max(x for x, y in region_tiles)
        min_y = min(y for x, y in region_tiles)
        max_y = max(y for x, y in region_tiles)
        width = max_x - min_x + 1
        height = max_y - min_y + 1
        
        # Count walls added to ensure we actually split the region
        walls_added = 0
        
        # Try both horizontal and vertical splits, starting with the longer dimension
        split_directions = []
        if width >= height:
            split_directions.extend(['horizontal', 'vertical'])
        else:
            split_directions.extend(['vertical', 'horizontal'])
            
        for split_direction in split_directions:
            if split_direction == 'horizontal':
                # Create a vertical wall with a gap
                wall_x = center_x
                gap_y = center_y
                
                for y in range(min_y, max_y + 1):
                    # Skip creating a wall at the gap position
                    if y == gap_y:
                        continue
                        
                    # Add a wall tile if this position is in the region
                    if (wall_x, y) in main_region and 0 < wall_x < len(self.map.layout[0]) - 1 and 0 < y < len(self.map.layout) - 1:
                        self.map.layout[y][wall_x] = 1  # Wall
                        walls_added += 1
            else:  # Vertical split
                # Create a horizontal wall with a gap
                wall_y = center_y
                gap_x = center_x
                
                for x in range(min_x, max_x + 1):
                    # Skip creating a wall at the gap position
                    if x == gap_x:
                        continue
                        
                    # Add a wall tile if this position is in the region
                    if (x, wall_y) in main_region and 0 < x < len(self.map.layout[0]) - 1 and 0 < wall_y < len(self.map.layout) - 1:
                        self.map.layout[wall_y][x] = 1  # Wall
                        walls_added += 1
            
            # If we added enough walls, we're done
            if walls_added >= 3:
                return True  # Return True to indicate success
                
        # If we couldn't add enough walls with either approach, try a more aggressive split
        if walls_added < 3:
            # Try creating a cross-shaped wall pattern with a gap in the center
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:  # Right, Left, Down, Up
                wall_length = max(width, height) // 3  # Make walls about 1/3 of the region size
                
                for i in range(1, wall_length + 1):
                    x = center_x + (dx * i)
                    y = center_y + (dy * i)
                    
                    # Add a wall tile if this position is in the region
                    if (x, y) in main_region and 0 < x < len(self.map.layout[0]) - 1 and 0 < y < len(self.map.layout) - 1:
                        self.map.layout[y][x] = 1  # Wall
                        walls_added += 1
            
        return walls_added >= 3  # Return True if we added enough walls
    
    def _create_maze_pattern(self):
        """Create a simple maze-like pattern in the center of the map to force multiple regions"""
        # Find the center of the map
        center_x = len(self.map.layout[0]) // 2
        center_y = len(self.map.layout) // 2
        
        # Create a plus sign pattern with gaps
        # Horizontal line
        for x in range(center_x - 5, center_x + 6):
            if x != center_x - 3 and x != center_x + 3:  # Leave gaps
                if 0 < x < len(self.map.layout[0]) - 1 and 0 < center_y < len(self.map.layout) - 1:
                    self.map.layout[center_y][x] = 1  # Wall
        
        # Vertical line
        for y in range(center_y - 5, center_y + 6):
            if y != center_y - 3 and y != center_y + 3:  # Leave gaps
                if 0 < center_x < len(self.map.layout[0]) - 1 and 0 < y < len(self.map.layout) - 1:
                    self.map.layout[y][center_x] = 1  # Wall
    
    def _force_create_second_region(self):
        """Force create a second region by adding a wall across the middle of the map"""
        # Determine if the map is more horizontal or vertical
        if len(self.map.layout[0]) > len(self.map.layout):
            # More horizontal, add a vertical wall
            wall_x = len(self.map.layout[0]) // 2
            gap_y = len(self.map.layout) // 2
            
            for y in range(1, len(self.map.layout) - 1):
                if y != gap_y:
                    self.map.layout[y][wall_x] = 1  # Wall
        else:
            # More vertical, add a horizontal wall
            wall_y = len(self.map.layout) // 2
            gap_x = len(self.map.layout[0]) // 2
            
            for x in range(1, len(self.map.layout[0]) - 1):
                if x != gap_x:
                    self.map.layout[wall_y][x] = 1  # Wall
    
    def _regenerate_layout(self):
        """Regenerate the layout with a higher wall probability"""
        # Initialize with random walls (1) and floors (0)
        # Use a higher wall probability to create more separated regions
        self.map.layout = []
        for y in range(self.map.grid_height):
            row = []
            for x in range(self.map.grid_width):
                # Always have walls around the edges
                if x == 0 or y == 0 or x == self.map.grid_width - 1 or y == self.map.grid_height - 1:
                    row.append(1)  # Wall
                else:
                    # Higher chance of being a wall (60% instead of 45%)
                    row.append(1 if random.random() < 0.6 else 0)
            self.map.layout.append(row)
        
        # Apply cellular automata rules to smooth the map
        self._smooth_map(3)  # Fewer smoothing iterations
        
        # Ensure there's a clear path for the player to move
        self._ensure_playable()
        
        # Force create a division
        self._force_create_second_region()
    
    def _check_regions_size(self):
        """Check if all regions are at least 6 tiles in size
        
        Returns:
            bool: True if all regions are large enough, False otherwise
        """
        # Find all disconnected regions
        regions = self.map._find_disconnected_regions()
        
        # Check if each region is large enough
        min_region_size = 6  # Minimum size for a playable region
        for region in regions:
            if len(region) < min_region_size:
                print(f"Found region with only {len(region)} tiles, minimum is {min_region_size}")
                return False
                
        # Also check if we have at least 2 regions
        if len(regions) < 2:
            print("Not enough regions found")
            return False
            
        return True
        
    def _merge_small_regions(self):
        """Merge small regions by removing walls between them
        
        This ensures all regions meet the minimum size requirement
        """
        print("Attempting to merge small regions...")
        regions = self.map._find_disconnected_regions()
        
        # Sort regions by size (smallest first)
        regions.sort(key=len)
        
        min_region_size = 6  # Minimum size for a playable region
        
        # Find small regions that need to be merged
        small_regions = [region for region in regions if len(region) < min_region_size]
        
        for small_region in small_regions:
            # Find the closest region to merge with
            closest_region = None
            min_distance = float('inf')
            
            # Calculate center of small region
            small_x_sum = sum(x for x, y in small_region)
            small_y_sum = sum(y for x, y in small_region)
            small_center_x = small_x_sum / len(small_region)
            small_center_y = small_y_sum / len(small_region)
            
            # Find the closest region that's large enough
            for region in regions:
                if region != small_region and len(region) >= min_region_size:
                    # Calculate center of this region
                    x_sum = sum(x for x, y in region)
                    y_sum = sum(y for x, y in region)
                    center_x = x_sum / len(region)
                    center_y = y_sum / len(region)
                    
                    # Calculate distance between centers
                    distance = ((center_x - small_center_x) ** 2 + (center_y - small_center_y) ** 2) ** 0.5
                    
                    if distance < min_distance:
                        min_distance = distance
                        closest_region = region
            
            if closest_region:
                # Create a path between the small region and the closest region
                # Find the closest points between the two regions
                min_point_distance = float('inf')
                small_point = None
                closest_point = None
                
                for sx, sy in small_region:
                    for cx, cy in closest_region:
                        dist = ((sx - cx) ** 2 + (sy - cy) ** 2) ** 0.5
                        if dist < min_point_distance:
                            min_point_distance = dist
                            small_point = (sx, sy)
                            closest_point = (cx, cy)
                
                if small_point and closest_point:
                    # Create a path between these points by removing walls
                    self._create_path(small_point[0], small_point[1], closest_point[0], closest_point[1])
                    print(f"Created path between regions of size {len(small_region)} and {len(closest_region)}")
        
        # Verify regions again
        regions = self.map._find_disconnected_regions()
        print(f"After merging: {len(regions)} regions with sizes: {[len(r) for r in regions]}")

