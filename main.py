"""
Main game module for Dungeon Crawler.
"""

import pygame
import sys
import random
import math
from typing import List, Optional, Tuple

import config
from dungeon_map import DungeonMap
from entities import (Player, Ghost, CrazyBear, MadRabbit, Coin, Treasure, Weapon, BowAndArrow, Arrow, Heart, Door, Exit,
                      SpeedBoost, SpeedPill, Shield, DoublePoints, VisionBoost,
                      RubyGem, EmeraldGem, SapphireGem, FreezeScroll, ProtectionShield,
                      ArtifactMaxWeapons, ArtifactMaxArrows, ArtifactFullHealth, ArtifactEnemyDestroyer,
                      WizardStaff, ChillinSkeleton, DarkWizard, WizardBlast)
from ui import UI
from visual_effects import VisualEffectsManager, Fireball, Fireball


class Game:
    """Main game class managing game state and loop."""
    
    def __init__(self):
        pygame.init()
        
        # Game settings
        self.resolution = config.DEFAULT_RESOLUTION
        self.difficulty = config.DEFAULT_DIFFICULTY
        self.screen_width, self.screen_height = config.RESOLUTIONS[self.resolution]
        
        # Initialize display
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Dungeon Crawler")
        self.clock = pygame.time.Clock()
        
        # Game state
        self.state = config.STATE_MENU
        self.menu_selection = 0
        self.pause_selection = 0
        self.show_instructions = False
        self.instruction_scroll = 0
        
        # Game objects
        self.ui = UI(self.screen_width, self.screen_height)
        self.visual_effects = VisualEffectsManager()  # Visual effects system
        self.dungeon_map: Optional[DungeonMap] = None
        self.player: Optional[Player] = None
        self.ghosts: List[Ghost] = []
        self.bears: List[CrazyBear] = []
        self.rabbits: List[MadRabbit] = []  # Mad Rabbits
        self.skeletons: List[ChillinSkeleton] = []  # Chillin' Skeletons
        self.wizards: List[DarkWizard] = []  # Dark Wizards
        self.wizard_blasts: List[WizardBlast] = []  # Wizard projectiles
        self.items: List = []  # Includes coins, treasures, weapons, bows, and power-ups
        self.doors: List[Door] = []
        self.dead_enemies: List = []  # Track dead enemies for respawn system
        self.exit: Optional[Exit] = None
        self.discovered_tiles: set = set()  # Fog of war system
        
        # Room tracking for secret room mechanic
        self.current_room_index: Optional[int] = None  # Track which room player is in
        self.original_room_index: Optional[int] = None  # Track starting room
        self.in_secret_room: bool = False  # Track if player is in secret room
        self.player_pre_transition_pos: Optional[Tuple[float, float]] = None  # Store position before transition
        self.transition_start_time: int = 0  # Track transition start time
        self.transition_target_room: Optional[int] = None  # Target room index for transition
        self.doors: List[Door] = []  # Teleport doors linking map locations
        self.last_door_use_time: int = 0  # Cooldown for door usage
        
        # Camera
        self.camera_x = 0
        self.camera_y = 0
        
        # Level
        self.current_level = 1
        self.total_items = 0
        self.open_room_items = 0  # Items in open rooms only
        self.open_room_items_collected = 0  # Items collected from open rooms
        self.exit_requirement_message_time = 0  # Time when message was shown
        
        # Combo system
        self.combo_count = 0
        self.last_kill_time = 0
        self.combo_timeout = 3000  # 3 seconds to maintain combo
        
        # Level timer for completion bonus
        self.level_start_time = 0
        self.level_completion_bonus = 0
        
        # Running flag
        self.running = True
    
    def set_resolution(self, resolution: str):
        """Change the game resolution."""
        self.resolution = resolution
        self.screen_width, self.screen_height = config.RESOLUTIONS[resolution]
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.ui = UI(self.screen_width, self.screen_height)
    
    def start_new_game(self):
        """Start a new game with complete reset."""
        self.current_level = 1
        self.player = None  # Reset player to ensure fresh start with full health
        self.start_level()
    
    def start_level(self):
        """Initialize a new level."""
        # Save current score and inventory if player exists
        saved_score = 0
        saved_coins = 0
        saved_treasures = 0
        saved_weapons = 0
        saved_arrows = 0
        saved_has_bow = False
        saved_max_weapons = config.PLAYER_BASE_MAX_WEAPONS
        saved_max_arrows = config.PLAYER_BASE_MAX_ARROWS
        saved_health = None
        saved_max_health = None
        if self.player:
            saved_score = self.player.score
            saved_coins = self.player.coins_collected
            saved_treasures = self.player.treasures_collected
            saved_weapons = self.player.weapons
            saved_arrows = self.player.arrows
            saved_has_bow = self.player.has_bow
            saved_max_weapons = self.player.max_weapons
            saved_max_arrows = self.player.max_arrows
            saved_health = self.player.health
            saved_max_health = self.player.max_health
        
        # Create dungeon map
        self.dungeon_map = DungeonMap(config.MAP_WIDTH, config.MAP_HEIGHT, self.difficulty)
        
        # Reset discovered tiles
        self.discovered_tiles = set()
        
        # Reset dead enemies list
        self.dead_enemies = []
        
        # Create player
        difficulty_settings = config.DIFFICULTY_SETTINGS[self.difficulty]
        spawn_x, spawn_y = self.dungeon_map.spawn_pos
        self.player = Player(spawn_x, spawn_y, difficulty_settings["player_health"])
        
        # Restore saved progress (including transferable capacities)
        self.player.score = saved_score
        self.player.coins_collected = saved_coins
        self.player.treasures_collected = saved_treasures
        self.player.weapons = saved_weapons
        self.player.arrows = saved_arrows
        self.player.has_bow = saved_has_bow
        self.player.max_weapons = saved_max_weapons
        self.player.max_arrows = saved_max_arrows
        
        # Restore health if this is not the first level
        if saved_health is not None and saved_max_health is not None:
            self.player.health = saved_health
            self.player.max_health = saved_max_health
        
        # Discover initial area around player
        self._discover_area(spawn_x, spawn_y, radius=5)
        
        # Create ghosts
        self.ghosts = []
        ghost_count = difficulty_settings["ghost_count"]
        for _ in range(ghost_count):
            x, y = self.dungeon_map.get_random_floor_position(exclude_secret=True)
            # Make sure ghost doesn't spawn too close to player
            while abs(x - spawn_x) < 5 and abs(y - spawn_y) < 5:
                x, y = self.dungeon_map.get_random_floor_position(exclude_secret=True)
            ghost = Ghost(x, y, difficulty_settings["ghost_speed"])
            self.ghosts.append(ghost)
        
        # Create crazy bears
        self.bears = []
        bear_count = difficulty_settings["bear_count"]
        for _ in range(bear_count):
            x, y = self.dungeon_map.get_random_floor_position(exclude_secret=True)
            # Make sure bear doesn't spawn too close to player
            while abs(x - spawn_x) < 5 and abs(y - spawn_y) < 5:
                x, y = self.dungeon_map.get_random_floor_position(exclude_secret=True)
            bear = CrazyBear(x, y, config.BEAR_SPEED)
            self.bears.append(bear)
        
        # Create mad rabbits (3 per level)
        self.rabbits = []
        rabbit_count = 3
        for _ in range(rabbit_count):
            x, y = self.dungeon_map.get_random_floor_position(exclude_secret=True)
            # Make sure rabbit doesn't spawn too close to player
            while abs(x - spawn_x) < 5 and abs(y - spawn_y) < 5:
                x, y = self.dungeon_map.get_random_floor_position(exclude_secret=True)
            rabbit = MadRabbit(x, y, config.RABBIT_SPEED)
            self.rabbits.append(rabbit)
        
        # Create chillin' skeletons (2 per level)
        self.skeletons = []
        skeleton_count = 2
        for _ in range(skeleton_count):
            x, y = self.dungeon_map.get_random_floor_position(exclude_secret=True)
            # Make sure skeleton doesn't spawn too close to player
            while abs(x - spawn_x) < 5 and abs(y - spawn_y) < 5:
                x, y = self.dungeon_map.get_random_floor_position(exclude_secret=True)
            skeleton = ChillinSkeleton(x, y)
            self.skeletons.append(skeleton)
        
        # Create dark wizards (1 per level)
        self.wizards = []
        self.wizard_blasts = []
        wizard_count = 1
        for _ in range(wizard_count):
            x, y = self.dungeon_map.get_random_floor_position(exclude_secret=True)
            # Make sure wizard doesn't spawn too close to player
            while abs(x - spawn_x) < 5 and abs(y - spawn_y) < 5:
                x, y = self.dungeon_map.get_random_floor_position(exclude_secret=True)
            wizard = DarkWizard(x, y)
            self.wizards.append(wizard)
        
        # Create doors - teleport doors (purple) and secret room doors (grey)
        self.doors = []
        self.secret_room_return_doors = []
        
        # 1. Create PURPLE teleport doors (hidden hallway shortcuts between open rooms)
        # These allow quick travel between distant open rooms (2-3 doors)
        map_width = self.dungeon_map.width
        map_height = self.dungeon_map.height
        
        num_teleport_pairs = random.randint(1, 2)  # 1-2 pairs = 2-4 doors, we'll limit to first pair for now
        
        # Create first teleport pair (left-right sides)
        left_door_x, left_door_y = None, None
        for attempt in range(100):
            x = random.randint(2, map_width // 3)
            y = random.randint(2, map_height - 2)
            if self.dungeon_map.is_walkable(x, y):
                left_door_x, left_door_y = x, y
                break
        
        right_door_x, right_door_y = None, None
        for attempt in range(100):
            x = random.randint(2 * map_width // 3, map_width - 2)
            y = random.randint(2, map_height - 2)
            if self.dungeon_map.is_walkable(x, y):
                right_door_x, right_door_y = x, y
                break
        
        # Create linked teleport door pair
        if left_door_x and right_door_x:
            left_door = Door(left_door_x, left_door_y, door_type="teleport")
            right_door = Door(right_door_x, right_door_y, door_type="teleport")
            
            # Find walkable offset positions near each door
            left_target_x, left_target_y = left_door_x, left_door_y
            right_target_x, right_target_y = right_door_x, right_door_y
            
            for offset_x, offset_y in [(3, 0), (0, 3), (-3, 0), (0, -3), (2, 2), (-2, 2), (2, -2), (-2, -2)]:
                test_x, test_y = right_door_x + offset_x, right_door_y + offset_y
                if self.dungeon_map.is_walkable(test_x, test_y):
                    right_target_x, right_target_y = test_x, test_y
                    break
            
            for offset_x, offset_y in [(3, 0), (0, 3), (-3, 0), (0, -3), (2, 2), (-2, 2), (2, -2), (-2, -2)]:
                test_x, test_y = left_door_x + offset_x, left_door_y + offset_y
                if self.dungeon_map.is_walkable(test_x, test_y):
                    left_target_x, left_target_y = test_x, test_y
                    break
            
            left_door.target_x = right_target_x
            left_door.target_y = right_target_y
            right_door.target_x = left_target_x
            right_door.target_y = left_target_y
            
            self.doors.append(left_door)
            self.doors.append(right_door)
        
        # Optionally create second teleport pair (top-bottom)
        if num_teleport_pairs > 1:
            top_door_x, top_door_y = None, None
            for attempt in range(100):
                x = random.randint(map_width // 4, 3 * map_width // 4)
                y = random.randint(2, map_height // 3)
                if self.dungeon_map.is_walkable(x, y):
                    top_door_x, top_door_y = x, y
                    break
            
            bottom_door_x, bottom_door_y = None, None
            for attempt in range(100):
                x = random.randint(map_width // 4, 3 * map_width // 4)
                y = random.randint(2 * map_height // 3, map_height - 2)
                if self.dungeon_map.is_walkable(x, y):
                    bottom_door_x, bottom_door_y = x, y
                    break
            
            if top_door_x and bottom_door_x:
                top_door = Door(top_door_x, top_door_y, door_type="teleport")
                bottom_door = Door(bottom_door_x, bottom_door_y, door_type="teleport")
                
                # Find walkable offset positions
                top_target_x, top_target_y = top_door_x, top_door_y
                bottom_target_x, bottom_target_y = bottom_door_x, bottom_door_y
                
                for offset_x, offset_y in [(3, 0), (0, 3), (-3, 0), (0, -3)]:
                    test_x, test_y = bottom_door_x + offset_x, bottom_door_y + offset_y
                    if self.dungeon_map.is_walkable(test_x, test_y):
                        bottom_target_x, bottom_target_y = test_x, test_y
                        break
                
                for offset_x, offset_y in [(3, 0), (0, 3), (-3, 0), (0, -3)]:
                    test_x, test_y = top_door_x + offset_x, top_door_y + offset_y
                    if self.dungeon_map.is_walkable(test_x, test_y):
                        top_target_x, top_target_y = test_x, test_y
                        break
                
                top_door.target_x = bottom_target_x
                top_door.target_y = bottom_target_y
                bottom_door.target_x = top_target_x
                bottom_door.target_y = top_target_y
                
                self.doors.append(top_door)
                self.doors.append(bottom_door)
        
        # 2. Create GREY secret room entrance doors (lead to hidden rooms)
        # These appear in open room walls/floors and lead to fixed hidden room locations
        for i, secret_room in enumerate(self.dungeon_map.secret_rooms):
            if i < len(self.dungeon_map.secret_doors):
                door_x, door_y = self.dungeon_map.secret_doors[i]
                
                # Ensure door is on walkable floor in open room
                if self.dungeon_map.is_walkable(door_x, door_y):
                    door = Door(door_x, door_y, door_type="secret")
                    door.linked_secret_room_index = self.dungeon_map.rooms.index(secret_room)
                    self.doors.append(door)
                else:
                    # Find nearby walkable tile
                    for offset_x in range(-2, 3):
                        for offset_y in range(-2, 3):
                            new_x = door_x + offset_x
                            new_y = door_y + offset_y
                            if self.dungeon_map.is_walkable(new_x, new_y):
                                door = Door(new_x, new_y, door_type="secret")
                                door.linked_secret_room_index = self.dungeon_map.rooms.index(secret_room)
                                self.doors.append(door)
                                break
                        else:
                            continue
                        break
            
            # Create BROWN return door in hidden room (exit back to open rooms)
            return_x = secret_room.center_x + 3
            return_y = secret_room.center_y + 3
            
            # Validate return door is on walkable floor, otherwise find nearby spot
            if not self.dungeon_map.is_walkable(return_x, return_y):
                # Search for nearest walkable tile in secret room
                found_spot = False
                for radius in range(1, 8):  # Search up to 8 tiles away
                    for offset_x in range(-radius, radius + 1):
                        for offset_y in range(-radius, radius + 1):
                            test_x = secret_room.center_x + offset_x
                            test_y = secret_room.center_y + offset_y
                            if self.dungeon_map.is_walkable(test_x, test_y):
                                return_x = test_x
                                return_y = test_y
                                found_spot = True
                                break
                        if found_spot:
                            break
                    if found_spot:
                        break
                
                # If still no spot found, use center as last resort
                if not found_spot:
                    return_x = secret_room.center_x
                    return_y = secret_room.center_y
            
            return_door = Door(return_x, return_y, door_type="return")
            return_door.is_return_door = True
            self.secret_room_return_doors.append(return_door)
        
        # Validate: Ensure every secret room has a return door
        if len(self.secret_room_return_doors) != len(self.dungeon_map.secret_rooms):
            print(f"WARNING: Secret room count ({len(self.dungeon_map.secret_rooms)}) does not match return door count ({len(self.secret_room_return_doors)})")
        
        # Room tracking
        self.current_room_index = 0
        self.original_room_index = 0
        self.in_secret_room = False
        
        # Helper function to check if position is occupied by a door
        def is_door_position(x: int, y: int) -> bool:
            # Check regular doors (purple teleport and grey secret entrances)
            for door in self.doors:
                if door.x == x and door.y == y:
                    return True
            # Check return doors (brown exits from hidden rooms)
            for return_door in self.secret_room_return_doors:
                if return_door.x == x and return_door.y == y:
                    return True
            return False
        
        # Create items (after doors are placed to avoid overlaps)
        self.items = []
        self.total_items = 0
        self.open_room_items = 0
        
        # Spawn coins (in open rooms only - these count toward exit requirement)
        coin_count = int(config.MAP_WIDTH * config.MAP_HEIGHT * difficulty_settings["item_spawn_rate"])
        for _ in range(coin_count):
            attempts = 0
            while attempts < 50:
                x, y = self.dungeon_map.get_random_floor_position(exclude_secret=True)
                if not is_door_position(x, y):
                    coin = Coin(x, y)
                    coin.is_open_room_item = True  # Mark as open room item
                    self.items.append(coin)
                    self.total_items += 1
                    self.open_room_items += 1
                    break
                attempts += 1
        
        # Spawn treasures (in open rooms only - these count toward exit requirement)
        treasure_count = int(config.MAP_WIDTH * config.MAP_HEIGHT * difficulty_settings["treasure_spawn_rate"])
        for _ in range(treasure_count):
            attempts = 0
            while attempts < 50:
                x, y = self.dungeon_map.get_random_floor_position(exclude_secret=True)
                if not is_door_position(x, y):
                    treasure = Treasure(x, y)
                    treasure.is_open_room_item = True  # Mark as open room item
                    self.items.append(treasure)
                    self.total_items += 1
                    self.open_room_items += 1
                    break
                attempts += 1
        
        # Spawn weapons (swords)
        weapon_count = int(config.MAP_WIDTH * config.MAP_HEIGHT * difficulty_settings["weapon_spawn_rate"])
        for _ in range(weapon_count):
            attempts = 0
            while attempts < 50:
                x, y = self.dungeon_map.get_random_floor_position()
                if not is_door_position(x, y):
                    self.items.append(Weapon(x, y))
                    break
                attempts += 1
        
        # Spawn arrows (half as many as swords)
        arrow_count = weapon_count // 2
        for _ in range(arrow_count):
            attempts = 0
            while attempts < 50:
                x, y = self.dungeon_map.get_random_floor_position()
                if not is_door_position(x, y):
                    self.items.append(Arrow(x, y))
                    break
                attempts += 1
        
        # Spawn bows (only 1 bow per level - enables arrow usage)
        bow_count = 1
        for _ in range(bow_count):
            attempts = 0
            while attempts < 50:
                x, y = self.dungeon_map.get_random_floor_position()
                if not is_door_position(x, y):
                    self.items.append(BowAndArrow(x, y))
                    break
                attempts += 1
        
        # Spawn hearts (5-6 per level)
        heart_count = random.randint(5, 6)
        for _ in range(heart_count):
            attempts = 0
            while attempts < 50:
                x, y = self.dungeon_map.get_random_floor_position()
                if not is_door_position(x, y):
                    self.items.append(Heart(x, y))
                    break
                attempts += 1
        
        # Spawn power-ups
        powerup_count = difficulty_settings["powerup_count"]
        powerup_types = [SpeedBoost, Shield, DoublePoints, VisionBoost]
        for _ in range(powerup_count):
            attempts = 0
            while attempts < 50:
                x, y = self.dungeon_map.get_random_floor_position()
                if not is_door_position(x, y):
                    # Randomly choose a power-up type
                    powerup_class = powerup_types[random.randint(0, len(powerup_types) - 1)]
                    self.items.append(powerup_class(x, y))
                    break
                attempts += 1
        
        # Spawn SpeedPills (2-4 per level)
        speed_pill_count = random.randint(2, 4)
        for _ in range(speed_pill_count):
            attempts = 0
            while attempts < 50:
                x, y = self.dungeon_map.get_random_floor_position()
                if not is_door_position(x, y):
                    self.items.append(SpeedPill(x, y))
                    break
                attempts += 1
        
        # Spawn gems (up to 3 per level) - animated treasures
        gem_count = random.randint(1, 3)
        gem_types = [RubyGem, EmeraldGem, SapphireGem]
        for _ in range(gem_count):
            attempts = 0
            while attempts < 50:
                x, y = self.dungeon_map.get_random_floor_position()
                if not is_door_position(x, y):
                    gem_class = random.choice(gem_types)
                    self.items.append(gem_class(x, y))
                    break
                attempts += 1
        
        # Spawn freeze scrolls (up to 3 per level)
        scroll_count = random.randint(1, 3)
        for _ in range(scroll_count):
            attempts = 0
            while attempts < 50:
                x, y = self.dungeon_map.get_random_floor_position()
                if not is_door_position(x, y):
                    self.items.append(FreezeScroll(x, y))
                    break
                attempts += 1
        
        # Spawn rare artifacts (up to 3 per level)
        artifact_count = random.randint(1, 3)
        artifact_types = [ArtifactMaxWeapons, ArtifactMaxArrows, ArtifactFullHealth, ArtifactEnemyDestroyer]
        for _ in range(artifact_count):
            attempts = 0
            while attempts < 50:
                x, y = self.dungeon_map.get_random_floor_position()
                if not is_door_position(x, y):
                    artifact_class = random.choice(artifact_types)
                    self.items.append(artifact_class(x, y))
                    break
                attempts += 1
        
        # Set initial room tracking
        self.current_room_index = 0  # Start in first room
        
        # Create exit
        exit_x, exit_y = self.dungeon_map.exit_pos
        self.exit = Exit(exit_x, exit_y)
        
        # Reset combo and timer
        self.combo_count = 0
        self.last_kill_time = 0
        self.level_start_time = pygame.time.get_ticks()
        self.level_completion_bonus = 0
        
        # Set game state
        self.state = config.STATE_PLAYING
    
    def _discover_area(self, center_x: float, center_y: float, radius: int = 3):
        """Discover tiles around a position."""
        cx = int(center_x)
        cy = int(center_y)
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                tx = cx + dx
                ty = cy + dy
                if 0 <= tx < self.dungeon_map.width and 0 <= ty < self.dungeon_map.height:
                    # Check if within circular radius
                    if dx * dx + dy * dy <= radius * radius:
                        self.discovered_tiles.add((tx, ty))
    
    def _get_player_room_index(self) -> Optional[int]:
        """Determine which room the player is currently in."""
        if not self.player or not self.dungeon_map:
            return None
        
        player_x = int(self.player.x)
        player_y = int(self.player.y)
        
        # Check each room
        for i, room in enumerate(self.dungeon_map.rooms):
            if (room.x <= player_x < room.x + room.width and
                room.y <= player_y < room.y + room.height):
                return i
        
        return None
    
    def _start_door_transition(self, target_x: int, target_y: int):
        """Start a door teleport transition with fade effect."""
        if self.state != config.STATE_PLAYING:
            return
        
        # Store target position
        self.transition_target_x = target_x
        self.transition_target_y = target_y
        
        # Set transition state
        self.state = config.STATE_TRANSITION
        self.transition_start_time = pygame.time.get_ticks()
    
    def _complete_door_transition(self):
        """Complete the door transition by moving player to target location."""
        if not hasattr(self, 'transition_target_x') or not hasattr(self, 'transition_target_y'):
            self.state = config.STATE_PLAYING
            return
        
        # Move player to target position
        self.player.x = self.transition_target_x
        self.player.y = self.transition_target_y
        
        # Discover new area
        self._discover_area(self.player.x, self.player.y, radius=5)
        
        # Return to playing state
        self.state = config.STATE_PLAYING
        self.transition_target_room = None
    
    def _start_room_transition(self, target_room_index: int, is_entering_secret: bool):
        """Start a room transition to a secret room or back."""
        if self.state != config.STATE_PLAYING:
            return
        
        # Store target room
        self.transition_target_room = target_room_index
        
        # Set transition state
        self.state = config.STATE_TRANSITION
        self.transition_start_time = pygame.time.get_ticks()
        
        # Update room tracking
        if is_entering_secret:
            self.in_secret_room = True
        else:
            self.in_secret_room = False
    
    def _update_combo(self, current_time: int):
        """Update combo counter when enemy is killed."""
        # Check if combo timeout has expired
        if current_time - self.last_kill_time > self.combo_timeout:
            self.combo_count = 0
        
        # Increment combo
        self.combo_count += 1
        self.last_kill_time = current_time
        
        # Show combo text if combo is 2 or higher
        if self.combo_count >= 2:
            self.visual_effects.create_combo_text(self.combo_count)
    
    def _calculate_level_bonus(self) -> int:
        """Calculate completion bonus based on time and items collected."""
        if self.level_start_time == 0:
            return 0
        
        current_time = pygame.time.get_ticks()
        elapsed_seconds = (current_time - self.level_start_time) / 1000.0
        
        # Time bonus: faster completion = more points
        # Max 1000 points for completing under 60 seconds, decreasing linearly
        time_bonus = max(0, int(1000 - (elapsed_seconds * 10)))
        
        # Perfect clear bonus: 500 points if all items collected
        perfect_bonus = 500 if self.player.coins_collected + self.player.treasures_collected >= self.total_items else 0
        
        return time_bonus + perfect_bonus
    
    def _complete_room_transition(self):
        """Complete the room transition by moving player to target room."""
        if self.transition_target_room is None or not self.dungeon_map:
            self.state = config.STATE_PLAYING
            return
        
        # Get target room
        if self.transition_target_room < len(self.dungeon_map.rooms):
            target_room = self.dungeon_map.rooms[self.transition_target_room]
            # Move player to center of target room
            self.player.x = target_room.center_x
            self.player.y = target_room.center_y
            self.current_room_index = self.transition_target_room
            
            # Discover new area
            self._discover_area(self.player.x, self.player.y, radius=5)
    
    def _handle_sword_attack(self):
        """Handle sword attack - consumes one sword from inventory."""
        if not self.player or not self.player.is_alive():
            return
        
        # Check if player has a sword
        if self.player.use_weapon():
            current_time = pygame.time.get_ticks()
            player_rect = self.player.get_rect()
            
            # Create red swirl effect around player
            player_center_x = self.player.x * config.TILE_SIZE + config.TILE_SIZE // 2
            player_center_y = self.player.y * config.TILE_SIZE + config.TILE_SIZE // 2
            self.visual_effects.create_sword_swirl_effect(player_center_x, player_center_y)
            
            # Check if any ghost is nearby
            for ghost in self.ghosts[:]:
                ghost_rect = ghost.get_rect()
                if player_rect.colliderect(ghost_rect):
                    ghost.health -= 1  # Deal 1 damage
                    # Only award score if enemy dies
                    if ghost.health <= 0:
                        # Update combo
                        self._update_combo(current_time)
                        score_gain = 200 if self.player.has_double_points(current_time) else 100
                        # Apply combo bonus
                        if self.combo_count > 1:
                            combo_multiplier = 1 + (self.combo_count - 1) * 0.1
                            score_gain = int(score_gain * combo_multiplier)
                        self.player.score += score_gain
                        # Create damage number
                        self.visual_effects.create_damage_number(
                            ghost.x * config.TILE_SIZE + config.TILE_SIZE // 2,
                            ghost.y * config.TILE_SIZE + config.TILE_SIZE // 2,
                            score_gain
                        )
                        self.visual_effects.trigger_screen_shake()
                    # Create hit effects
                    self.visual_effects.create_hit_particles(
                        ghost.x * config.TILE_SIZE + config.TILE_SIZE // 2,
                        ghost.y * config.TILE_SIZE + config.TILE_SIZE // 2,
                        config.RED
                    )
            
            # Check if any bear is nearby
            for bear in self.bears[:]:
                bear_rect = bear.get_rect()
                if player_rect.colliderect(bear_rect):
                    bear.health -= 1  # Deal 1 damage
                    # Only award score if enemy dies
                    if bear.health <= 0:
                        # Update combo
                        self._update_combo(current_time)
                        score_gain = 300 if self.player.has_double_points(current_time) else 150
                        # Apply combo bonus
                        if self.combo_count > 1:
                            combo_multiplier = 1 + (self.combo_count - 1) * 0.1
                            score_gain = int(score_gain * combo_multiplier)
                        self.player.score += score_gain
                        # Create damage number
                        self.visual_effects.create_damage_number(
                            bear.x * config.TILE_SIZE + config.TILE_SIZE // 2,
                            bear.y * config.TILE_SIZE + config.TILE_SIZE // 2,
                            score_gain
                        )
                        self.visual_effects.trigger_screen_shake()
                    # Create hit effects
                    self.visual_effects.create_hit_particles(
                        bear.x * config.TILE_SIZE + config.TILE_SIZE // 2,
                        bear.y * config.TILE_SIZE + config.TILE_SIZE // 2,
                        config.BROWN
                    )
            
            # Check if any rabbit is nearby
            for rabbit in self.rabbits[:]:
                rabbit_rect = rabbit.get_rect()
                if player_rect.colliderect(rabbit_rect):
                    rabbit.health -= 1  # Deal 1 damage
                    # Only award score if enemy dies
                    if rabbit.health <= 0:
                        # Update combo
                        self._update_combo(current_time)
                        score_gain = 400 if self.player.has_double_points(current_time) else 200
                        # Apply combo bonus
                        if self.combo_count > 1:
                            combo_multiplier = 1 + (self.combo_count - 1) * 0.1
                            score_gain = int(score_gain * combo_multiplier)
                        self.player.score += score_gain
                        # Create damage number
                        self.visual_effects.create_damage_number(
                            rabbit.x * config.TILE_SIZE + config.TILE_SIZE // 2,
                            rabbit.y * config.TILE_SIZE + config.TILE_SIZE // 2,
                            score_gain
                        )
                        self.visual_effects.trigger_screen_shake()
                    # Create hit effects
                    self.visual_effects.create_hit_particles(
                        rabbit.x * config.TILE_SIZE + config.TILE_SIZE // 2,
                        rabbit.y * config.TILE_SIZE + config.TILE_SIZE // 2,
                        config.PINK
                    )
            
            # Check if any skeleton is nearby (takes 3 hits)
            for skeleton in self.skeletons[:]:
                skeleton_rect = skeleton.get_rect()
                if player_rect.colliderect(skeleton_rect):
                    skeleton.health -= 1  # Deal 1 damage
                    # Only award score if enemy dies
                    if skeleton.health <= 0:
                        # Update combo
                        self._update_combo(current_time)
                        score_gain = 300 if self.player.has_double_points(current_time) else 150
                        # Apply combo bonus
                        if self.combo_count > 1:
                            combo_multiplier = 1 + (self.combo_count - 1) * 0.1
                            score_gain = int(score_gain * combo_multiplier)
                        self.player.score += score_gain
                        # Create damage number
                        self.visual_effects.create_damage_number(
                            skeleton.x * config.TILE_SIZE + config.TILE_SIZE // 2,
                            skeleton.y * config.TILE_SIZE + config.TILE_SIZE // 2,
                            score_gain
                        )
                        self.visual_effects.trigger_screen_shake()
                        # Drop loot with flinging effect
                        rand_val = random.random()
                        if rand_val < 0.33:
                            # 33% chance for protection shield
                            dropped_item = ProtectionShield(skeleton.x, skeleton.y)
                        elif rand_val < 0.66:
                            # 33% chance for treasure (gold)
                            dropped_item = Treasure(skeleton.x, skeleton.y)
                        else:
                            # 34% chance for freeze scroll
                            dropped_item = FreezeScroll(skeleton.x, skeleton.y)
                        
                        # Fling the item away from skeleton
                        fling_angle = random.uniform(0, 2 * math.pi)
                        fling_speed = random.uniform(0.15, 0.25)
                        dropped_item.vx = math.cos(fling_angle) * fling_speed
                        dropped_item.vy = math.sin(fling_angle) * fling_speed
                        self.items.append(dropped_item)
                    # Create hit effects
                    self.visual_effects.create_hit_particles(
                        skeleton.x * config.TILE_SIZE + config.TILE_SIZE // 2,
                        skeleton.y * config.TILE_SIZE + config.TILE_SIZE // 2,
                        config.SKELETON_COLOR
                    )
            
            # Check if any wizard is nearby (takes 5 hits)
            for wizard in self.wizards[:]:
                wizard_rect = wizard.get_rect()
                if player_rect.colliderect(wizard_rect):
                    wizard.health -= 1  # Deal 1 damage
                    # Only award score if enemy dies
                    if wizard.health <= 0:
                        # Update combo
                        self._update_combo(current_time)
                        score_gain = 500 if self.player.has_double_points(current_time) else 250
                        # Apply combo bonus
                        if self.combo_count > 1:
                            combo_multiplier = 1 + (self.combo_count - 1) * 0.1
                            score_gain = int(score_gain * combo_multiplier)
                        self.player.score += score_gain
                        # Create damage number
                        self.visual_effects.create_damage_number(
                            wizard.x * config.TILE_SIZE + config.TILE_SIZE // 2,
                            wizard.y * config.TILE_SIZE + config.TILE_SIZE // 2,
                            score_gain
                        )
                        self.visual_effects.trigger_screen_shake()
                        # Drop wizard staff
                        self.items.append(WizardStaff(wizard.x, wizard.y))
                    # Create hit effects
                    self.visual_effects.create_hit_particles(
                        wizard.x * config.TILE_SIZE + config.TILE_SIZE // 2,
                        wizard.y * config.TILE_SIZE + config.TILE_SIZE // 2,
                        config.WIZARD_COLOR
                    )
    
    def _handle_bow_attack(self):
        """Handle bow attack - consumes one bow from inventory and shoots arrow at nearest enemy."""
        if not self.player or not self.player.is_alive():
            return
        
        # Check if player has a bow and arrows before attempting to use
        if not self.player.has_bow or self.player.arrows <= 0:
            return  # Exit early if no bow or no arrows
        
        # Check if player has a bow
        if self.player.use_bow():
            current_time = pygame.time.get_ticks()
            
            # Find closest enemy within range
            closest_enemy = None
            closest_distance = 5  # Max bow range
            
            # Check ghosts
            for ghost in self.ghosts[:]:
                if ghost.is_alive():
                    dx = ghost.x - self.player.x
                    dy = ghost.y - self.player.y
                    distance = math.sqrt(dx * dx + dy * dy)
                    if distance < closest_distance:
                        closest_distance = distance
                        closest_enemy = ghost
            
            # Check bears
            for bear in self.bears[:]:
                if bear.is_alive():
                    dx = bear.x - self.player.x
                    dy = bear.y - self.player.y
                    distance = math.sqrt(dx * dx + dy * dy)
                    if distance < closest_distance:
                        closest_distance = distance
                        closest_enemy = bear
            
            # Check rabbits
            for rabbit in self.rabbits[:]:
                if rabbit.is_alive():
                    dx = rabbit.x - self.player.x
                    dy = rabbit.y - self.player.y
                    distance = math.sqrt(dx * dx + dy * dy)
                    if distance < closest_distance:
                        closest_distance = distance
                        closest_enemy = rabbit
            
            # Check skeletons
            for skeleton in self.skeletons[:]:
                if skeleton.is_alive():
                    dx = skeleton.x - self.player.x
                    dy = skeleton.y - self.player.y
                    distance = math.sqrt(dx * dx + dy * dy)
                    if distance < closest_distance:
                        closest_distance = distance
                        closest_enemy = skeleton
            
            # Check wizards
            for wizard in self.wizards[:]:
                if wizard.is_alive():
                    dx = wizard.x - self.player.x
                    dy = wizard.y - self.player.y
                    distance = math.sqrt(dx * dx + dy * dy)
                    if distance < closest_distance:
                        closest_distance = distance
                        closest_enemy = wizard
            
            # If an enemy was found, shoot arrow at it
            if closest_enemy:
                # Create arrow projectile
                player_screen_x = self.player.x * config.TILE_SIZE + config.TILE_SIZE // 2
                player_screen_y = self.player.y * config.TILE_SIZE + config.TILE_SIZE // 2
                target_screen_x = closest_enemy.x * config.TILE_SIZE + config.TILE_SIZE // 2
                target_screen_y = closest_enemy.y * config.TILE_SIZE + config.TILE_SIZE // 2
                
                self.visual_effects.create_arrow(
                    player_screen_x,
                    player_screen_y,
                    target_screen_x,
                    target_screen_y
                )
                
                # Damage enemy by 1 (arrow is just visual but deals 1 damage)
                closest_enemy.health -= 1
                
                # Calculate score with double points power-up (only if enemy dies)
                if closest_enemy.health <= 0:
                    # Update combo
                    self._update_combo(current_time)
                    
                    if isinstance(closest_enemy, MadRabbit):
                        score_gain = 400 if self.player.has_double_points(current_time) else 200
                    elif isinstance(closest_enemy, CrazyBear):
                        score_gain = 300 if self.player.has_double_points(current_time) else 150
                    elif isinstance(closest_enemy, ChillinSkeleton):
                        score_gain = 300 if self.player.has_double_points(current_time) else 150
                        # Drop loot
                        if random.random() < config.SKELETON_GOLD_DROP_CHANCE:
                            self.items.append(Treasure(closest_enemy.x, closest_enemy.y))
                        else:
                            self.items.append(FreezeScroll(closest_enemy.x, closest_enemy.y))
                    elif isinstance(closest_enemy, DarkWizard):
                        score_gain = 500 if self.player.has_double_points(current_time) else 250
                        # Drop wizard staff
                        self.items.append(WizardStaff(closest_enemy.x, closest_enemy.y))
                    else:  # Ghost
                        score_gain = 200 if self.player.has_double_points(current_time) else 100
                    
                    # Apply combo bonus
                    if self.combo_count > 1:
                        combo_multiplier = 1 + (self.combo_count - 1) * 0.1
                        score_gain = int(score_gain * combo_multiplier)
                    
                    self.player.score += score_gain
                    
                    # Create damage number
                    self.visual_effects.create_damage_number(
                        target_screen_x,
                        target_screen_y,
                        score_gain
                    )
                
                # Create hit effects (always show hit effect)
                self.visual_effects.create_hit_particles(
                    target_screen_x,
                    target_screen_y,
                    config.BLUE
                )
    
    def _handle_fireball_attack(self):
        """Handle fireball attack from wizard staff - deals double damage (2x swords/arrows)."""
        if not self.player or not self.player.is_alive():
            return
        
        # Check if player has wizard staff and has uses remaining
        if not self.player.has_wizard_staff or self.player.wizard_staff_uses <= 0:
            return
        
        current_time = pygame.time.get_ticks()
        
        # Find closest enemy within range (7 tiles - longer than bow)
        closest_enemy = None
        closest_distance = 7
        
        # Check all enemy types
        for enemy_list in [self.ghosts, self.bears, self.rabbits, self.skeletons, self.wizards]:
            for enemy in enemy_list[:]:
                if enemy.is_alive():
                    dx = enemy.x - self.player.x
                    dy = enemy.y - self.player.y
                    distance = math.sqrt(dx * dx + dy * dy)
                    if distance < closest_distance:
                        closest_distance = distance
                        closest_enemy = enemy
        
        # If an enemy was found, shoot fireball at it
        if closest_enemy:
            # Create fireball projectile
            player_screen_x = self.player.x * config.TILE_SIZE + config.TILE_SIZE // 2
            player_screen_y = self.player.y * config.TILE_SIZE + config.TILE_SIZE // 2
            target_screen_x = closest_enemy.x * config.TILE_SIZE + config.TILE_SIZE // 2
            target_screen_y = closest_enemy.y * config.TILE_SIZE + config.TILE_SIZE // 2
            
            # Create fireball
            fireball = Fireball(
                player_screen_x,
                player_screen_y,
                target_screen_x,
                target_screen_y
            )
            self.visual_effects.fireballs.append(fireball)
            
            # Damage enemy by 2 (double damage - equivalent to 2 swords/arrows)
            closest_enemy.health -= 2
            
            # Consume one staff use
            self.player.wizard_staff_uses -= 1
            if self.player.wizard_staff_uses <= 0:
                self.player.has_wizard_staff = False
            
            # Calculate score with double points power-up (only if enemy dies)
            if closest_enemy.health <= 0:
                # Update combo
                self._update_combo(current_time)
                
                if isinstance(closest_enemy, MadRabbit):
                    score_gain = 400 if self.player.has_double_points(current_time) else 200
                elif isinstance(closest_enemy, CrazyBear):
                    score_gain = 300 if self.player.has_double_points(current_time) else 150
                elif isinstance(closest_enemy, ChillinSkeleton):
                    score_gain = 300 if self.player.has_double_points(current_time) else 150
                    # Drop loot
                    if random.random() < config.SKELETON_GOLD_DROP_CHANCE:
                        self.items.append(Treasure(closest_enemy.x, closest_enemy.y))
                    else:
                        self.items.append(FreezeScroll(closest_enemy.x, closest_enemy.y))
                elif isinstance(closest_enemy, DarkWizard):
                    score_gain = 500 if self.player.has_double_points(current_time) else 250
                    # Drop wizard staff
                    self.items.append(WizardStaff(closest_enemy.x, closest_enemy.y))
                else:  # Ghost
                    score_gain = 200 if self.player.has_double_points(current_time) else 100
                
                # Apply combo bonus
                if self.combo_count > 1:
                    combo_multiplier = 1 + (self.combo_count - 1) * 0.1
                    score_gain = int(score_gain * combo_multiplier)
                
                self.player.score += score_gain
                
                # Create damage number
                self.visual_effects.create_damage_number(
                    target_screen_x,
                    target_screen_y,
                    score_gain
                )
            
            # Create fire hit effects
            self.visual_effects.create_hit_particles(
                target_screen_x,
                target_screen_y,
                (255, 140, 0)  # Orange fire color
            )
            
            # Add extra fire particles for more impact
            for _ in range(10):
                self.visual_effects.create_hit_particles(
                    target_screen_x,
                    target_screen_y,
                    (255, 100, 0)  # Red-orange
                )
    
    def handle_menu_input(self, event):
        """Handle input in menu state."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.menu_selection = (self.menu_selection - 1) % 5
            elif event.key == pygame.K_DOWN:
                self.menu_selection = (self.menu_selection + 1) % 5
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                if self.menu_selection == 0:  # Start Game
                    self.start_new_game()
                elif self.menu_selection == 1:  # Resolution
                    resolutions = list(config.RESOLUTIONS.keys())
                    current_idx = resolutions.index(self.resolution)
                    next_idx = (current_idx + 1) % len(resolutions)
                    self.set_resolution(resolutions[next_idx])
                elif self.menu_selection == 2:  # Difficulty
                    difficulties = list(config.DIFFICULTY_SETTINGS.keys())
                    current_idx = difficulties.index(self.difficulty)
                    next_idx = (current_idx + 1) % len(difficulties)
                    self.difficulty = difficulties[next_idx]
                elif self.menu_selection == 3:  # Instructions
                    self.show_instructions = True
                    self.instruction_scroll = 0  # Reset scroll position
                elif self.menu_selection == 4:  # Quit
                    self.running = False
            elif event.key == pygame.K_ESCAPE:
                if self.show_instructions:
                    self.show_instructions = False
    
    def handle_game_input(self, keys):
        """Handle input during gameplay."""
        if not self.player or not self.player.is_alive():
            return
        
        # Movement
        dx = 0
        dy = 0
        speed = self.player.speed * 0.016  # Normalize for frame rate
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += speed
        
        if dx != 0 or dy != 0:
            self.player.move(dx, dy, self.dungeon_map)
    
    def handle_pause_input(self, event):
        """Handle input in pause state."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.pause_selection = (self.pause_selection - 1) % 3
            elif event.key == pygame.K_DOWN:
                self.pause_selection = (self.pause_selection + 1) % 3
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                if self.pause_selection == 0:  # Resume
                    self.state = config.STATE_PLAYING
                elif self.pause_selection == 1:  # Main Menu
                    self.state = config.STATE_MENU
                    self.menu_selection = 0
                elif self.pause_selection == 2:  # Quit
                    self.running = False
            elif event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                self.state = config.STATE_PLAYING
    
    def update_game(self):
        """Update game logic."""
        if not self.player or self.state != config.STATE_PLAYING:
            return
        
        current_time = pygame.time.get_ticks()
        
        # Check if combo has timed out
        if current_time - self.last_kill_time > self.combo_timeout and self.combo_count > 0:
            self.combo_count = 0
        
        # Update player power-ups
        self.player.update_power_ups(current_time)
        
        # Discover tiles around player (increased radius with vision boost)
        vision_radius = 6 if self.player.has_vision_boost(current_time) else 4
        self._discover_area(self.player.x, self.player.y, radius=vision_radius)
        
        # Update visual effects
        self.visual_effects.update()
        
        # Update ghosts
        for ghost in self.ghosts[:]:
            if ghost.is_alive():
                ghost.update(self.player, self.dungeon_map, current_time)
        
        # Update bears
        for bear in self.bears[:]:
            if bear.is_alive():
                bear.update(self.player, self.dungeon_map, current_time)
        
        # Update rabbits
        for rabbit in self.rabbits[:]:
            if rabbit.is_alive():
                rabbit.update(self.player, self.dungeon_map, current_time)
        
        # Update skeletons
        for skeleton in self.skeletons[:]:
            if skeleton.is_alive():
                skeleton.update(self.player, self.dungeon_map, current_time)
        
        # Update wizards
        for wizard in self.wizards[:]:
            if wizard.is_alive():
                wizard.update(self.player, self.dungeon_map, current_time)
                # Collect wizard blasts
                for blast in wizard.blasts:
                    if blast not in self.wizard_blasts:
                        self.wizard_blasts.append(blast)
                wizard.blasts = []
        
        # Update wizard blasts and check for player collision
        for blast in self.wizard_blasts[:]:
            if blast.update(self.dungeon_map):
                # Hit wall
                self.wizard_blasts.remove(blast)
            else:
                # Check if hit player
                player_rect = self.player.get_rect()
                blast_rect = blast.get_rect()
                if player_rect.colliderect(blast_rect):
                    self.player.take_damage(config.WIZARD_DAMAGE, current_time)
                    self.wizard_blasts.remove(blast)
        
        # Update items with velocity (flung from skeleton deaths)
        for item in self.items:
            if hasattr(item, 'update'):
                item.update()
        
        # Check item collection (includes coins, treasures, weapons, bows, power-ups)
        player_rect = self.player.get_rect()
        for item in self.items[:]:
            item_rect = item.get_rect()
            if player_rect.colliderect(item_rect):
                # Handle different item types
                if item.item_type == "coin":
                    self.player.collect_coin()
                    # Track open room item collection
                    if hasattr(item, 'is_open_room_item') and item.is_open_room_item:
                        self.open_room_items_collected += 1
                    # Create sparkle effect
                    self.visual_effects.create_collection_sparkles(
                        item.x * config.TILE_SIZE + config.TILE_SIZE // 2,
                        item.y * config.TILE_SIZE + config.TILE_SIZE // 2,
                        config.YELLOW
                    )
                elif item.item_type == "treasure":
                    self.player.collect_treasure()
                    # Track open room item collection
                    if hasattr(item, 'is_open_room_item') and item.is_open_room_item:
                        self.open_room_items_collected += 1
                    # Create sparkle effect
                    self.visual_effects.create_collection_sparkles(
                        item.x * config.TILE_SIZE + config.TILE_SIZE // 2,
                        item.y * config.TILE_SIZE + config.TILE_SIZE // 2,
                        config.GOLD
                    )
                elif item.item_type == "weapon":
                    self.player.collect_weapon()
                    # Create sparkle effect
                    self.visual_effects.create_collection_sparkles(
                        item.x * config.TILE_SIZE + config.TILE_SIZE // 2,
                        item.y * config.TILE_SIZE + config.TILE_SIZE // 2,
                        config.RED
                    )
                elif item.item_type == "bow":
                    self.player.collect_bow()
                    # Create bright sparkle effect around player
                    player_center_x = self.player.x * config.TILE_SIZE + config.TILE_SIZE // 2
                    player_center_y = self.player.y * config.TILE_SIZE + config.TILE_SIZE // 2
                    self.visual_effects.create_bow_pickup_effect(player_center_x, player_center_y)
                elif item.item_type == "arrow":
                    self.player.collect_arrow()
                    # Create sparkle effect
                    self.visual_effects.create_collection_sparkles(
                        item.x * config.TILE_SIZE + config.TILE_SIZE // 2,
                        item.y * config.TILE_SIZE + config.TILE_SIZE // 2,
                        config.ARROW_COLOR
                    )
                elif item.item_type == "heart":
                    self.player.collect_heart()
                    # Create sparkle effect with heart color
                    self.visual_effects.create_collection_sparkles(
                        item.x * config.TILE_SIZE + config.TILE_SIZE // 2,
                        item.y * config.TILE_SIZE + config.TILE_SIZE // 2,
                        config.HEART_COLOR
                    )
                elif item.item_type == "powerup":
                    # Activate power-up based on type
                    if isinstance(item, SpeedBoost):
                        self.player.activate_speed_boost(current_time)
                    elif isinstance(item, SpeedPill):
                        self.player.activate_speed_pill(current_time)
                    elif isinstance(item, Shield):
                        self.player.activate_shield(current_time)
                    elif isinstance(item, DoublePoints):
                        self.player.activate_double_points(current_time)
                    elif isinstance(item, VisionBoost):
                        self.player.activate_vision_boost(current_time)
                    # Create power-up collection effect
                    self.visual_effects.create_collection_sparkles(
                        item.x * config.TILE_SIZE + config.TILE_SIZE // 2,
                        item.y * config.TILE_SIZE + config.TILE_SIZE // 2,
                        item.color
                    )
                elif item.item_type.startswith("gem_"):
                    # Collect gem
                    self.player.score += item.value
                    self.visual_effects.create_collection_sparkles(
                        item.x * config.TILE_SIZE + config.TILE_SIZE // 2,
                        item.y * config.TILE_SIZE + config.TILE_SIZE // 2,
                        item.color
                    )
                elif item.item_type == "freeze_scroll":
                    # Activate freeze effect
                    self.player.freeze_enemies_end = current_time + config.FREEZE_SCROLL_DURATION
                    # Create blue ice wave effect from player
                    player_center_x = self.player.x * config.TILE_SIZE + config.TILE_SIZE // 2
                    player_center_y = self.player.y * config.TILE_SIZE + config.TILE_SIZE // 2
                    self.visual_effects.create_freeze_wave_effect(player_center_x, player_center_y)
                    self.visual_effects.create_collection_sparkles(
                        item.x * config.TILE_SIZE + config.TILE_SIZE // 2,
                        item.y * config.TILE_SIZE + config.TILE_SIZE // 2,
                        config.FREEZE_SCROLL_COLOR
                    )
                    
                    # Deal damage to all enemies within radius
                    enemies_damaged = 0
                    for enemy_list in [self.ghosts, self.bears, self.rabbits, self.skeletons, self.wizards]:
                        for enemy in enemy_list[:]:
                            if enemy.is_alive():
                                dx = enemy.x - self.player.x
                                dy = enemy.y - self.player.y
                                distance = math.sqrt(dx * dx + dy * dy)
                                if distance <= config.FREEZE_SCROLL_RADIUS:
                                    # Deal damage
                                    enemy.health -= config.FREEZE_SCROLL_DAMAGE
                                    enemies_damaged += 1
                                    
                                    # Create ice hit effect
                                    enemy_center_x = enemy.x * config.TILE_SIZE + config.TILE_SIZE // 2
                                    enemy_center_y = enemy.y * config.TILE_SIZE + config.TILE_SIZE // 2
                                    self.visual_effects.create_hit_particles(
                                        enemy_center_x,
                                        enemy_center_y,
                                        (100, 200, 255)  # Ice blue color
                                    )
                                    
                                    # Award points if enemy dies from freeze damage
                                    if enemy.health <= 0:
                                        # Update combo
                                        self._update_combo(current_time)
                                        
                                        if isinstance(enemy, MadRabbit):
                                            score_gain = 400 if self.player.has_double_points(current_time) else 200
                                        elif isinstance(enemy, CrazyBear):
                                            score_gain = 300 if self.player.has_double_points(current_time) else 150
                                        elif isinstance(enemy, ChillinSkeleton):
                                            score_gain = 300 if self.player.has_double_points(current_time) else 150
                                            # Drop loot
                                            if random.random() < config.SKELETON_GOLD_DROP_CHANCE:
                                                self.items.append(Treasure(enemy.x, enemy.y))
                                            else:
                                                self.items.append(FreezeScroll(enemy.x, enemy.y))
                                        elif isinstance(enemy, DarkWizard):
                                            score_gain = 500 if self.player.has_double_points(current_time) else 250
                                            # Drop wizard staff
                                            self.items.append(WizardStaff(enemy.x, enemy.y))
                                        else:  # Ghost
                                            score_gain = 200 if self.player.has_double_points(current_time) else 100
                                        
                                        # Apply combo bonus
                                        if self.combo_count > 1:
                                            combo_multiplier = 1 + (self.combo_count - 1) * 0.1
                                            score_gain = int(score_gain * combo_multiplier)
                                        
                                        self.player.score += score_gain
                                        
                                        # Create damage number
                                        self.visual_effects.create_damage_number(
                                            enemy_center_x,
                                            enemy_center_y,
                                            score_gain
                                        )
                elif item.item_type.startswith("artifact_"):
                    # Handle artifacts
                    if item.item_type == "artifact_max_weapons":
                        self.player.max_weapons += config.ARTIFACT_MAX_WEAPONS_BONUS
                    elif item.item_type == "artifact_max_arrows":
                        self.player.max_arrows += config.ARTIFACT_MAX_ARROWS_BONUS
                    elif item.item_type == "artifact_full_health":
                        self.player.health = self.player.max_health
                    elif item.item_type == "artifact_enemy_destroyer":
                        # Destroy all enemies within radius
                        for ghost in self.ghosts[:]:
                            dist = math.sqrt((ghost.x - self.player.x)**2 + (ghost.y - self.player.y)**2)
                            if dist <= config.ARTIFACT_ENEMY_DESTROY_RADIUS:
                                ghost.health = 0
                        for bear in self.bears[:]:
                            dist = math.sqrt((bear.x - self.player.x)**2 + (bear.y - self.player.y)**2)
                            if dist <= config.ARTIFACT_ENEMY_DESTROY_RADIUS:
                                bear.health = 0
                        for rabbit in self.rabbits[:]:
                            dist = math.sqrt((rabbit.x - self.player.x)**2 + (rabbit.y - self.player.y)**2)
                            if dist <= config.ARTIFACT_ENEMY_DESTROY_RADIUS:
                                rabbit.health = 0
                        for skeleton in self.skeletons[:]:
                            dist = math.sqrt((skeleton.x - self.player.x)**2 + (skeleton.y - self.player.y)**2)
                            if dist <= config.ARTIFACT_ENEMY_DESTROY_RADIUS:
                                skeleton.health = 0
                        for wizard in self.wizards[:]:
                            dist = math.sqrt((wizard.x - self.player.x)**2 + (wizard.y - self.player.y)**2)
                            if dist <= config.ARTIFACT_ENEMY_DESTROY_RADIUS:
                                wizard.health = 0
                    self.visual_effects.create_collection_sparkles(
                        item.x * config.TILE_SIZE + config.TILE_SIZE // 2,
                        item.y * config.TILE_SIZE + config.TILE_SIZE // 2,
                        config.ARTIFACT_COLOR
                    )
                elif item.item_type == "wizard_staff":
                    # Collect wizard staff (temporary for current level)
                    self.player.has_wizard_staff = True
                    self.player.wizard_staff_uses = config.WIZARD_STAFF_USES
                    self.visual_effects.create_collection_sparkles(
                        item.x * config.TILE_SIZE + config.TILE_SIZE // 2,
                        item.y * config.TILE_SIZE + config.TILE_SIZE // 2,
                        config.WIZARD_STAFF_COLOR
                    )
                elif item.item_type == "protection_shield":
                    # Collect protection shield (10 hits)
                    self.player.has_protection_shield = True
                    self.player.shield_hits_remaining = 10
                    self.visual_effects.create_collection_sparkles(
                        item.x * config.TILE_SIZE + config.TILE_SIZE // 2,
                        item.y * config.TILE_SIZE + config.TILE_SIZE // 2,
                        config.SHIELD_COLOR
                    )
                # Remove collected item
                self.items.remove(item)
        # Update room tracking
        new_room_index = self._get_player_room_index()
        if new_room_index is not None and new_room_index != self.current_room_index:
            # Before changing rooms, save original room if entering secret room
            if new_room_index < len(self.dungeon_map.rooms):
                new_room_is_secret = self.dungeon_map.rooms[new_room_index].is_secret
                # If entering a secret room from a non-secret room, save our origin
                if new_room_is_secret and not self.in_secret_room:
                    self.original_room_index = self.current_room_index
                
                self.current_room_index = new_room_index
                self.in_secret_room = new_room_is_secret

        # Check door interactions (with cooldown)
        if current_time - self.last_door_use_time >= 1000:  # 1 second cooldown
            for door in self.doors:
                door_rect = door.get_rect()
                if player_rect.colliderect(door_rect):
                    if door.door_type == "teleport":
                        # Teleport to linked door position
                        if hasattr(door, 'target_x') and hasattr(door, 'target_y'):
                            self._start_door_transition(door.target_x, door.target_y)
                            self.last_door_use_time = current_time
                            break
                    elif door.door_type == "secret":
                        # Enter secret room
                        if door.linked_secret_room_index is not None:
                            # Save current room so return door brings us back here
                            self.original_room_index = self.current_room_index
                            self._start_room_transition(door.linked_secret_room_index, is_entering_secret=True)
                            self.last_door_use_time = current_time
                            break
            
            # Check return doors in secret rooms
            if self.in_secret_room:
                for return_door in self.secret_room_return_doors:
                    door_rect = return_door.get_rect()
                    if player_rect.colliderect(door_rect):
                        # Return to main dungeon
                        self._start_room_transition(self.original_room_index, is_entering_secret=False)
                        self.last_door_use_time = current_time
                        break
        
        # Track dead enemies for respawn and remove from active lists
        for ghost in self.ghosts:
            if not ghost.is_alive():
                self.dead_enemies.append({
                    'type': 'ghost',
                    'x': ghost.x,
                    'y': ghost.y,
                    'speed': ghost.speed,
                    'death_time': current_time
                })
        for bear in self.bears:
            if not bear.is_alive():
                self.dead_enemies.append({
                    'type': 'bear',
                    'x': bear.x,
                    'y': bear.y,
                    'speed': bear.speed,
                    'death_time': current_time
                })
        for rabbit in self.rabbits:
            if not rabbit.is_alive():
                self.dead_enemies.append({
                    'type': 'rabbit',
                    'x': rabbit.x,
                    'y': rabbit.y,
                    'speed': rabbit.speed,
                    'death_time': current_time
                })
        for skeleton in self.skeletons:
            if not skeleton.is_alive():
                # Skeletons respawn after 10 seconds
                self.dead_enemies.append({
                    'type': 'skeleton',
                    'x': skeleton.x,
                    'y': skeleton.y,
                    'death_time': current_time
                })
        for wizard in self.wizards:
            if not wizard.is_alive():
                # Wizards respawn after 10 seconds
                self.dead_enemies.append({
                    'type': 'wizard',
                    'x': wizard.x,
                    'y': wizard.y,
                    'death_time': current_time
                })
        
        self.ghosts = [g for g in self.ghosts if g.is_alive()]
        self.bears = [b for b in self.bears if b.is_alive()]
        self.rabbits = [r for r in self.rabbits if r.is_alive()]
        self.skeletons = [s for s in self.skeletons if s.is_alive()]
        self.wizards = [w for w in self.wizards if w.is_alive()]
        
        # Respawn dead enemies (5 seconds for ghosts/bears, 30 seconds for rabbits, 10 seconds for skeletons/wizards)
        enemies_to_respawn = []
        for enemy_data in self.dead_enemies[:]:
            if enemy_data['type'] == 'rabbit':
                respawn_time = config.RABBIT_RESPAWN_TIME
            elif enemy_data['type'] in ['skeleton', 'wizard']:
                respawn_time = 10000  # 10 seconds for skeletons and wizards
            else:
                respawn_time = 5000  # 5 seconds for ghosts and bears
            
            if current_time - enemy_data['death_time'] >= respawn_time:
                if enemy_data['type'] == 'ghost':
                    self.ghosts.append(Ghost(enemy_data['x'], enemy_data['y'], enemy_data['speed']))
                elif enemy_data['type'] == 'bear':
                    self.bears.append(CrazyBear(enemy_data['x'], enemy_data['y'], enemy_data['speed']))
                elif enemy_data['type'] == 'rabbit':
                    self.rabbits.append(MadRabbit(enemy_data['x'], enemy_data['y'], enemy_data['speed']))
                elif enemy_data['type'] == 'skeleton':
                    self.skeletons.append(ChillinSkeleton(enemy_data['x'], enemy_data['y']))
                elif enemy_data['type'] == 'wizard':
                    self.wizards.append(DarkWizard(enemy_data['x'], enemy_data['y']))
                enemies_to_respawn.append(enemy_data)
        
        # Remove respawned enemies from dead list
        for enemy_data in enemies_to_respawn:
            self.dead_enemies.remove(enemy_data)
        
        # Check exit condition - requires collecting 90% of open room items
        if self.exit:
            exit_rect = self.exit.get_rect()
            if player_rect.colliderect(exit_rect):
                # Calculate required items (90% of open room items)
                required_items = int(self.open_room_items * 0.90)
                
                if self.open_room_items_collected >= required_items:
                    # Can exit - calculate and award level completion bonus
                    self.level_completion_bonus = self._calculate_level_bonus()
                    self.player.score += self.level_completion_bonus
                    self.state = config.STATE_LEVEL_COMPLETE
                else:
                    # Not enough items collected - show message
                    if current_time - self.exit_requirement_message_time > 2000:  # Show message every 2 seconds
                        self.exit_requirement_message_time = current_time
                        # Message will be displayed by UI
        
        # Check game over
        if not self.player.is_alive():
            self.state = config.STATE_GAME_OVER
        
        # Update camera
        self.update_camera()
    
    def update_camera(self):
        """Update camera to follow player."""
        if not self.player:
            return
        
        # Center camera on player
        target_x = int(self.player.x * config.TILE_SIZE - self.screen_width // 2)
        target_y = int(self.player.y * config.TILE_SIZE - (self.screen_height - self.ui.ui_height) // 2)
        
        # Clamp camera to map bounds
        max_x = self.dungeon_map.width * config.TILE_SIZE - self.screen_width
        max_y = self.dungeon_map.height * config.TILE_SIZE - (self.screen_height - self.ui.ui_height)
        
        self.camera_x = max(0, min(target_x, max_x))
        self.camera_y = max(0, min(target_y, max_y))
    
    def update_transition(self):
        """Handle transition state with fade effect."""
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.transition_start_time
        
        # Wait for half the transition duration, then teleport
        if elapsed >= config.TRANSITION_FADE_DURATION // 2:
            # Complete the transition (door or room)
            if hasattr(self, 'transition_target_room') and self.transition_target_room is not None:
                self._complete_room_transition()
            else:
                self._complete_door_transition()
            
            # Check if full transition is complete
            if elapsed >= config.TRANSITION_FADE_DURATION:
                self.state = config.STATE_PLAYING
                self.transition_target_room = None
    
    def draw_game(self):
        """Draw the game world with visual effects."""
        self.screen.fill(config.BLACK)
        
        if not self.dungeon_map:
            return
        
        # Get screen shake offset
        shake_x, shake_y = self.visual_effects.get_shake_offset()
        
        # Calculate visible tile range
        start_x = max(0, self.camera_x // config.TILE_SIZE)
        end_x = min(self.dungeon_map.width, (self.camera_x + self.screen_width) // config.TILE_SIZE + 1)
        start_y = max(0, self.camera_y // config.TILE_SIZE)
        end_y = min(self.dungeon_map.height, (self.camera_y + self.screen_height) // config.TILE_SIZE + 1)
        
        # Draw tiles
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                screen_x = x * config.TILE_SIZE - self.camera_x
                screen_y = y * config.TILE_SIZE - self.camera_y + self.ui.ui_height
                
                if self.dungeon_map.tiles[y][x] == 1:  # Floor
                    # Stone floor with variation
                    base_color = config.FLOOR_COLOR
                    variation = ((x * 7 + y * 13) % 20) - 10
                    floor_color = tuple(max(0, min(255, c + variation)) for c in base_color)
                    pygame.draw.rect(self.screen, floor_color,
                                   (screen_x, screen_y, config.TILE_SIZE, config.TILE_SIZE))
                    
                    # Add floor cracks/details
                    if (x + y) % 5 == 0:
                        crack_color = tuple(max(0, c - 15) for c in floor_color)
                        pygame.draw.line(self.screen, crack_color,
                                       (screen_x + 5, screen_y + 5),
                                       (screen_x + config.TILE_SIZE - 5, screen_y + config.TILE_SIZE - 5), 1)
                    
                    # Border between tiles
                    pygame.draw.rect(self.screen, config.DARK_GRAY,
                                   (screen_x, screen_y, config.TILE_SIZE, config.TILE_SIZE), 1)
                else:  # Wall
                    # Draw stone wall with depth
                    pygame.draw.rect(self.screen, config.WALL_COLOR,
                                   (screen_x, screen_y, config.TILE_SIZE, config.TILE_SIZE))
                    
                    # Add stone brick lines
                    brick_offset = (x % 2) * (config.TILE_SIZE // 2)
                    pygame.draw.line(self.screen, config.WALL_BORDER,
                                   (screen_x + brick_offset, screen_y),
                                   (screen_x + brick_offset, screen_y + config.TILE_SIZE), 1)
                    pygame.draw.line(self.screen, config.WALL_BORDER,
                                   (screen_x, screen_y + config.TILE_SIZE // 2),
                                   (screen_x + config.TILE_SIZE, screen_y + config.TILE_SIZE // 2), 1)
                    
                    # Add shadow/depth effect
                    shadow_color = config.WALL_BORDER
                    pygame.draw.rect(self.screen, shadow_color,
                                   (screen_x, screen_y, config.TILE_SIZE, config.TILE_SIZE), 2)
                    
                    # Highlight top-left corner for 3D effect
                    highlight = tuple(min(255, c + 20) for c in config.WALL_COLOR)
                    pygame.draw.line(self.screen, highlight,
                                   (screen_x + 1, screen_y + 1),
                                   (screen_x + config.TILE_SIZE - 1, screen_y + 1), 1)
                    pygame.draw.line(self.screen, highlight,
                                   (screen_x + 1, screen_y + 1),
                                   (screen_x + 1, screen_y + config.TILE_SIZE - 1), 1)
        
        # Draw decorative torches on walls
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                if self.dungeon_map.tiles[y][x] == 0:  # Wall
                    # Check if there's a floor tile adjacent (good place for torch)
                    has_floor_adjacent = False
                    if x > 0 and self.dungeon_map.tiles[y][x-1] == 1:
                        has_floor_adjacent = True
                    if x < self.dungeon_map.width - 1 and self.dungeon_map.tiles[y][x+1] == 1:
                        has_floor_adjacent = True
                    if y > 0 and self.dungeon_map.tiles[y-1][x] == 1:
                        has_floor_adjacent = True
                    
                    # Randomly place torches
                    if has_floor_adjacent and (x * 17 + y * 23) % 37 == 0:
                        screen_x = x * config.TILE_SIZE - self.camera_x
                        screen_y = y * config.TILE_SIZE - self.camera_y + self.ui.ui_height
                        
                        # Draw torch
                        torch_x = screen_x + config.TILE_SIZE // 2
                        torch_y = screen_y + config.TILE_SIZE // 2
                        
                        # Flame flicker
                        flicker = abs(math.sin(pygame.time.get_ticks() * 0.01 + x + y)) * 3
                        flame_size = 4 + int(flicker)
                        
                        # Torch stick
                        pygame.draw.rect(self.screen, (80, 50, 20),
                                       (torch_x - 2, torch_y, 4, 8))
                        # Flame
                        pygame.draw.circle(self.screen, (255, 150, 0),
                                         (torch_x, torch_y - 2), flame_size)
                        pygame.draw.circle(self.screen, (255, 200, 50),
                                         (torch_x, torch_y - 2), flame_size - 2)
        
        # Draw items (with screen shake offset applied)
        for item in self.items:
            item.draw(self.screen, self.camera_x - shake_x, self.camera_y - self.ui.ui_height - shake_y)
        
        # Draw doors
        for door in self.doors:
            door.draw(self.screen, self.camera_x - shake_x, self.camera_y - self.ui.ui_height - shake_y)
        
        # Draw return doors if in secret room
        if self.in_secret_room:
            for return_door in self.secret_room_return_doors:
                return_door.draw(self.screen, self.camera_x - shake_x, self.camera_y - self.ui.ui_height - shake_y)
        
        # Draw exit
        if self.exit:
            self.exit.draw(self.screen, self.camera_x - shake_x, self.camera_y - self.ui.ui_height - shake_y)
        
        # Draw ghosts
        for ghost in self.ghosts:
            ghost.draw(self.screen, self.camera_x - shake_x, self.camera_y - self.ui.ui_height - shake_y)
        
        # Draw bears
        for bear in self.bears:
            bear.draw(self.screen, self.camera_x - shake_x, self.camera_y - self.ui.ui_height - shake_y)
        
        # Draw rabbits
        for rabbit in self.rabbits:
            rabbit.draw(self.screen, self.camera_x - shake_x, self.camera_y - self.ui.ui_height - shake_y)
        
        # Draw skeletons
        for skeleton in self.skeletons:
            skeleton.draw(self.screen, self.camera_x - shake_x, self.camera_y - self.ui.ui_height - shake_y)
        
        # Draw wizards
        for wizard in self.wizards:
            wizard.draw(self.screen, self.camera_x - shake_x, self.camera_y - self.ui.ui_height - shake_y)
        
        # Draw wizard blasts
        for blast in self.wizard_blasts:
            blast.draw(self.screen, self.camera_x - shake_x, self.camera_y - self.ui.ui_height - shake_y)
        
        # Draw player
        if self.player:
            self.player.draw(self.screen, self.camera_x - shake_x, self.camera_y - self.ui.ui_height - shake_y)
        
        # Draw visual effects (particles, damage numbers)
        self.visual_effects.draw(self.screen, self.camera_x - shake_x, self.camera_y - self.ui.ui_height - shake_y)
        
        # Draw UI (UI not affected by screen shake)
        if self.player:
            self.ui.draw_game_ui(self.screen, self.player, self.current_level, self.total_items, self.combo_count,
                               self.open_room_items, self.open_room_items_collected)
            
            # Show exit requirement message if player tried to exit without enough items
            current_time = pygame.time.get_ticks()
            if self.exit_requirement_message_time > 0 and current_time - self.exit_requirement_message_time < 2000:
                required_items = int(self.open_room_items * 0.75)
                message = f"Need {required_items - self.open_room_items_collected} more open room items to exit!"
                message_surface = self.ui.font_medium.render(message, True, config.RED)
                message_rect = message_surface.get_rect(center=(self.screen.get_width() // 2, 
                                                                self.screen.get_height() // 2))
                # Draw background for message
                bg_rect = message_rect.inflate(20, 10)
                pygame.draw.rect(self.screen, (0, 0, 0, 180), bg_rect)
                pygame.draw.rect(self.screen, config.RED, bg_rect, 2)
                self.screen.blit(message_surface, message_rect)
            
            # Draw minimap
            self.ui.draw_minimap(self.screen, self.dungeon_map, self.player, 
                               self.ghosts, self.bears, self.rabbits, self.skeletons, self.wizards,
                               self.dungeon_map.exit_pos, self.discovered_tiles)
            # Draw active power-ups status
            self.ui.draw_powerup_status(self.screen, self.player, pygame.time.get_ticks())
    
    def draw_transition_fade(self):
        """Draw dark fade transition effect."""
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.transition_start_time
        
        # Calculate fade alpha (0-255)
        # Fade to black in first half, fade from black in second half
        half_duration = config.TRANSITION_FADE_DURATION // 2
        if elapsed < half_duration:
            # Fading to black
            alpha = int((elapsed / half_duration) * 255)
        else:
            # Fading from black
            alpha = int(((config.TRANSITION_FADE_DURATION - elapsed) / half_duration) * 255)
        
        # Create dark overlay
        fade_surface = pygame.Surface((self.screen_width, self.screen_height))
        fade_surface.fill((0, 0, 0))
        fade_surface.set_alpha(alpha)
        self.screen.blit(fade_surface, (0, 0))
    
    def run(self):
        """Main game loop."""
        while self.running:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                if self.state == config.STATE_MENU:
                    if not self.show_instructions:
                        self.handle_menu_input(event)
                    else:
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_ESCAPE:
                                self.show_instructions = False
                            elif event.key == pygame.K_UP or event.key == pygame.K_w:
                                self.instruction_scroll = max(0, self.instruction_scroll - 30)
                            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                                self.instruction_scroll = min(self.ui.get_max_instruction_scroll(), 
                                                             self.instruction_scroll + 30)
                        elif event.type == pygame.MOUSEWHEEL:
                            self.instruction_scroll = max(0, min(self.ui.get_max_instruction_scroll(),
                                                                self.instruction_scroll - event.y * 20))
                
                elif self.state == config.STATE_PLAYING:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                            self.state = config.STATE_PAUSED
                            self.pause_selection = 0
                        # Sword attack (SPACE key) - consumes one sword
                        elif event.key == pygame.K_SPACE:
                            self._handle_sword_attack()
                        # Bow attack (B key) - consumes one bow
                        elif event.key == pygame.K_b:
                            self._handle_bow_attack()
                        # Wizard staff fireball (Z key)
                        elif event.key == pygame.K_z:
                            self._handle_fireball_attack()
                        # Wizard staff fireball (Z key)
                        elif event.key == pygame.K_z:
                            self._handle_fireball_attack()
                
                elif self.state == config.STATE_PAUSED:
                    self.handle_pause_input(event)
                
                elif self.state == config.STATE_LEVEL_COMPLETE:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                        self.current_level += 1
                        self.start_level()
                
                elif self.state == config.STATE_GAME_OVER:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                        self.state = config.STATE_MENU
                        self.menu_selection = 0
            
            # Game update
            if self.state == config.STATE_PLAYING:
                keys = pygame.key.get_pressed()
                self.handle_game_input(keys)
                self.update_game()
            elif self.state == config.STATE_TRANSITION:
                self.update_transition()
            
            # Rendering
            if self.state == config.STATE_MENU:
                if self.show_instructions:
                    self.ui.draw_instructions(self.screen, self.instruction_scroll)
                else:
                    self.ui.draw_menu(self.screen, self.menu_selection, 
                                     self.resolution, self.difficulty)
            
            elif self.state == config.STATE_PLAYING:
                self.draw_game()
            
            elif self.state == config.STATE_TRANSITION:
                # Draw the game underneath
                self.draw_game()
                # Draw fade overlay
                self.draw_transition_fade()
            
            elif self.state == config.STATE_PAUSED:
                self.draw_game()
                self.ui.draw_pause_menu(self.screen, self.pause_selection)
            
            elif self.state == config.STATE_LEVEL_COMPLETE:
                self.draw_game()
                self.ui.draw_level_complete(self.screen, self.player, self.current_level)
            
            elif self.state == config.STATE_GAME_OVER:
                self.ui.draw_game_over(self.screen, self.player, self.current_level)
            
            # Update display
            pygame.display.flip()
            self.clock.tick(config.FPS)
        
        pygame.quit()
        sys.exit()


def main():
    """Entry point for the game."""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
