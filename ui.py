"""
UI rendering and game state management.
"""

import pygame
from typing import Optional
import config


class UI:
    """Manages UI rendering."""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.ui_height = 60
        
        # Initialize fonts
        pygame.font.init()
        self.font_small = pygame.font.Font(None, config.FONT_SMALL)
        self.font_medium = pygame.font.Font(None, config.FONT_MEDIUM)
        self.font_large = pygame.font.Font(None, config.FONT_LARGE)
        self.font_xlarge = pygame.font.Font(None, config.FONT_XLARGE)
    
    def draw_game_ui(self, surface: pygame.Surface, player, level: int, total_items: int, combo_count: int = 0,
                    open_room_items: int = 0, open_room_items_collected: int = 0):
        """Draw the game UI (health, score, combo counter, etc.)."""
        # Draw UI background
        pygame.draw.rect(surface, config.UI_BG, (0, 0, self.screen_width, self.ui_height))
        
        # Draw health bar
        health_width = 200
        health_x = 10
        health_y = 10
        health_percent = player.health / player.max_health
        
        pygame.draw.rect(surface, config.DARK_GRAY, 
                        (health_x, health_y, health_width, 20))
        pygame.draw.rect(surface, config.HEALTH_COLOR, 
                        (health_x, health_y, int(health_width * health_percent), 20))
        pygame.draw.rect(surface, config.WHITE, 
                        (health_x, health_y, health_width, 20), 2)
        
        # Draw health text
        health_text = self.font_small.render(f"Health: {player.health}/{player.max_health}", 
                                             True, config.UI_TEXT)
        surface.blit(health_text, (health_x + 5, health_y + 2))
        
        # Draw score
        score_text = self.font_medium.render(f"Score: {player.score}", True, config.UI_TEXT)
        surface.blit(score_text, (health_x + health_width + 20, health_y))
        
        # Draw combo counter if active
        if combo_count > 1:
            combo_text = self.font_medium.render(f"{combo_count}x COMBO", True, config.GOLD)
            combo_x = health_x + health_width + 20
            combo_y = health_y + 25
            # Draw with shadow for emphasis
            shadow = self.font_medium.render(f"{combo_count}x COMBO", True, config.BLACK)
            surface.blit(shadow, (combo_x + 1, combo_y + 1))
            surface.blit(combo_text, (combo_x, combo_y))
        
        # Draw weapons and arrows
        weapon_text = self.font_medium.render(f"Swords: {player.weapons}/5", True, config.WEAPON_COLOR)
        surface.blit(weapon_text, (health_x + health_width + 200, health_y))
        
        # Show bow status and arrow count
        if player.has_bow:
            bow_status = f"Arrows: {player.arrows}/10"
            bow_color = config.BOW_COLOR
        else:
            bow_status = "No Bow"
            bow_color = (100, 100, 100)  # Gray when no bow
        bow_text = self.font_medium.render(bow_status, True, bow_color)
        surface.blit(bow_text, (health_x + health_width + 350, health_y))
        
        # Draw items collected with open room progress
        # Show open room items needed for exit (90% requirement)
        if open_room_items > 0:
            required_items = int(open_room_items * 0.90)
            if open_room_items_collected >= required_items:
                # Player has enough items - show in green
                items_color = config.GREEN
                items_text = self.font_medium.render(
                    f"Open Room: {open_room_items_collected}/{open_room_items} ✓", 
                    True, items_color)
            else:
                # Player needs more items - show in yellow
                items_color = config.COIN_COLOR
                items_text = self.font_medium.render(
                    f"Open Room: {open_room_items_collected}/{open_room_items} (need {required_items})", 
                    True, items_color)
        else:
            # Fallback to old display
            items_text = self.font_medium.render(
                f"Items: {player.coins_collected + player.treasures_collected}/{total_items}", 
                True, config.COIN_COLOR)
        surface.blit(items_text, (self.screen_width - 350, health_y))
        
        # Draw shield status if active
        if player.has_protection_shield and player.shield_hits_remaining > 0:
            shield_text = self.font_medium.render(f"Shield: {player.shield_hits_remaining}/10", True, config.SHIELD_COLOR)
            surface.blit(shield_text, (self.screen_width - 200, health_y + 25))
            # Draw shield icon
            shield_icon_x = self.screen_width - 230
            shield_icon_y = health_y + 30
            shield_points = [
                (shield_icon_x, shield_icon_y - 5),
                (shield_icon_x + 4, shield_icon_y - 3),
                (shield_icon_x + 4, shield_icon_y + 2),
                (shield_icon_x, shield_icon_y + 6),
                (shield_icon_x - 4, shield_icon_y + 2),
                (shield_icon_x - 4, shield_icon_y - 3)
            ]
            pygame.draw.polygon(surface, config.SHIELD_COLOR, shield_points)
            pygame.draw.polygon(surface, config.WHITE, shield_points, 1)
        else:
            # Draw level when no shield
            level_text = self.font_medium.render(f"Level: {level}", True, config.UI_HIGHLIGHT)
            surface.blit(level_text, (self.screen_width - 200, health_y + 25))
        
        # Draw level at top right if shield is showing
        if player.has_protection_shield and player.shield_hits_remaining > 0:
            level_text = self.font_medium.render(f"Level: {level}", True, config.UI_HIGHLIGHT)
            surface.blit(level_text, (self.screen_width - 200, health_y + 50))
        
        # Draw inventory display (compact icons)
        self._draw_inventory(surface, player, health_x + health_width + 20, health_y + 50)
    
    def _draw_inventory(self, surface: pygame.Surface, player, start_x: int, start_y: int):
        """Draw compact inventory panel showing collected items with icons."""
        # Inventory background
        inv_width = 180
        inv_height = 30
        pygame.draw.rect(surface, (40, 40, 40), (start_x - 5, start_y - 5, inv_width, inv_height))
        pygame.draw.rect(surface, config.WHITE, (start_x - 5, start_y - 5, inv_width, inv_height), 1)
        
        # Title
        inv_title = self.font_small.render("Inventory:", True, config.UI_TEXT)
        surface.blit(inv_title, (start_x, start_y - 3))
        
        icon_x = start_x + 65
        icon_y = start_y + 5
        icon_spacing = 22
        
        # Wizard Staff icon
        if player.has_wizard_staff:
            pygame.draw.circle(surface, config.WIZARD_STAFF_COLOR, (icon_x, icon_y), 7)
            pygame.draw.circle(surface, config.WHITE, (icon_x, icon_y), 7, 1)
            # Small staff symbol
            pygame.draw.line(surface, config.WHITE, (icon_x, icon_y - 4), (icon_x, icon_y + 4), 2)
            icon_x += icon_spacing
        
        # Bow icon
        if player.has_bow:
            # Draw bow shape
            pygame.draw.arc(surface, config.BOW_COLOR, (icon_x - 6, icon_y - 6, 12, 12), 0.5, 2.64, 2)
            pygame.draw.line(surface, config.BOW_COLOR, (icon_x - 4, icon_y - 5), (icon_x - 4, icon_y + 5), 1)
            icon_x += icon_spacing
        
        # Swords icon (if player has any)
        if player.weapons > 0:
            # Draw sword
            pygame.draw.line(surface, config.WEAPON_COLOR, (icon_x - 4, icon_y + 4), (icon_x + 4, icon_y - 4), 2)
            pygame.draw.rect(surface, config.GOLD, (icon_x - 2, icon_y + 3, 4, 2))
            icon_x += icon_spacing
        
        # Shield icon (if active)
        if player.has_protection_shield and player.shield_hits_remaining > 0:
            shield_pts = [
                (icon_x, icon_y - 5),
                (icon_x + 4, icon_y - 3),
                (icon_x + 4, icon_y + 2),
                (icon_x, icon_y + 6),
                (icon_x - 4, icon_y + 2),
                (icon_x - 4, icon_y - 3)
            ]
            pygame.draw.polygon(surface, config.SHIELD_COLOR, shield_pts)
            pygame.draw.polygon(surface, config.WHITE, shield_pts, 1)
            icon_x += icon_spacing
    
    def draw_minimap(self, surface: pygame.Surface, dungeon_map, player, ghosts, bears, rabbits, skeletons, wizards,
                     exit_pos, discovered_tiles):
        """Draw a minimap showing discovered areas."""
        # Minimap position (upper left corner, below UI)
        map_x = config.MINIMAP_MARGIN
        map_y = self.ui_height + config.MINIMAP_MARGIN
        
        # Draw minimap background
        pygame.draw.rect(surface, config.MINIMAP_BG,
                        (map_x, map_y, config.MINIMAP_SIZE, config.MINIMAP_SIZE))
        pygame.draw.rect(surface, config.WHITE,
                        (map_x, map_y, config.MINIMAP_SIZE, config.MINIMAP_SIZE), 2)
        
        # Calculate scale
        scale_x = config.MINIMAP_SIZE / dungeon_map.width
        scale_y = config.MINIMAP_SIZE / dungeon_map.height
        tile_size = min(scale_x, scale_y)
        
        # Draw discovered tiles
        for (tx, ty) in discovered_tiles:
            if 0 <= tx < dungeon_map.width and 0 <= ty < dungeon_map.height:
                mini_x = map_x + int(tx * tile_size)
                mini_y = map_y + int(ty * tile_size)
                
                if dungeon_map.tiles[ty][tx] == 1:  # Floor
                    color = config.MINIMAP_FLOOR
                else:  # Wall
                    color = config.MINIMAP_WALL
                
                pygame.draw.rect(surface, color,
                               (mini_x, mini_y, max(2, int(tile_size)), max(2, int(tile_size))))
        
        # Draw exit
        if exit_pos:
            exit_x = map_x + int(exit_pos[0] * tile_size)
            exit_y = map_y + int(exit_pos[1] * tile_size)
            if (int(exit_pos[0]), int(exit_pos[1])) in discovered_tiles:
                pygame.draw.circle(surface, config.MINIMAP_EXIT,
                                 (exit_x, exit_y), max(2, int(tile_size)))
        
        # Draw bears
        for bear in bears:
            bear_tx = int(bear.x)
            bear_ty = int(bear.y)
            if (bear_tx, bear_ty) in discovered_tiles:
                bear_x = map_x + int(bear.x * tile_size)
                bear_y = map_y + int(bear.y * tile_size)
                pygame.draw.circle(surface, config.MINIMAP_BEAR,
                                 (bear_x, bear_y), max(2, int(tile_size * 0.8)))
        
        # Draw rabbits
        for rabbit in rabbits:
            rabbit_tx = int(rabbit.x)
            rabbit_ty = int(rabbit.y)
            if (rabbit_tx, rabbit_ty) in discovered_tiles:
                rabbit_x = map_x + int(rabbit.x * tile_size)
                rabbit_y = map_y + int(rabbit.y * tile_size)
                pygame.draw.circle(surface, config.MINIMAP_RABBIT,
                                 (rabbit_x, rabbit_y), max(2, int(tile_size * 0.8)))
        
        # Draw skeletons
        for skeleton in skeletons:
            skeleton_tx = int(skeleton.x)
            skeleton_ty = int(skeleton.y)
            if (skeleton_tx, skeleton_ty) in discovered_tiles:
                skeleton_x = map_x + int(skeleton.x * tile_size)
                skeleton_y = map_y + int(skeleton.y * tile_size)
                pygame.draw.circle(surface, config.SKELETON_COLOR,
                                 (skeleton_x, skeleton_y), max(2, int(tile_size * 0.8)))
        
        # Draw wizards
        for wizard in wizards:
            wizard_tx = int(wizard.x)
            wizard_ty = int(wizard.y)
            if (wizard_tx, wizard_ty) in discovered_tiles:
                wizard_x = map_x + int(wizard.x * tile_size)
                wizard_y = map_y + int(wizard.y * tile_size)
                pygame.draw.circle(surface, config.WIZARD_COLOR,
                                 (wizard_x, wizard_y), max(2, int(tile_size * 0.8)))
        
        # Draw ghosts
        for ghost in ghosts:
            ghost_tx = int(ghost.x)
            ghost_ty = int(ghost.y)
            if (ghost_tx, ghost_ty) in discovered_tiles:
                ghost_x = map_x + int(ghost.x * tile_size)
                ghost_y = map_y + int(ghost.y * tile_size)
                pygame.draw.circle(surface, config.MINIMAP_GHOST,
                                 (ghost_x, ghost_y), max(2, int(tile_size * 0.8)))
        
        # Draw player
        player_x = map_x + int(player.x * tile_size)
        player_y = map_y + int(player.y * tile_size)
        pygame.draw.circle(surface, config.MINIMAP_PLAYER,
                         (player_x, player_y), max(3, int(tile_size * 1.2)))
        
        # Draw title
        minimap_title = self.font_small.render("MAP", True, config.UI_TEXT)
        surface.blit(minimap_title, (map_x + 5, map_y + 5))
    
    def draw_menu(self, surface: pygame.Surface, selected_option: int, 
                  resolution: str, difficulty: str):
        """Draw the main menu."""
        surface.fill(config.BLACK)
        
        # Title
        title = self.font_xlarge.render("DUNGEON CRAWLER", True, config.UI_HIGHLIGHT)
        title_rect = title.get_rect(center=(self.screen_width // 2, 100))
        surface.blit(title, title_rect)
        
        # Subtitle
        subtitle = self.font_medium.render("Collect treasures and escape!", True, config.UI_TEXT)
        subtitle_rect = subtitle.get_rect(center=(self.screen_width // 2, 150))
        surface.blit(subtitle, subtitle_rect)
        
        # Menu options
        menu_options = [
            "Start Game",
            f"Resolution: {resolution}",
            f"Difficulty: {difficulty}",
            "Instructions",
            "Quit"
        ]
        
        y_offset = 250
        for i, option in enumerate(menu_options):
            color = config.UI_HIGHLIGHT if i == selected_option else config.UI_TEXT
            text = self.font_large.render(option, True, color)
            text_rect = text.get_rect(center=(self.screen_width // 2, y_offset + i * 60))
            surface.blit(text, text_rect)
            
            # Draw selection indicator
            if i == selected_option:
                indicator = self.font_large.render(">", True, config.UI_HIGHLIGHT)
                surface.blit(indicator, (text_rect.left - 40, text_rect.top))
    
    def draw_pause_menu(self, surface: pygame.Surface, selected_option: int):
        """Draw the pause menu."""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(180)
        overlay.fill(config.BLACK)
        surface.blit(overlay, (0, 0))
        
        # Pause title
        title = self.font_xlarge.render("PAUSED", True, config.UI_HIGHLIGHT)
        title_rect = title.get_rect(center=(self.screen_width // 2, 200))
        surface.blit(title, title_rect)
        
        # Menu options
        menu_options = ["Resume", "Main Menu", "Quit"]
        
        y_offset = 300
        for i, option in enumerate(menu_options):
            color = config.UI_HIGHLIGHT if i == selected_option else config.UI_TEXT
            text = self.font_large.render(option, True, color)
            text_rect = text.get_rect(center=(self.screen_width // 2, y_offset + i * 60))
            surface.blit(text, text_rect)
            
            if i == selected_option:
                indicator = self.font_large.render(">", True, config.UI_HIGHLIGHT)
                surface.blit(indicator, (text_rect.left - 40, text_rect.top))
    
    def draw_instructions(self, surface: pygame.Surface, scroll_offset: int = 0):
        """Draw the scrollable instructions screen."""
        surface.fill(config.BLACK)
        
        # Title (fixed at top)
        title = self.font_xlarge.render("GAME GUIDE", True, config.UI_HIGHLIGHT)
        title_rect = title.get_rect(center=(self.screen_width // 2, 40))
        surface.blit(title, title_rect)
        
        # Create scrollable content (using medium font for better readability)
        instructions = [
            ("CONTROLS:", config.UI_HIGHLIGHT),
            ("Arrow Keys / WASD - Move around the dungeon", config.UI_TEXT),
            ("SPACE - Swing Sword (melee attack when near enemy)", config.UI_TEXT),
            ("B - Shoot Bow (ranged attack, requires arrows)", config.UI_TEXT),
            ("P / ESC - Pause game", config.UI_TEXT),
            ("", config.UI_TEXT),
            
            ("OBJECTIVE:", config.UI_HIGHLIGHT),
            ("Collect all coins and treasures in the main dungeon", config.UI_TEXT),
            ("Find secret rooms for bonus items and power-ups", config.UI_TEXT),
            ("Defeat or avoid enemies to survive", config.UI_TEXT),
            ("Find the exit door to complete each level", config.UI_TEXT),
            ("Progress through increasingly difficult dungeons", config.UI_TEXT),
            ("", config.UI_TEXT),
            
            ("ITEMS:", config.UI_HIGHLIGHT),
            ("Coins (yellow circles) - 10 points each", config.COIN_COLOR),
            ("Treasures (orange circles) - 50 points each", (255, 165, 0)),
            ("", config.UI_TEXT),
            ("NEW ITEMS:", config.UI_HIGHLIGHT),
            ("Ruby Gems - 100 points (sparkle animation)", (220, 20, 60)),
            ("Emerald Gems - 75 points (sparkle animation)", (0, 201, 87)),
            ("Sapphire Gems - 50 points (sparkle animation)", (15, 82, 186)),
            ("Freeze Scrolls - Freeze all enemies 5 seconds", (173, 216, 230)),
            ("Artifacts - Permanent upgrades (1-3 per level)", (255, 215, 0)),
            ("  * Max Weapons +3 (keeps between levels)", config.UI_TEXT),
            ("  * Max Arrows +5 (keeps between levels)", config.UI_TEXT),
            ("  * Full Health restore", config.UI_TEXT),
            ("  * Enemy destroyer (5 tile radius)", config.UI_TEXT),
            ("", config.UI_TEXT),
            ("WEAPONS:", config.UI_HIGHLIGHT),
            ("Swords (blue circles) - Melee weapons", config.WEAPON_COLOR),
            ("Bow (purple) - Ranged weapon", config.BOW_COLOR),
            ("Arrows (cyan) - Bow ammunition", (0, 255, 255)),
            ("Wizard Staff - Dropped by wizards (temp)", (138, 43, 226)),
            ("", config.UI_TEXT),
            
            ("POWER-UPS:", config.UI_HIGHLIGHT),
            ("SpeedPill (bright orange with sparkles)", config.SPEED_PILL_COLOR),
            ("  - Boosts your speed by 80% for 4 seconds", config.UI_TEXT),
            ("  - Multiple pills can spawn in secret rooms", config.UI_TEXT),
            ("", config.UI_TEXT),
            
            ("ENEMIES:", config.UI_HIGHLIGHT),
            ("Ghost (red floating spirits) - 1 hit to destroy", config.GHOST_COLOR),
            ("  - Slow moving, deals 10 damage on contact", config.UI_TEXT),
            ("  - Respawns after 20 seconds", config.UI_TEXT),
            ("", config.UI_TEXT),
            ("CrazyBear (brown/tan) - 2 hits to destroy", (139, 90, 43)),
            ("  - Faster than ghosts, deals 15 damage", config.UI_TEXT),
            ("  - Requires 2 sword swings or 2 arrows", config.UI_TEXT),
            ("  - Respawns after 25 seconds", config.UI_TEXT),
            ("", config.UI_TEXT),
            ("MadRabbit (purple, fades) - 3 hits to destroy", config.RABBIT_COLOR),
            ("  - Fast and aggressive, deals 20 damage", config.UI_TEXT),
            ("  - Requires 3 sword swings or 3 arrows", config.UI_TEXT),
            ("  - Color fades as it takes damage", config.UI_TEXT),
            ("  - Respawns after 30 seconds", config.UI_TEXT),
            ("", config.UI_TEXT),
            ("NEW ENEMIES:", config.UI_HIGHLIGHT),
            ("Chillin' Skeleton (white bones) - 3 hits", (200, 200, 200)),
            ("  - Slow but tough, deals 12 damage", config.UI_TEXT),
            ("  - Skull cracks show damage taken", config.UI_TEXT),
            ("  - Drops gold or freeze scrolls", config.UI_TEXT),
            ("  - Does NOT respawn", config.UI_TEXT),
            ("", config.UI_TEXT),
            ("Dark Wizard (purple robe) - 5 hits", (138, 43, 226)),
            ("  - Shoots magical projectiles, 15 damage", config.UI_TEXT),
            ("  - Attacks from distance (ranged)", config.UI_TEXT),
            ("  - Drops wizard staff when defeated", config.UI_TEXT),
            ("  - Does NOT respawn", config.UI_TEXT),
            ("", config.UI_TEXT),
            
            ("SPECIAL FEATURES:", config.UI_HIGHLIGHT),
            ("Minimap - Shows discovered areas (upper left)", (100, 200, 255)),
            ("Secret Rooms - Hidden bonus areas", (180, 140, 255)),
            ("  - Look for doors to special chambers", config.UI_TEXT),
            ("  - All secret rooms have exits", config.UI_TEXT),
            ("Visual Effects - Glowing pickups and combat", (255, 255, 100)),
            ("  - Bright burst when collecting bow", config.UI_TEXT),
            ("  - Red swirl when swinging sword", config.UI_TEXT),
            ("", config.UI_TEXT),
            
            ("TIPS:", config.UI_HIGHLIGHT),
            ("* Scores now carry over between levels!", (100, 255, 100)),
            ("* Artifact capacity upgrades are permanent", (255, 215, 0)),
            ("* Freeze scrolls help when surrounded", config.UI_TEXT),
            ("* Skeletons and wizards drop valuable loot", config.UI_TEXT),
            ("* Wizard staff is powerful but temporary", config.UI_TEXT),
            ("* Explore thoroughly to find all items", config.UI_TEXT),
            ("* Use bow for safer distance attacks", config.UI_TEXT),
            ("* SpeedPills help dodge enemies", config.UI_TEXT),
            ("* Some enemies need multiple hits", config.UI_TEXT),
            ("* Check minimap to track progress", config.UI_TEXT),
            ("", config.UI_TEXT),
            ("", config.UI_TEXT),
            ("Use UP/DOWN arrows or mouse wheel to scroll", (150, 150, 150)),
            ("Press ESC to return to menu", (150, 150, 150)),
        ]
        
        # Calculate content area
        content_top = 90
        content_height = self.screen_height - content_top - 60
        line_height = 32  # Increased for larger font
        
        # Draw content area background
        content_rect = pygame.Rect(40, content_top, self.screen_width - 100, content_height)
        pygame.draw.rect(surface, (20, 20, 20), content_rect)
        pygame.draw.rect(surface, config.UI_HIGHLIGHT, content_rect, 2)
        
        # Create a surface for scrollable content
        y_offset = content_top + 10 - scroll_offset
        
        # Only render lines that are visible
        for line_text, color in instructions:
            if y_offset > content_top - line_height and y_offset < content_top + content_height + line_height:
                if line_text:  # Skip empty lines for rendering
                    # Use medium font for better readability
                    text = self.font_medium.render(line_text, True, color)
                    text_rect = text.get_rect(midleft=(60, y_offset))
                    # Clip text to content area
                    if y_offset >= content_top and y_offset <= content_top + content_height - 30:
                        surface.blit(text, text_rect)
            y_offset += line_height
        
        # Draw scroll bar on the right side
        max_scroll = self.get_max_instruction_scroll()
        if max_scroll > 0:
            scrollbar_x = self.screen_width - 70
            scrollbar_top = content_top + 10
            scrollbar_height = content_height - 20
            scrollbar_width = 20
            
            # Draw scrollbar track
            track_rect = pygame.Rect(scrollbar_x, scrollbar_top, scrollbar_width, scrollbar_height)
            pygame.draw.rect(surface, (60, 60, 60), track_rect)
            pygame.draw.rect(surface, config.UI_HIGHLIGHT, track_rect, 2)
            
            # Calculate scrollbar thumb position and size
            total_content_height = len(instructions) * line_height
            visible_ratio = min(1.0, content_height / total_content_height)
            thumb_height = max(30, int(scrollbar_height * visible_ratio))
            
            scroll_ratio = scroll_offset / max_scroll if max_scroll > 0 else 0
            thumb_y = scrollbar_top + int((scrollbar_height - thumb_height) * scroll_ratio)
            
            # Draw scrollbar thumb
            thumb_rect = pygame.Rect(scrollbar_x + 2, thumb_y, scrollbar_width - 4, thumb_height)
            pygame.draw.rect(surface, config.UI_HIGHLIGHT, thumb_rect)
            pygame.draw.rect(surface, config.WHITE, thumb_rect, 1)
        
        # Draw scroll indicators with larger, more visible arrows
        if scroll_offset > 0:
            # Up arrow indicator - large and prominent
            arrow_text = self.font_xlarge.render("SCROLL UP", True, config.UI_HIGHLIGHT)
            arrow_rect = arrow_text.get_rect(center=(self.screen_width // 2, content_top - 20))
            surface.blit(arrow_text, arrow_rect)
            # Draw arrow symbol
            pygame.draw.polygon(surface, config.UI_HIGHLIGHT, [
                (self.screen_width // 2 - 80, content_top - 15),
                (self.screen_width // 2 - 90, content_top - 25),
                (self.screen_width // 2 - 70, content_top - 25)
            ])
        
        if scroll_offset < max_scroll:
            # Down arrow indicator - large and prominent
            arrow_text = self.font_xlarge.render("SCROLL DOWN", True, config.UI_HIGHLIGHT)
            arrow_rect = arrow_text.get_rect(center=(self.screen_width // 2, self.screen_height - 25))
            surface.blit(arrow_text, arrow_rect)
            # Draw arrow symbol
            pygame.draw.polygon(surface, config.UI_HIGHLIGHT, [
                (self.screen_width // 2 + 100, self.screen_height - 20),
                (self.screen_width // 2 + 90, self.screen_height - 30),
                (self.screen_width // 2 + 110, self.screen_height - 30)
            ])
    
    def get_max_instruction_scroll(self) -> int:
        """Calculate maximum scroll offset for instructions."""
        content_top = 90
        content_height = self.screen_height - content_top - 60
        line_height = 32  # Updated to match draw_instructions
        total_lines = 102  # Updated total number of instruction lines (added new items and enemies)
        total_content_height = total_lines * line_height
        return max(0, total_content_height - content_height)
    
    def draw_level_complete(self, surface: pygame.Surface, player, level: int):
        """Draw level complete screen."""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(200)
        overlay.fill(config.BLACK)
        surface.blit(overlay, (0, 0))
        
        # Title
        title = self.font_xlarge.render("LEVEL COMPLETE!", True, config.UI_HIGHLIGHT)
        title_rect = title.get_rect(center=(self.screen_width // 2, 200))
        surface.blit(title, title_rect)
        
        # Stats
        stats = [
            f"Level: {level}",
            f"Score: {player.score}",
            f"Coins: {player.coins_collected}",
            f"Treasures: {player.treasures_collected}",
            "",
            "Press SPACE to continue"
        ]
        
        y_offset = 300
        for line in stats:
            text = self.font_large.render(line, True, config.UI_TEXT)
            text_rect = text.get_rect(center=(self.screen_width // 2, y_offset))
            surface.blit(text, text_rect)
            y_offset += 50
    
    def draw_game_over(self, surface: pygame.Surface, player, level: int):
        """Draw game over screen."""
        surface.fill(config.BLACK)
        
        # Title
        title = self.font_xlarge.render("GAME OVER", True, config.HEALTH_COLOR)
        title_rect = title.get_rect(center=(self.screen_width // 2, 200))
        surface.blit(title, title_rect)
        
        # Final stats
        stats = [
            f"Final Level: {level}",
            f"Final Score: {player.score}",
            f"Coins Collected: {player.coins_collected}",
            f"Treasures Found: {player.treasures_collected}",
            "",
            "Press SPACE to return to menu"
        ]
        
        y_offset = 300
        for line in stats:
            text = self.font_large.render(line, True, config.UI_TEXT)
            text_rect = text.get_rect(center=(self.screen_width // 2, y_offset))
            surface.blit(text, text_rect)
            y_offset += 50
    
    def draw_powerup_status(self, surface: pygame.Surface, player, current_time: int):
        """Draw active power-up status indicators."""
        # Position below minimap
        status_x = self.screen_width - config.MINIMAP_SIZE - config.MINIMAP_MARGIN
        status_y = self.ui_height + config.MINIMAP_MARGIN + config.MINIMAP_SIZE + 10
        
        active_powerups = []
        
        # Check each power-up type
        if player.speed_boost_end > current_time:
            time_left = (player.speed_boost_end - current_time) / 1000.0
            active_powerups.append(("SPEED", config.SPEED_BOOST_COLOR, time_left))
        
        if player.shield_end > current_time:
            time_left = (player.shield_end - current_time) / 1000.0
            active_powerups.append(("SHIELD", config.SHIELD_COLOR, time_left))
        
        if player.double_points_end > current_time:
            time_left = (player.double_points_end - current_time) / 1000.0
            active_powerups.append(("2X PTS", config.DOUBLE_POINTS_COLOR, time_left))
        
        if player.vision_boost_end > current_time:
            time_left = (player.vision_boost_end - current_time) / 1000.0
            active_powerups.append(("VISION", config.VISION_BOOST_COLOR, time_left))
        
        # Draw power-up status bars
        if active_powerups:
            # Title
            title = self.font_small.render("POWER-UPS:", True, config.UI_TEXT)
            surface.blit(title, (status_x, status_y))
            status_y += 20
            
            for name, color, time_left in active_powerups:
                # Power-up name
                text = self.font_small.render(name, True, color)
                surface.blit(text, (status_x, status_y))
                
                # Time bar
                bar_width = 100
                bar_height = 10
                bar_x = status_x + 70
                bar_y = status_y + 2
                
                # Background
                pygame.draw.rect(surface, config.DARK_GRAY,
                               (bar_x, bar_y, bar_width, bar_height))
                
                # Determine max duration based on power-up type
                max_duration = config.SPEED_BOOST_DURATION / 1000.0  # Default
                if name == "SHIELD":
                    max_duration = config.SHIELD_DURATION / 1000.0
                elif name == "2X PTS":
                    max_duration = config.DOUBLE_POINTS_DURATION / 1000.0
                elif name == "VISION":
                    max_duration = config.VISION_BOOST_DURATION / 1000.0
                
                # Fill based on time remaining
                fill_width = int(bar_width * (time_left / max_duration))
                pygame.draw.rect(surface, color,
                               (bar_x, bar_y, fill_width, bar_height))
                
                # Border
                pygame.draw.rect(surface, config.WHITE,
                               (bar_x, bar_y, bar_width, bar_height), 1)
                
                status_y += 18
