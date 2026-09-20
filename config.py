"""
Game configuration and constants for Dungeon Crawler.
"""

import pygame

# Window settings
RESOLUTIONS = {
    "small": (800, 600),
    "medium": (1024, 768),
    "large": (1280, 960),
    "xlarge": (1600, 1200)
}
DEFAULT_RESOLUTION = "medium"
FPS = 60

# Tile size
TILE_SIZE = 40

# Colors (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
LIGHT_GRAY = (192, 192, 192)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GOLD = (255, 215, 0)  # For treasure sparkles
BROWN = (139, 69, 19)  # For bear effects

# Wall colors
WALL_COLOR = (100, 100, 150)
WALL_BORDER = (80, 80, 120)

# Floor colors
FLOOR_COLOR = (50, 50, 50)
FLOOR_HIGHLIGHT = (70, 70, 70)

# Entity colors
PLAYER_COLOR = (0, 200, 255)
GHOST_COLOR = (255, 100, 100)
GHOST_ANGRY_COLOR = (255, 0, 0)

# Item colors
COIN_COLOR = (255, 215, 0)
TREASURE_COLOR = (255, 165, 0)
WEAPON_COLOR = (200, 200, 255)
BOW_COLOR = (139, 69, 19)
ARROW_COLOR = (160, 82, 45)
HEART_COLOR = (255, 50, 100)  # Pink/red heart for health
DOOR_COLOR = (150, 75, 0)
SECRET_DOOR_COLOR = (100, 100, 100)
EXIT_COLOR = (0, 255, 0)

# New item colors
GEM_RUBY_COLOR = (220, 20, 60)  # Deep red
GEM_EMERALD_COLOR = (0, 201, 87)  # Bright green
GEM_SAPPHIRE_COLOR = (15, 82, 186)  # Deep blue
FREEZE_SCROLL_COLOR = (173, 216, 230)  # Light blue
ARTIFACT_COLOR = (255, 215, 0)  # Gold
WIZARD_STAFF_COLOR = (138, 43, 226)  # Purple

# Power-up colors
SPEED_BOOST_COLOR = (255, 255, 0)
SPEED_PILL_COLOR = (255, 140, 0)  # Bright orange for speed pill
SHIELD_COLOR = (100, 200, 255)
DOUBLE_POINTS_COLOR = (255, 100, 255)
VISION_BOOST_COLOR = (150, 255, 150)

# Crazy Bear colors
BEAR_COLOR = (139, 69, 19)
BEAR_ACCENT = (210, 180, 140)

# Mad Rabbit colors
RABBIT_COLOR = (255, 100, 200)  # Bright pink/magenta
RABBIT_DAMAGED_COLOR = (200, 120, 160)  # Faded pink
RABBIT_DYING_COLOR = (150, 140, 145)  # Almost grey
PINK = (255, 192, 203)  # For inner ears and nose

# Skeleton colors
SKELETON_COLOR = (200, 200, 200)  # Light grey
SKELETON_BONE_COLOR = (240, 240, 240)  # Almost white

# Dark Wizard colors
WIZARD_COLOR = (75, 0, 130)  # Indigo
WIZARD_ROBE_COLOR = (138, 43, 226)  # Purple
WIZARD_BLAST_COLOR = (255, 0, 255)  # Magenta

# UI colors
UI_BG = (40, 40, 40)
UI_TEXT = (255, 255, 255)
UI_HIGHLIGHT = (100, 200, 100)
HEALTH_COLOR = (255, 0, 0)
ENERGY_COLOR = (0, 150, 255)

# Minimap settings
MINIMAP_SIZE = 150
MINIMAP_MARGIN = 10
MINIMAP_BG = (20, 20, 20)
MINIMAP_WALL = (80, 80, 100)
MINIMAP_FLOOR = (40, 40, 40)
MINIMAP_PLAYER = (0, 200, 255)
MINIMAP_GHOST = (255, 100, 100)
MINIMAP_BEAR = (160, 100, 50)
MINIMAP_RABBIT = (255, 100, 200)
MINIMAP_EXIT = (0, 255, 0)

# Game difficulty settings
DIFFICULTY_SETTINGS = {
    "easy": {
        "ghost_speed": 1.5,
        "ghost_count": 2,
        "bear_count": 1,
        "player_health": 100,
        "item_spawn_rate": 0.15,
        "treasure_spawn_rate": 0.10,
        "weapon_spawn_rate": 0.08,
        "bow_count": 2,
        "powerup_count": 4  # More power-ups on easy
    },
    "medium": {
        "ghost_speed": 2.0,
        "ghost_count": 3,
        "bear_count": 1,
        "player_health": 75,
        "item_spawn_rate": 0.12,
        "treasure_spawn_rate": 0.08,
        "weapon_spawn_rate": 0.06,
        "bow_count": 1,
        "powerup_count": 3  # Balanced power-ups
    },
    "hard": {
        "ghost_speed": 2.5,
        "ghost_count": 3,
        "bear_count": 2,
        "player_health": 50,
        "item_spawn_rate": 0.10,
        "treasure_spawn_rate": 0.06,
        "weapon_spawn_rate": 0.04,
        "bow_count": 1,
        "powerup_count": 2  # Fewer power-ups on hard
    }
}
DEFAULT_DIFFICULTY = "medium"

