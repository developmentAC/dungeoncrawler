# Dungeon Crawler Game v0.5.7

A feature-rich graphical dungeon crawler game built with Python and Pygame. Navigate procedurally generated dungeons, collect gems and rare artifacts, fight new enemies like skeletons and wizards, freeze enemies with scrolls, and progress with accumulating scores and upgradeable capacities!

## Features

- **Progressive Scoring System**: Scores now accumulate across levels! Keep your hard-earned points as you advance through dungeons
- **Upgradeable Capacities**: Collect artifacts to permanently increase max weapon and arrow carrying capacity (transferable between levels)
- **New Collectibles**: Gems (ruby, emerald, sapphire), freeze scrolls, and rare artifacts with special powers
- **New Enemies**: Chillin' Skeletons (3 hits) and Dark Wizards (5 hits) with unique behaviors and loot drops
- **Procedural Map Generation**: Large random dungeon layouts (50x35 tiles) using binary matrices
- **Minimap System**: Upper-left corner minimap showing discovered areas, enemies, and exit (relocated for better visibility)
- **Scrollable Instructions**: Comprehensive in-game guide with detailed information about all enemies, items, and power-ups
  - Navigate with arrow keys or mouse wheel
  - Visual scroll indicators
  - Complete game mechanics explained
- **Enhanced Power-Up System**: Collect power-ups for temporary buffs:
  - **SpeedPill** (⚡): Bright orange pill with glowing effects - increases movement speed by 80% for 4 seconds
  - **Shield** (🛡️): Temporary invincibility for 8 seconds with visual shield glow
  - **Double Points** (2X): Score multiplier for 7 seconds
  - **Vision Boost** (👁️): Extended fog-of-war vision radius for 10 seconds
- **Advanced Visual Effects System**:
  - **Enhanced Item Graphics**: Bow and SpeedPill now have glowing, pulsing effects with rotating sparkles
  - **Combat Visual Feedback**: Red swirl effect when swinging sword, bright multi-ring burst when collecting bow
  - **Particle Effects**: Sparkles on item collection, hit splashes on combat
  - **Animated Arrows**: Visible arrow projectiles that fly from player to target when using bow
  - **Damage Numbers**: Floating score numbers on enemy defeats
  - **Screen Shake**: Impact feedback on successful attacks
  - **Power-Up Visual Feedback**: Active power-ups show on player (shield glow, speed lines, colored tints, glowing eyes)
  - **Status Indicators**: Real-time power-up status bars showing time remaining
- **Enhanced Graphics**: Detailed sprite-like graphics for all entities created procedurally
  - Ghosts with floating animation, glowing eyes, and wavy effects
  - Weapons rendered as rotating swords with sparkle effects
  - Bow with glowing multi-layer aura, rotating sparkles, and animated drawing motion
  - SpeedPill with bright orange glow, pulsing effects, and rotating sparkles
  - Crazy Bears - silly looking enemies with bouncing animation and crossed eyes
  - MadRabbits - purple aggressive enemies that fade to gray as they take damage
  - Coins with spinning 3D animation
  - Treasure chests with pulsing glow
  - Stone walls with brick patterns and 3D depth
  - Animated torches on dungeon walls
  - Glowing portal exit with swirling particles
- **Combat System**:
  - Melee combat with swords (close range) - red swirl visual effect on swing
  - Ranged combat with bows (5-tile range) - bright burst effect on collection
  - Multi-hit enemy system: Ghosts (1 hit), CrazyBears (2 hits), MadRabbits (3 hits)
  - Visual feedback with particles, damage numbers, and color fading on damaged enemies
  - Screen shake on impact
  - Double points power-up multiplies combat scores
  - Safety checks prevent crashes when using weapons without ammunition
- **Multiple Difficulty Levels**: Easy, Medium, and Hard with different ghost counts, spawn rates, and power-up availability
- **Resolution Options**: Support for multiple screen resolutions (800x600 to 1600x1200)
- **Enemy AI**: 
  - Ghosts with detection and chase behavior (respawn after 20 seconds)
  - Crazy bears with bouncing animation and silly behavior (respawn after 25 seconds)
  - MadRabbits - fast, aggressive enemies with color-fading damage system (respawn after 30 seconds)
  - **Chillin' Skeletons** - Slow but tough enemies requiring 3 hits, drop gold or freeze scrolls (no respawn)
  - **Dark Wizards** - Ranged attackers shooting magical blasts, require 5 hits, drop powerful wizard staff (no respawn)
