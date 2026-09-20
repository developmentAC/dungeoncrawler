"""
Map generation using binary matrices.
"""

import random
from typing import List, Tuple, Optional
import config


class Room:
    """Represents a rectangular room in the dungeon."""
    
    def __init__(self, x: int, y: int, width: int, height: int, is_secret: bool = False):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.is_secret = is_secret
        self.center_x = x + width // 2
        self.center_y = y + height // 2
    
    def intersects(self, other: 'Room') -> bool:
        """Check if this room intersects with another room."""
        return (self.x < other.x + other.width and
                self.x + self.width > other.x and
                self.y < other.y + other.height and
                self.y + self.height > other.y)


class DungeonMap:
    """Generates and manages dungeon maps using binary matrices."""
    
    def __init__(self, width: int, height: int, difficulty: str):
        self.width = width
        self.height = height
        self.difficulty = difficulty
        self.difficulty_settings = config.DIFFICULTY_SETTINGS[difficulty]
        
        # Binary matrix: 0 = wall, 1 = floor
        self.tiles: List[List[int]] = [[0 for _ in range(width)] for _ in range(height)]
        
        # Rooms list
        self.rooms: List[Room] = []
        self.secret_rooms: List[Room] = []
        
        # Special locations
        self.spawn_pos: Optional[Tuple[int, int]] = None
        self.exit_pos: Optional[Tuple[int, int]] = None
        self.secret_doors: List[Tuple[int, int]] = []
        
        # Track which rooms already have secret doors to prevent duplicates
        self.rooms_with_doors: set = set()
        
        # Generate the map
        self._generate()
    
    def _generate(self):
        """Generate the dungeon map."""
        # Create rooms
        for _ in range(config.MAX_ROOMS):
            width = random.randint(config.ROOM_MIN_SIZE, config.ROOM_MAX_SIZE)
            height = random.randint(config.ROOM_MIN_SIZE, config.ROOM_MAX_SIZE)
            x = random.randint(1, self.width - width - 1)
            y = random.randint(1, self.height - height - 1)
            
            is_secret = random.random() < config.SECRET_ROOM_CHANCE and len(self.secret_rooms) < 2
            new_room = Room(x, y, width, height, is_secret)
            
            # Check if room intersects with existing rooms
            if not any(new_room.intersects(room) for room in self.rooms):
                self._carve_room(new_room)
                
                if is_secret:
                    # Secret room - don't connect with corridor, only accessible via purple door
                    self.secret_rooms.append(new_room)
                    self.rooms.append(new_room)
                    # Store the last regular room as the door placement reference
                    if self.rooms:
                        # Find nearest non-secret room for door placement
                        nearest_regular_room = None
                        min_distance = float('inf')
                        for room in self.rooms:
                            if not room.is_secret:
                                distance = abs(room.center_x - new_room.center_x) + abs(room.center_y - new_room.center_y)
                                if distance < min_distance:
                                    min_distance = distance
                                    nearest_regular_room = room
                        if nearest_regular_room:
                            self._add_secret_door(nearest_regular_room, new_room)
                else:
                    # Regular room - connect to previous room with corridor
                    if self.rooms:
                        # Find the last non-secret room
                        prev_regular_room = None
                        for room in reversed(self.rooms):
                            if not room.is_secret:
                                prev_regular_room = room
                                break
                        
                        if prev_regular_room:
                            self._create_corridor(prev_regular_room.center_x, prev_regular_room.center_y,
                                                new_room.center_x, new_room.center_y)
                    
                    self.rooms.append(new_room)
        
        # Set spawn position (first non-secret room)
        if self.rooms:
            # Find first non-secret room for player spawn
            spawn_room = None
            for room in self.rooms:
                if not room.is_secret:
                    spawn_room = room
                    break
            
            # Fallback to first room if no non-secret rooms found (shouldn't happen)
            if spawn_room is None:
                spawn_room = self.rooms[0]
            
            self.spawn_pos = (spawn_room.center_x, spawn_room.center_y)
            
            # Set exit position (last non-secret room)
            exit_room = self.rooms[-1]
            for room in reversed(self.rooms):
                if not room.is_secret:
                    exit_room = room
                    break
            self.exit_pos = (exit_room.center_x, exit_room.center_y)
    
    def _carve_room(self, room: Room):
        """Carve out a room in the map (set tiles to 1)."""
        for y in range(room.y, room.y + room.height):
            for x in range(room.x, room.x + room.width):
                if 0 <= x < self.width and 0 <= y < self.height:
                    self.tiles[y][x] = 1
    
    def _create_corridor(self, x1: int, y1: int, x2: int, y2: int):
        """Create a corridor between two points."""
        # Horizontal then vertical
        if random.random() < 0.5:
            # Horizontal first
            for x in range(min(x1, x2), max(x1, x2) + 1):
                if 0 <= x < self.width and 0 <= y1 < self.height:
                    self.tiles[y1][x] = 1
                    # Make corridor wider
                    if 0 <= y1 + 1 < self.height:
                        self.tiles[y1 + 1][x] = 1
            # Then vertical
            for y in range(min(y1, y2), max(y1, y2) + 1):
                if 0 <= x2 < self.width and 0 <= y < self.height:
                    self.tiles[y][x2] = 1
                    if 0 <= x2 + 1 < self.width:
                        self.tiles[y][x2 + 1] = 1
        else:
            # Vertical first
            for y in range(min(y1, y2), max(y1, y2) + 1):
                if 0 <= x1 < self.width and 0 <= y < self.height:
                    self.tiles[y][x1] = 1
                    if 0 <= x1 + 1 < self.width:
                        self.tiles[y][x1 + 1] = 1
            # Then horizontal
            for x in range(min(x1, x2), max(x1, x2) + 1):
                if 0 <= x < self.width and 0 <= y2 < self.height:
                    self.tiles[y2][x] = 1
                    if 0 <= y2 + 1 < self.height:
                        self.tiles[y2 + 1][x] = 1
    
    def _add_secret_door(self, from_room: Room, to_room: Room):
        """Add a secret door in the main dungeon that leads to an isolated secret room.
        Only one door per room is allowed."""
        # The secret room is isolated (no corridor), so place door in main dungeon
        if to_room.is_secret:
            secret_room = to_room
            main_room = from_room
        else:
            secret_room = from_room
            main_room = to_room
        
        # Find walkable tiles in the main dungeon corridors near the secret room
        # Place door in a corridor tile that's reasonably close to the secret room
        candidates = []
        
        # Search in the general area between the main room and secret room
        search_radius = 8
        center_x = (main_room.center_x + secret_room.center_x) // 2
        center_y = (main_room.center_y + secret_room.center_y) // 2
        
        for x in range(center_x - search_radius, center_x + search_radius):
            for y in range(center_y - search_radius, center_y + search_radius):
                # Must be walkable
                if not self.is_walkable(x, y):
                    continue
                
                # Must NOT be inside the secret room
                if (secret_room.x <= x < secret_room.x + secret_room.width and
                    secret_room.y <= y < secret_room.y + secret_room.height):
                    continue
                
                # Must NOT be inside any room (should be in corridor)
                # Also track which room this position is in (if any) to prevent duplicates
                in_room = False
                room_id = None
                for room in self.rooms:
                    if not room.is_secret:
                        if (room.x <= x < room.x + room.width and
                            room.y <= y < room.y + room.height):
                            in_room = True
                            room_id = id(room)
                            break
                
                # Add to candidates only if not in a room, or if room doesn't have a door yet
                if not in_room:
                    candidates.append((x, y, None))
                elif room_id and room_id not in self.rooms_with_doors:
                    candidates.append((x, y, room_id))
        
        # Choose door location closest to secret room (but not inside it)
        if candidates:
            best_door = min(candidates,
                          key=lambda pos: abs(pos[0] - secret_room.center_x) + abs(pos[1] - secret_room.center_y))
            door_x, door_y, room_id = best_door
            self.secret_doors.append((door_x, door_y))
            # Mark this room as having a door
            if room_id:
                self.rooms_with_doors.add(room_id)
        else:
            # Fallback: place in main room near secret room (only if it doesn't have a door)
            main_room_id = id(main_room)
            if main_room_id not in self.rooms_with_doors:
                candidates = []
                for x in range(main_room.x + 1, main_room.x + main_room.width - 1):
                    for y in range(main_room.y + 1, main_room.y + main_room.height - 1):
                        if self.is_walkable(x, y):
                            candidates.append((x, y))
                
                if candidates:
                    best_door = min(candidates,
                                  key=lambda pos: abs(pos[0] - secret_room.center_x) + abs(pos[1] - secret_room.center_y))
                    self.secret_doors.append(best_door)
                    self.rooms_with_doors.add(main_room_id)
    
    def is_walkable(self, x: int, y: int) -> bool:
        """Check if a tile is walkable."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x] == 1
        return False
    
    def get_random_floor_position(self, exclude_secret: bool = False) -> Tuple[int, int]:
        """Get a random walkable floor position."""
        max_attempts = 100
        for _ in range(max_attempts):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            
            if self.is_walkable(x, y):
                # Check if it's in a secret room if we want to exclude them
                if exclude_secret:
                    in_secret = any(
                        room.x <= x < room.x + room.width and
                        room.y <= y < room.y + room.height
                        for room in self.secret_rooms
                    )
                    if in_secret:
                        continue
                return (x, y)
        
        # Fallback to spawn position
        return self.spawn_pos if self.spawn_pos else (self.width // 2, self.height // 2)