# Map generation
MAP_WIDTH = 50
MAP_HEIGHT = 35
ROOM_MIN_SIZE = 5
ROOM_MAX_SIZE = 12
MAX_ROOMS = 6  # Try to generate ~4 open rooms + 2 secret rooms
SECRET_ROOM_CHANCE = 0.33  # Chance for secret rooms (aim for 2 per level)
NUM_TELEPORT_DOORS = 3  # Purple doors (hidden hallway shortcuts)
NUM_SECRET_ROOMS = 2  # Grey door entrances to hidden rooms

# Player settings
PLAYER_SPEED = 4
PLAYER_MAX_WEAPONS = 5  # Max swords (default)
PLAYER_MAX_ARROWS = 10  # Max arrows (default)
PLAYER_MAX_WEAPONS_LEGACY = 5  # For backwards compatibility
PLAYER_BASE_MAX_WEAPONS = 5  # Starting max weapons
PLAYER_BASE_MAX_ARROWS = 10  # Starting max arrows

# Ghost settings
GHOST_DETECTION_RANGE = 200
GHOST_ATTACK_RANGE = 30
GHOST_DAMAGE = 10
GHOST_ATTACK_COOLDOWN = 1000  # milliseconds

# Crazy Bear settings
BEAR_SPEED = 1.2
BEAR_DETECTION_RANGE = 150
BEAR_ATTACK_RANGE = 35
BEAR_DAMAGE = 15
BEAR_ATTACK_COOLDOWN = 1500  # milliseconds

# Mad Rabbit settings
RABBIT_SPEED = 1.5
RABBIT_DETECTION_RANGE = 180
RABBIT_ATTACK_RANGE = 35
RABBIT_DAMAGE = 20
RABBIT_ATTACK_COOLDOWN = 1200  # milliseconds
RABBIT_RESPAWN_TIME = 30000  # 30 seconds in milliseconds

# Skeleton settings
SKELETON_SPEED = 0.8
SKELETON_DETECTION_RANGE = 200
SKELETON_ATTACK_RANGE = 35
SKELETON_DAMAGE = 12
SKELETON_ATTACK_COOLDOWN = 1500  # milliseconds
SKELETON_HEALTH = 3  # Takes 3 hits to destroy
SKELETON_GOLD_DROP_CHANCE = 0.6  # 60% chance to drop gold
SKELETON_SCROLL_DROP_CHANCE = 0.4  # 40% chance to drop scroll

# Dark Wizard settings
WIZARD_SPEED = 1.0
WIZARD_DETECTION_RANGE = 250
WIZARD_ATTACK_RANGE = 200
WIZARD_DAMAGE = 15
WIZARD_ATTACK_COOLDOWN = 1000  # 1 second between shots
WIZARD_HEALTH = 5  # Takes 5 hits to destroy
WIZARD_BLAST_SPEED = 6  # Speed of projectile
WIZARD_STAFF_USES = 999  # Unlimited uses for current level

# Item values
COIN_VALUE = 10
TREASURE_VALUE = 50
WEAPON_DAMAGE = 30
HEART_HEALTH = 20  # Health recovered by heart
HEART_SPAWN_RATE = 0.03  # Sparse spawn rate for hearts

# New item values
GEM_RUBY_VALUE = 100
GEM_EMERALD_VALUE = 75
GEM_SAPPHIRE_VALUE = 50
FREEZE_SCROLL_DURATION = 5000  # 5 seconds freeze
FREEZE_SCROLL_DAMAGE = 2  # Damage dealt to enemies when activated
FREEZE_SCROLL_RADIUS = 15  # Tiles - area of effect for damage
ARTIFACT_MAX_WEAPONS_BONUS = 3  # Increases max weapons by 3
ARTIFACT_MAX_ARROWS_BONUS = 5  # Increases max arrows by 5
ARTIFACT_ENEMY_DESTROY_RADIUS = 5  # Tiles
WIZARD_STAFF_DAMAGE = 40

# Power-up settings (durations in milliseconds)
SPEED_BOOST_DURATION = 5000  # 5 seconds
SPEED_BOOST_MULTIPLIER = 1.8
SPEED_PILL_DURATION = 4000  # 4 seconds
SPEED_PILL_MULTIPLIER = 1.8
SHIELD_DURATION = 8000  # 8 seconds
DOUBLE_POINTS_DURATION = 10000  # 10 seconds
VISION_BOOST_DURATION = 7000  # 7 seconds
VISION_BOOST_RADIUS = 8  # tiles

# Power-up spawn rates (per level)
POWERUP_SPAWN_CHANCE = 0.03

# Game states
STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_PAUSED = "paused"
STATE_TRANSITION = "transition"  # Room transition with fade effect
STATE_LEVEL_COMPLETE = "level_complete"
STATE_GAME_OVER = "game_over"

# Font sizes
FONT_SMALL = 16
FONT_MEDIUM = 24
FONT_LARGE = 36
FONT_XLARGE = 48

# Visual effects settings
PARTICLE_LIFETIME = 1000  # milliseconds
SCREEN_SHAKE_DURATION = 200  # milliseconds
SCREEN_SHAKE_INTENSITY = 5  # pixels
DAMAGE_NUMBER_RISE_SPEED = 1.5  # pixels per frame
DAMAGE_NUMBER_LIFETIME = 1000  # milliseconds
TRANSITION_FADE_DURATION = 800  # milliseconds for room transition fade