- **Enemy Respawn System**: Defeated enemies respawn after set times (20-30 seconds depending on difficulty), maintaining challenge throughout the level
- **Collectibles**:
  - Coins (10 points each) - spinning gold coins
  - Treasures (50 points each) - glowing treasure chests
  - **Gems** (1-3 per level) - Ruby (100pts), Emerald (75pts), Sapphire (50pts) with sparkle animations
  - **Freeze Scrolls** (1-3 per level) - Freeze all enemies for 5 seconds with ice particle effects
  - **Rare Artifacts** (1-3 per level) - Permanent upgrades: max weapons +3, max arrows +5, full health, enemy destroyer
  - Swords (destroy enemies) - magical swords for melee combat (consumed per use)
  - Bow & Arrows (ranged weapon) - destroy enemies from a distance (consumed per use, enhanced with glowing effects)
  - **Wizard Staff** (dropped by Dark Wizards) - Powerful temporary weapon for current level only
  - Hearts - restore health (20 HP each, 5-6 spawned per level)
  - SpeedPill - bright orange power-up with glowing effects (2-4 per level in hidden rooms)
  - Other Power-ups - Shield, Double Points, Vision Boost (temporary buff items)
- **Open Room System**: 4 interconnected open rooms per level connected by narrow hallways (2-3 tiles wide)
  - Player spawns in open rooms (never in hidden rooms)
  - Can walk freely between open rooms via hallways
  - Contains items, enemies, and grey door entrances
- **Three-Tier Door System**: 
  - **Purple Teleport Doors** (2-3 per level): Hidden hallway shortcuts for quick travel between distant open rooms (optional fast travel)
  - **Grey Secret Doors** (2 per level): Entrances from open rooms to hidden bonus rooms (visible when nearby)
  - **Brown Return Doors** (in each hidden room): Exits from hidden rooms back to open room system
  - Smooth dark fade transitions between areas
- **Hidden Rooms**: Separate bonus areas with treasures and fewer enemies
  - Accessible only via grey doors from open rooms
  - Always contain brown exit door back to open rooms
  - Player never spawns in hidden rooms
- **Game States**: Menu, playing, paused, level complete, and game over
- **Atmospheric Dungeon**: Stone floors with cracks, brick walls with depth, and flickering torches
- **Progressive Levels**: Advance through increasingly challenging dungeons
- **Fog of War**: Only discovered areas are visible on the minimap (enhanced with Vision Boost power-up)

## Installation

This project uses `uv` for dependency management. Make sure you have `uv` installed.

```bash
# Install dependencies
uv sync

# Run the game
uv run python main.py
```

## Controls

- **Arrow Keys / WASD**: Move player (speed increased with Speed Boost power-up)
- **SPACE**: Use sword (when near an enemy) - triggers visual effects, consumes one sword
- **B**: Use bow (ranged attack - works from distance) - triggers visual effects, consumes one bow
- **Z**: Shoot fireball with wizard staff (7-tile range, double damage) - triggers fire effects
- **P / ESC**: Pause game
- **Arrow Keys**: Navigate menus
- **ENTER / SPACE**: Select menu option

## Game Objective

1. Explore the **open room system** - 4 interconnected rooms connected by hallways
2. Collect all coins and treasures in the **open rooms** (hidden room items don't count toward level completion)
3. Pick up power-ups for temporary advantages (SpeedPill for speed boost, Shield for invincibility, etc.)
4. Collect hearts to restore health when damaged (5-6 available per level)
5. Defeat or avoid ghosts, crazy bears, mad rabbits, skeletons, and wizards using swords, bows, or fireball staff
6. Note that defeated enemies respawn after set times - manage resources wisely
7. Use **purple teleport doors** (optional) to quickly travel between distant open rooms
8. Find **grey secret doors** to discover hidden bonus rooms with extra treasures and fewer enemies
9. Use **brown return doors** inside hidden rooms to exit back to the open room system
8. Use return doors (brown) inside secret rooms to exit back to main dungeon
9. Locate the green exit portal to complete the level (accessible after collecting all main dungeon items)
10. Progress through levels to achieve the highest score
11. Use the minimap (upper-left corner) to navigate and track discovered areas
12. Strategically use power-ups to maximize score and survivability

## Power-Up System

### SpeedPill (Bright Orange Sphere with Lightning Bolt)
- **Duration**: 4 seconds
- **Effect**: Increased movement speed by 80% (1.8x multiplier)
- **Visual**: Bright orange glowing sphere with rotating sparkles and black lightning bolt symbol
- **Spawning**: 2-4 SpeedPills per level, typically in secret rooms
- **Best Used**: When exploring quickly, escaping danger, or rushing to collect items

### Shield (Shield Shape - Yellow)
- **Duration**: 8 seconds
- **Effect**: Complete invincibility - blocks all damage
- **Visual**: Glowing yellow shield aura around player
- **Best Used**: When fighting multiple enemies or low on health

### Double Points (2X Text - Purple)
- **Duration**: 7 seconds
- **Effect**: All combat scores doubled (ghosts: 200, bears: 300)
- **Visual**: Purple color tint on player
- **Best Used**: Before engaging in combat for maximum score

### Vision Boost (Eye Symbol - Green)
- **Duration**: 10 seconds
- **Effect**: Extended fog-of-war radius (6 tiles instead of 4)
- **Visual**: Glowing green eyes on player
- **Best Used**: When exploring unknown areas or looking for exits

## Difficulty Levels

### Easy
- 2 ghosts (1 hit each)
- 1 crazy bear (2 hits)
- 1-2 mad rabbits (3 hits each)
- Slower enemy speed
- 100 health
- Higher item spawn rates
- 2 bows available
- **4 power-ups** per level (includes 2-4 SpeedPills)

### Medium
- 3 ghosts (1 hit each)
- 1 crazy bear (2 hits)
- 2-3 mad rabbits (3 hits each)
- Medium enemy speed
- 75 health
- Balanced item spawn rates
- 1 bow available
- **3 power-ups** per level (includes 2-4 SpeedPills)

### Hard
- 3 ghosts (1 hit each)
- 2 crazy bears (2 hits each)
- 3 mad rabbits (3 hits each)
- Faster enemy speed
- 50 health
- Lower item spawn rates
- 1 bow available
- **2 power-ups** per level (includes 2-4 SpeedPills)

## Collectible Items

### Coins
- **Appearance**: Spinning 3D gold coins with metallic shine
- **Points**: +10 per coin
- **Purpose**: Required to unlock the exit portal
- **Effect**: Collected automatically on contact with sparkle particle effect
- **Availability**: Scattered throughout main dungeon and secret rooms

### Treasures
- **Appearance**: Wooden chests with golden locks and pulsing glow
- **Points**: +50 per treasure
- **Purpose**: Required to unlock the exit portal (high-value collectible)
- **Effect**: Collected automatically on contact with sparkle particle effect
- **Availability**: Fewer than coins, found in both main dungeon and secret rooms

### Swords (Weapons)
- **Appearance**: Rotating magical swords with silver blades, golden crossguards, and sparkle effects
- **Points**: No point value
- **Purpose**: Melee combat weapon for destroying enemies at close range
- **Usage**: Press SPACE when near an enemy - consumes one sword per swing
- **Effect**: Destroys ghosts (+100 points, +200 with Double Points) and crazy bears (+150 points, +300 with Double Points)
- **Availability**: Scattered throughout dungeons; use strategically as each swing consumes one sword
- **Limit**: Maximum 5 swords can be carried at once

### Bow (Weapon Enabler)
- **Appearance**: Wooden bow with drawn arrow, glowing multi-layer aura, and rotating sparkles
- **Points**: No point value
- **Purpose**: One-time collectible that enables the use of arrows
- **Usage**: Collected automatically; only 1 bow spawns per level
- **Effect**: Unlocks ability to shoot arrows at enemies; triggers bright multi-ring burst visual effect on collection
- **Visual Effects**: 5 layers of pulsing glow, 4 rotating sparkles, floating animation
- **Availability**: One bow per level - essential for ranged combat
- **Note**: Must collect bow before arrows can be used

### Arrows (Ranged Ammunition)
- **Appearance**: Arrow with brown shaft, silver tip, and red feathers; floats with animation
- **Points**: No point value
- **Purpose**: Ammunition for bow weapon - ranged combat from distance (5-tile range)
- **Usage**: Press B to shoot - consumes one arrow per shot (requires bow to be collected first)
- **Effect**: Destroys ghosts (+100 points, +200 with Double Points) and crazy bears (+150 points, +300 with Double Points) from safety
- **Availability**: Spawns at half the rate of swords; collect to build ammunition supply
- **Limit**: Maximum 10 arrows can be carried at once
- **Advantage**: Attack enemies without getting close, avoiding damage

### Hearts
- **Appearance**: Pink/red pulsing hearts with floating animation
- **Points**: No point value
- **Purpose**: Health restoration when damaged by enemies
- **Effect**: Restores 20 HP when collected (health capped at maximum)
- **Availability**: Sparse - only 5-6 hearts spawn per level
- **Strategy**: Conserve for emergencies; cannot heal beyond maximum health

### Power-Ups
Power-ups provide temporary buffs with visual indicators. See the "Power-Up System" section above for detailed descriptions of:
- **SpeedPill** (⚡ Orange Sphere - Bright Orange): Increased movement speed by 80% for 4 seconds (2-4 per level)
- **Shield** (🛡️ Shield - Yellow): Invincibility for 8 seconds
- **Double Points** (2X - Purple): Score multiplier for 7 seconds
- **Vision Boost** (👁️ Eye - Green): Extended vision radius for 10 seconds

### Gems (NEW in v0.5.0)
Animated collectibles with diamond shapes and rotating sparkles (1-3 per level):
- **Ruby Gem** (💎 Deep Red): 100 points - highest value gem
- **Emerald Gem** (💎 Bright Green): 75 points - medium value gem
- **Sapphire Gem** (💎 Deep Blue): 50 points - entry-level gem
- **Animation**: All gems float, rotate, and display 4 sparkles orbiting around them
- **Purpose**: High-value collectibles that boost your score

### Freeze Scrolls (NEW in v0.5.0)
- **Appearance**: Parchment scroll with ice crystal symbol and orbiting ice particles
- **Effect**: Freezes ALL enemies for 5 seconds - they cannot move or attack
- **Spawning**: 1-3 scrolls per level
- **Strategy**: Use when surrounded by enemies or planning to collect items in dangerous areas
- **Visual**: Light blue scroll with animated frost particles

### Rare Artifacts (NEW in v0.5.0)
Glowing star-shaped items with pulsing auras (1-3 per level). Effects are PERMANENT and transfer between levels:
- **Artifact of Weapon Mastery** (⭐ Gold): Increases max sword capacity by +3 (keeps forever!)
- **Artifact of Archery** (⭐ Gold): Increases max arrow capacity by +5 (keeps forever!)
- **Artifact of Vitality** (⭐ Gold): Instantly restores full health
- **Artifact of Destruction** (⭐ Gold): Destroys all enemies within 5-tile radius
- **Animation**: 8-pointed rotating star with glowing aura and sparkle effects
- **Strategy**: Capacity upgrades are permanent investments for the entire game

### Wizard Staff (NEW in v0.5.0, ENHANCED in v0.5.3)
- **Appearance**: Magical staff with purple orb and sparkles
- **Source**: Dropped by Dark Wizards when defeated
- **Attack**: Press **Z** to shoot fireballs at enemies
- **Fireball Power**: Deals double damage (2 hits worth) - can one-shot Ghosts, Bears, Rabbits
- **Range**: 7 tiles (longer than bow's 5 tiles)
- **Visual Effects**: Spectacular fire trail with orange/red flame particles
- **Duration**: Only for current level - resets when advancing to next level
- **Uses**: Unlimited fireballs during the level
- **Strategy**: Powerful temporary weapon for taking down tough enemies quickly

## Game Elements

### Visual Details
- **Player**: Blue adventurer with head, body, and weapon indicators (sword on right, bow on left)
- **Ghosts**: Floating specters with animated movement, glowing eyes that turn yellow when angry, wavy ethereal bodies (1 hit to destroy)
- **Crazy Bears**: Brown silly bears with bouncing animation, crossed spinning eyes, goofy tongue, and waving paws (2 hits to destroy)
- **MadRabbits**: Purple aggressive enemies with color-fading system (purple → damaged gray → dying gray) as they take hits (3 hits to destroy)
- **Chillin' Skeletons** (NEW): White bone warriors with glowing red eyes, visible skull cracks as they take damage (3 hits to destroy)
- **Dark Wizards** (NEW): Floating purple-robed spellcasters with glowing magenta eyes, shoot projectile attacks (5 hits to destroy), 1.5x larger size for better visibility
- **Walls**: Stone brick walls with 3D depth, highlights, and shadows
- **Floors**: Varied stone tiles with cracks and weathering
- **Torches**: Flickering flames on dungeon walls providing ambient lighting
- **Doors**: 
  - **Purple teleport doors** with mystical glow and sparkle (hidden hallway shortcuts between distant open rooms)
  - **Grey secret doors** with shimmer effect (entrances from open rooms to hidden rooms)
  - **Brown return doors** with wooden texture (exits from hidden rooms back to open rooms)
  - All use dark fade transition effect
- **Exit**: Swirling green portal with particles and pulsing glow effect (accessible after collecting all main dungeon items)
- **Minimap**: Upper-left corner showing discovered areas with player (cyan), ghosts (red), bears (brown), rabbits (purple), and exit (green)
- **Particles**: Colorful sparkles on item collection, hit splashes in combat, door entry effects, glowing auras on enhanced items
- **Damage Numbers**: Yellow floating numbers showing score gains
- **Visual Effects**: Red swirl on sword swings, bright multi-ring burst on bow collection, glowing sparkles on SpeedPill and Bow

### Colors and Effects
- **Blue**: Player character
- **Red/Dark Red**: Ghosts (turns bright red with yellow eyes when chasing)
- **Brown**: Crazy bears with tan belly and silly appearance
- **Purple**: MadRabbits (fades to gray as they take damage)
- **Yellow**: Coins with metallic shine
- **Orange**: Treasure chests with golden accents
- **Silver/Blue**: Magical swords
- **Brown/Gray**: Bow and arrows (bow enhanced with glowing purple aura and sparkles)
- **Pink/Red**: Hearts for health recovery
- **Brown**: Wooden doors
- **Gray**: Secret doors (visible on floor)
- **Green**: Exit portal (animated)
- **Stone Gray**: Dungeon walls with brick patterns
- **Dark Gray**: Floor tiles with variation
- **Orange/Yellow**: Flickering torches
- **Bright Orange**: SpeedPill power-up (orange sphere with black lightning bolt, glowing effects, rotating sparkles)
- **Yellow**: Shield power-up (shield shape)
- **Purple**: Double Points power-up (2X symbol)
- **Green**: Vision Boost power-up (eye symbol)

### Scoring
- Coins: +10 points
- Treasures: +50 points
- **Ruby Gems**: +100 points
- **Emerald Gems**: +75 points
- **Sapphire Gems**: +50 points
- Destroying ghosts (1 hit): +100 points (or +200 with Double Points power-up)
- Destroying crazy bears (2 hits): +150 points (or +300 with Double Points power-up)
- Destroying mad rabbits (3 hits): +200 points (or +400 with Double Points power-up)
- **Destroying skeletons (3 hits)**: +150 points (or +300 with Double Points power-up)
- **Destroying dark wizards (5 hits)**: +250 points (or +500 with Double Points power-up)

**NEW in v0.5.0**: Scores now accumulate across levels! Your total score carries over when advancing to the next level.

## Technical Details

### Project Structure
```
dungeoncrawler_3/
├── main.py            # Main game loop and game manager
├── config.py          # Game configuration and constants
├── dungeon_map.py     # Procedural map generation
├── entities.py        # Player, ghosts, items, and power-ups
├── ui.py             # UI rendering, menus, and power-up status display
├── visual_effects.py  # Particle system, damage numbers, screen shake
├── pyproject.toml    # Project dependencies
└── README.md         # This file
```

### Code Features
- **Well-Commented Code**: Extensive comments throughout all files for easy maintenance
- **Modular Design**: Separate files for different game systems
- **Type Hints**: Python type hints for better code clarity
- **Configuration System**: Centralized constants in config.py for easy tweaking
- **Entity System**: Object-oriented design with inheritance
- **Visual Effects Manager**: Dedicated system for particles and screen effects
- **Power-Up System**: Time-based buff system with visual feedback

### Binary Matrix Map Generation

The game uses binary matrices to represent the dungeon:
- `0` = Wall (not walkable)
- `1` = Floor (walkable)

Rooms are randomly generated and connected with corridors. Secret rooms have a 30% chance of spawning and are connected via secret doors.

### Entity System

All game entities inherit from a base `Entity` class:
- **Player**: Manages health, inventory, score, and movement
- **Ghost**: AI-controlled enemies with detection and chase behavior
- **Items**: Coins, treasures, and weapons
- **Doors**: Regular and secret doors
- **Exit**: Level completion portal

## Development

The game follows Python conventions and uses type hints where appropriate. The architecture is modular with separate concerns for:
- Game logic (main.py)
- Configuration (config.py)
- Map generation (dungeon_map.py)
- Entities (entities.py)
- UI/rendering (ui.py)

## Future Enhancements

Potential features for future versions:
- Sound effects and music
- More enemy types
- Power-ups and special abilities
- Leaderboard system
- Custom key bindings
- Additional tile types (traps, teleporters)
- Minimap display

## Requirements

- Python >= 3.9
- Pygame >= 2.5.0

## License

This project is open source and available for educational purposes.

## Credits

Developed using Python, Pygame, and UV for dependency management.
