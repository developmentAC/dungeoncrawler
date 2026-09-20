"""
Game entities including player, ghosts, and items.
"""

import pygame
import math
import random
from typing import List, Tuple, Optional
import config


class Entity:
    """Base class for all game entities."""
    
    def __init__(self, x: float, y: float, color: Tuple[int, int, int]):
        self.x = x
        self.y = y
        self.color = color
        self.size = config.TILE_SIZE - 4
    
    def get_rect(self) -> pygame.Rect:
        """Get the entity's collision rectangle."""
        return pygame.Rect(
            int(self.x * config.TILE_SIZE) + 2,
            int(self.y * config.TILE_SIZE) + 2,
            self.size,
            self.size
        )
    
    def draw(self, surface: pygame.Surface, camera_x: int, camera_y: int):
        """Draw the entity."""
        screen_x = int(self.x * config.TILE_SIZE - camera_x)
        screen_y = int(self.y * config.TILE_SIZE - camera_y)
        pygame.draw.rect(surface, self.color,
                        (screen_x + 2, screen_y + 2, self.size, self.size))
        # Add border
        pygame.draw.rect(surface, config.WHITE,
                        (screen_x + 2, screen_y + 2, self.size, self.size), 2)


class Player(Entity):
    """Player character with power-up support."""
    
    def __init__(self, x: float, y: float, max_health: int):
        super().__init__(x, y, config.PLAYER_COLOR)
        # Health and basic stats
        self.max_health = max_health
        self.health = max_health
        self.score = 0
        
        # Inventory
        self.weapons = 0  # Swords
        self.arrows = 0  # Arrow count
        self.has_bow = False  # Whether player has collected a bow
        self.coins_collected = 0
        self.treasures_collected = 0
        
        # Upgradeable capacities (transferable between levels)
        self.max_weapons = config.PLAYER_BASE_MAX_WEAPONS
        self.max_arrows = config.PLAYER_BASE_MAX_ARROWS
        
        # Wizard staff (temporary, only for current level)
        self.has_wizard_staff = False
        self.wizard_staff_uses = 0
        
        # Protection shield (hit-based, not timed)
        self.has_protection_shield = False
        self.shield_hits_remaining = 0
        
        # Movement
        self.base_speed = config.PLAYER_SPEED
        self.speed = self.base_speed
        self.invulnerable_time = 0
        
        # Power-up states (end times in milliseconds)
        self.speed_boost_end = 0
        self.speed_pill_end = 0
        self.shield_end = 0
        self.double_points_end = 0
        self.vision_boost_end = 0
        self.freeze_enemies_end = 0  # Freeze scroll effect
    
    def move(self, dx: float, dy: float, dungeon_map):
        """Move the player if the destination is walkable."""
        new_x = self.x + dx
        new_y = self.y + dy
        
        # Check if new position is walkable
        if dungeon_map.is_walkable(int(new_x), int(self.y)):
            self.x = new_x
        if dungeon_map.is_walkable(int(self.x), int(new_y)):
            self.y = new_y
    
    def take_damage(self, damage: int, current_time: int):
        """
        Take damage if not invulnerable or shielded.
        
        Args:
            damage: Amount of damage to take
            current_time: Current game time in milliseconds
        """
        # Check if protection shield is active (hit-based)
        if self.has_protection_shield and self.shield_hits_remaining > 0:
            self.shield_hits_remaining -= 1
            if self.shield_hits_remaining <= 0:
                self.has_protection_shield = False
                self.shield_hits_remaining = 0
            return  # Shield absorbs damage
        
        # Check if timed shield is active (old power-up system)
        if current_time < self.shield_end:
            return  # Shield absorbs damage
        
        # Check normal invulnerability
        if self.invulnerable_time <= current_time:
            self.health -= damage
            self.invulnerable_time = current_time + 1000  # 1 second invulnerability
            if self.health < 0:
                self.health = 0
    
    def use_weapon(self) -> bool:
        """Use a weapon if available."""
        if self.weapons > 0:
            self.weapons -= 1
            return True
        return False
    
    def use_bow(self) -> bool:
        """Use a bow if player has bow and arrows available."""
        if self.has_bow and self.arrows > 0:
            self.arrows -= 1
            return True
        return False
    
    def collect_coin(self):
        """Collect a coin."""
        self.coins_collected += 1
        self.score += config.COIN_VALUE
    
    def collect_treasure(self):
        """Collect a treasure."""
        self.treasures_collected += 1
        self.score += config.TREASURE_VALUE
    
    def collect_weapon(self):
        """Collect a weapon (sword)."""
        if self.weapons < self.max_weapons:
            self.weapons += 1
    
    def collect_bow(self):
        """Collect a bow (enables arrow usage)."""
        self.has_bow = True
    
    def collect_arrow(self):
        """Collect an arrow."""
        if self.arrows < self.max_arrows:
            self.arrows += 1
    
    def collect_heart(self):
        """Collect a heart to restore health."""
        self.health = min(self.max_health, self.health + config.HEART_HEALTH)
    
    def activate_speed_boost(self, current_time: int):
        """
        Activate speed boost power-up.
        
        Args:
            current_time: Current game time in milliseconds
        """
        self.speed_boost_end = current_time + config.SPEED_BOOST_DURATION
        self.speed = self.base_speed * config.SPEED_BOOST_MULTIPLIER
    
    def activate_speed_pill(self, current_time: int):
        """
        Activate speed pill power-up (4 seconds).
        
        Args:
            current_time: Current game time in milliseconds
        """
        self.speed_pill_end = current_time + config.SPEED_PILL_DURATION
        self.speed = self.base_speed * config.SPEED_PILL_MULTIPLIER
    
    def activate_shield(self, current_time: int):
        """
        Activate shield power-up.
        
        Args:
            current_time: Current game time in milliseconds
        """
        self.shield_end = current_time + config.SHIELD_DURATION
    
    def activate_double_points(self, current_time: int):
        """
        Activate double points power-up.
        
        Args:
            current_time: Current game time in milliseconds
        """
        self.double_points_end = current_time + config.DOUBLE_POINTS_DURATION
    
    def activate_vision_boost(self, current_time: int):
        """
        Activate vision boost power-up.
        
        Args:
            current_time: Current game time in milliseconds
        """
        self.vision_boost_end = current_time + config.VISION_BOOST_DURATION
    
    def update_power_ups(self, current_time: int):
        """
        Update power-up states and revert speed when expired.
        
        Args:
            current_time: Current game time in milliseconds
        """
        # Check if speed boost or speed pill expired
        if (current_time >= self.speed_boost_end and 
            current_time >= self.speed_pill_end and 
            self.speed != self.base_speed):
            self.speed = self.base_speed
    
    def has_shield(self, current_time: int) -> bool:
        """Check if shield is active."""
        return current_time < self.shield_end
    
    def has_double_points(self, current_time: int) -> bool:
        """Check if double points is active."""
        return current_time < self.double_points_end
    
    def has_vision_boost(self, current_time: int) -> bool:
        """Check if vision boost is active."""
        return current_time < self.vision_boost_end
    
    def has_speed_boost(self, current_time: int) -> bool:
        """Check if speed boost or speed pill is active."""
        return current_time < self.speed_boost_end or current_time < self.speed_pill_end
    
    def is_alive(self) -> bool:
        """Check if player is alive."""
        return self.health > 0
    
    def draw(self, surface: pygame.Surface, camera_x: int, camera_y: int):
        """Draw the player as an adventurer with power-up visual indicators."""
        screen_x = int(self.x * config.TILE_SIZE - camera_x)
        screen_y = int(self.y * config.TILE_SIZE - camera_y)
        center_x = screen_x + config.TILE_SIZE // 2
        center_y = screen_y + config.TILE_SIZE // 2
        
        # Get current time for power-up checks
        current_time = pygame.time.get_ticks()
        
        # Skip if invulnerable and flashing (unless shielded)
        if self.invulnerable_time > current_time and not self.has_shield(current_time):
            if (current_time // 100) % 2 == 0:
                return
        
        # Draw shield effect if active
        if self.has_shield(current_time):
            shield_pulse = abs(math.sin(current_time * 0.005))
            shield_radius = self.size // 2 + int(shield_pulse * 5)
            pygame.draw.circle(surface, config.SHIELD_COLOR, (center_x, center_y), 
                             shield_radius, 3)
        
        # Draw speed lines if speed boost active
        if self.has_speed_boost(current_time):
            for i in range(3):
                offset = i * 8
                line_length = 10 - i * 2
                pygame.draw.line(surface, config.SPEED_BOOST_COLOR,
                               (center_x - self.size // 2 - offset, center_y - 5 + i * 5),
                               (center_x - self.size // 2 - offset - line_length, center_y - 5 + i * 5), 2)
        
        # Draw body (larger circle)
        body_color = config.PLAYER_COLOR
        # Tint body if double points active
        if self.has_double_points(current_time):
            pulse = abs(math.sin(current_time * 0.008))
            body_color = (
                int(config.PLAYER_COLOR[0] * (0.7 + pulse * 0.3)),
                int(config.PLAYER_COLOR[1] * (0.5 + pulse * 0.5)),
                255
            )
        pygame.draw.circle(surface, body_color, (center_x, center_y), self.size // 3)
        
        # Draw head
        pygame.draw.circle(surface, (100, 220, 255), (center_x, center_y - self.size // 4), self.size // 5)
        
        # Draw eyes (glowing if vision boost active)
        eye_color = config.VISION_BOOST_COLOR if self.has_vision_boost(current_time) else config.WHITE
        pygame.draw.circle(surface, eye_color, (center_x - 3, center_y - self.size // 4), 2)
        pygame.draw.circle(surface, eye_color, (center_x + 3, center_y - self.size // 4), 2)
        
        # Draw shield outline
        pygame.draw.circle(surface, (150, 150, 200), (center_x, center_y), self.size // 3, 2)
        
        # Draw weapon indicator if carrying weapons
        if self.weapons > 0:
            sword_color = (200, 200, 255)
            pygame.draw.line(surface, sword_color, 
                           (center_x + self.size // 3, center_y), 
                           (center_x + self.size // 2, center_y - self.size // 3), 3)
        
        # Draw bow indicator if player has bow
        if self.has_bow:
            bow_color = config.BOW_COLOR
            # Draw simple bow arc
            pygame.draw.arc(surface, bow_color,
                          (center_x - self.size // 3 - 5, center_y - 5, 10, 10),
                          0, 3.14, 2)


class Ghost(Entity):
    """Ghost enemy with AI."""
    
    def __init__(self, x: float, y: float, speed: float):
        super().__init__(x, y, config.GHOST_COLOR)
        self.speed = speed
        self.health = 1
        self.last_attack_time = 0
        self.wander_direction = [random.choice([-1, 0, 1]), random.choice([-1, 0, 1])]
        self.wander_timer = 0
        self.is_angry = False
    
    def update(self, player: Player, dungeon_map, current_time: int):
        """Update ghost AI and movement."""
        # Calculate distance to player
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # Check if player is in detection range
        if distance < config.GHOST_DETECTION_RANGE / config.TILE_SIZE:
            self.is_angry = True
            # Chase player
            if distance > 0.5:
                move_x = (dx / distance) * self.speed * 0.02
                move_y = (dy / distance) * self.speed * 0.02
                
                # Try to move towards player
                new_x = self.x + move_x
                new_y = self.y + move_y
                
                if dungeon_map.is_walkable(int(new_x), int(self.y)):
                    self.x = new_x
                if dungeon_map.is_walkable(int(self.x), int(new_y)):
                    self.y = new_y
            
            # Attack if in range
            if distance < config.GHOST_ATTACK_RANGE / config.TILE_SIZE:
                if current_time - self.last_attack_time > config.GHOST_ATTACK_COOLDOWN:
                    player.take_damage(config.GHOST_DAMAGE, current_time)
                    self.last_attack_time = current_time
        else:
            # Wander randomly
            self.is_angry = False
            self.wander_timer += 1
            
            if self.wander_timer > 60:  # Change direction every second
                self.wander_direction = [random.choice([-1, 0, 1]), random.choice([-1, 0, 1])]
                self.wander_timer = 0
            
            move_x = self.wander_direction[0] * self.speed * 0.01
            move_y = self.wander_direction[1] * self.speed * 0.01
            
            new_x = self.x + move_x
            new_y = self.y + move_y
            
            if dungeon_map.is_walkable(int(new_x), int(self.y)):
                self.x = new_x
            else:
                self.wander_direction[0] = -self.wander_direction[0]
            
            if dungeon_map.is_walkable(int(self.x), int(new_y)):
                self.y = new_y
            else:
                self.wander_direction[1] = -self.wander_direction[1]
        
        # Update color based on state
        self.color = config.GHOST_ANGRY_COLOR if self.is_angry else config.GHOST_COLOR
    
    def is_alive(self) -> bool:
        """Check if ghost is alive."""
        return self.health > 0
    
    def draw(self, surface: pygame.Surface, camera_x: int, camera_y: int):
        """Draw the ghost with spooky appearance."""
        screen_x = int(self.x * config.TILE_SIZE - camera_x)
        screen_y = int(self.y * config.TILE_SIZE - camera_y)
        center_x = screen_x + config.TILE_SIZE // 2
        center_y = screen_y + config.TILE_SIZE // 2
        
        # Floating animation
        float_offset = int(math.sin(pygame.time.get_ticks() * 0.003) * 3)
        center_y += float_offset
        
        # Semi-transparent effect (draw multiple layers)
        alpha_color = self.color
        
        # Draw ghostly body (main circle)
        pygame.draw.circle(surface, alpha_color, (center_x, center_y), self.size // 2)
        
        # Draw wavy bottom edge
        wave_points = []
        for i in range(5):
            x = center_x - self.size // 2 + i * (self.size // 4)
            wave = math.sin(pygame.time.get_ticks() * 0.005 + i) * 3
            y = center_y + self.size // 2 + int(wave)
            wave_points.append((x, y))
        
        # Draw trailing effect
        for i, point in enumerate(wave_points):
            pygame.draw.circle(surface, alpha_color, point, 4)
        
        # Draw eyes (scary when angry)
        eye_color = (255, 255, 0) if self.is_angry else (100, 100, 100)
        pygame.draw.circle(surface, eye_color, (center_x - 6, center_y - 4), 4)
        pygame.draw.circle(surface, eye_color, (center_x + 6, center_y - 4), 4)
        
        # Draw pupils
        pupil_color = config.BLACK if self.is_angry else (50, 50, 50)
        pygame.draw.circle(surface, pupil_color, (center_x - 6, center_y - 4), 2)
        pygame.draw.circle(surface, pupil_color, (center_x + 6, center_y - 4), 2)
        
        # Draw mouth when angry
        if self.is_angry:
            mouth_points = [
                (center_x - 6, center_y + 4),
                (center_x, center_y + 8),
                (center_x + 6, center_y + 4)
            ]
            pygame.draw.lines(surface, (150, 0, 0), False, mouth_points, 2)
        
        # Outer glow
        pygame.draw.circle(surface, alpha_color, (center_x, center_y), self.size // 2, 2)
        
        # Draw health bar
        self._draw_health_bar(surface, screen_x, screen_y)
    
    def _draw_health_bar(self, surface: pygame.Surface, screen_x: int, screen_y: int):
        """Draw health bar above enemy."""
        bar_width = config.TILE_SIZE
        bar_height = 4
        bar_x = screen_x
        bar_y = screen_y - 8
        
        # Background (black)
        pygame.draw.rect(surface, config.BLACK, (bar_x, bar_y, bar_width, bar_height))
        
        # Health bar color (ghosts are 1-hit, so always green when alive)
        bar_color = (0, 255, 0)  # Green
        
        # Draw filled portion
        if self.health > 0:
            pygame.draw.rect(surface, bar_color, (bar_x, bar_y, bar_width, bar_height))


class CrazyBear(Entity):
    """Crazy Bear enemy - a silly looking adversary."""
    
    def __init__(self, x: float, y: float, speed: float):
        super().__init__(x, y, config.BEAR_COLOR)
        self.speed = speed
        self.health = 2  # Takes 2 hits to kill
        self.max_health = 2
        self.last_attack_time = 0
        self.wander_direction = [random.choice([-1, 0, 1]), random.choice([-1, 0, 1])]
        self.wander_timer = 0
        self.is_dancing = False
        self.dance_timer = 0
    
    def update(self, player: Player, dungeon_map, current_time: int):
        """Update bear AI and movement."""
        # Calculate distance to player
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # Random dancing behavior
        self.dance_timer += 1
        if self.dance_timer > 120:
            self.is_dancing = not self.is_dancing
            self.dance_timer = 0
        
        # Check if player is in detection range
        if distance < config.BEAR_DETECTION_RANGE / config.TILE_SIZE:
            # Chase player (but clumsily)
            if distance > 0.5:
                move_x = (dx / distance) * self.speed * 0.015
                move_y = (dy / distance) * self.speed * 0.015
                
                # Add silly wobble
                wobble = math.sin(pygame.time.get_ticks() * 0.01) * 0.5
                move_x += wobble * 0.02
                move_y += wobble * 0.02
                
                # Try to move towards player
                new_x = self.x + move_x
                new_y = self.y + move_y
                
                if dungeon_map.is_walkable(int(new_x), int(self.y)):
                    self.x = new_x
                if dungeon_map.is_walkable(int(self.x), int(new_y)):
                    self.y = new_y
            
            # Attack if in range
            if distance < config.BEAR_ATTACK_RANGE / config.TILE_SIZE:
                if current_time - self.last_attack_time > config.BEAR_ATTACK_COOLDOWN:
                    player.take_damage(config.BEAR_DAMAGE, current_time)
                    self.last_attack_time = current_time
        else:
            # Wander randomly and goofily
            self.wander_timer += 1
            
            if self.wander_timer > 40:  # Change direction more frequently
                self.wander_direction = [random.choice([-1, 0, 1]), random.choice([-1, 0, 1])]
                self.wander_timer = 0
            
            move_x = self.wander_direction[0] * self.speed * 0.008
            move_y = self.wander_direction[1] * self.speed * 0.008
            
            new_x = self.x + move_x
            new_y = self.y + move_y
            
            if dungeon_map.is_walkable(int(new_x), int(self.y)):
                self.x = new_x
            else:
                self.wander_direction[0] = -self.wander_direction[0]
            
            if dungeon_map.is_walkable(int(self.x), int(new_y)):
                self.y = new_y
            else:
                self.wander_direction[1] = -self.wander_direction[1]
    
    def is_alive(self) -> bool:
        """Check if bear is alive."""
        return self.health > 0
    
    def draw(self, surface: pygame.Surface, camera_x: int, camera_y: int):
        """Draw the crazy bear with silly appearance."""
        screen_x = int(self.x * config.TILE_SIZE - camera_x)
        screen_y = int(self.y * config.TILE_SIZE - camera_y)
        center_x = screen_x + config.TILE_SIZE // 2
        center_y = screen_y + config.TILE_SIZE // 2
        
        # Bouncing animation
        bounce = abs(math.sin(pygame.time.get_ticks() * 0.008)) * 4
        center_y -= int(bounce)
        
        # Draw body (round brown bear)
        pygame.draw.circle(surface, self.color, (center_x, center_y + 2), self.size // 2)
        
        # Draw belly
        pygame.draw.circle(surface, config.BEAR_ACCENT, (center_x, center_y + 4), self.size // 3)
        
        # Draw head
        head_y = center_y - self.size // 3
        pygame.draw.circle(surface, self.color, (center_x, head_y), self.size // 3)
        
        # Draw ears (silly round ears)
        ear_offset = self.size // 4
        pygame.draw.circle(surface, self.color, (center_x - ear_offset, head_y - ear_offset), 6)
        pygame.draw.circle(surface, self.color, (center_x + ear_offset, head_y - ear_offset), 6)
        pygame.draw.circle(surface, config.BEAR_ACCENT, (center_x - ear_offset, head_y - ear_offset), 3)
        pygame.draw.circle(surface, config.BEAR_ACCENT, (center_x + ear_offset, head_y - ear_offset), 3)
        
        # Draw silly crossed eyes
        eye_spin = pygame.time.get_ticks() * 0.005
        eye1_x = center_x - 5 + int(math.sin(eye_spin) * 2)
        eye2_x = center_x + 5 + int(math.cos(eye_spin) * 2)
        pygame.draw.circle(surface, config.WHITE, (eye1_x, head_y), 4)
        pygame.draw.circle(surface, config.WHITE, (eye2_x, head_y), 4)
        pygame.draw.circle(surface, config.BLACK, (eye1_x + 1, head_y), 2)
        pygame.draw.circle(surface, config.BLACK, (eye2_x - 1, head_y), 2)
        
        # Draw goofy tongue sticking out
        if self.is_dancing:
            tongue_length = int(abs(math.sin(pygame.time.get_ticks() * 0.01)) * 6) + 3
            pygame.draw.line(surface, (255, 100, 100),
                           (center_x, head_y + 5),
                           (center_x + 3, head_y + 5 + tongue_length), 3)
        
        # Draw snout
        pygame.draw.circle(surface, config.BEAR_ACCENT, (center_x, head_y + 4), 5)
        pygame.draw.circle(surface, config.BLACK, (center_x, head_y + 3), 2)
        
        # Draw paws
        paw_swing = math.sin(pygame.time.get_ticks() * 0.01) * 3
        pygame.draw.circle(surface, self.color, (center_x - 10, center_y + 8 + int(paw_swing)), 4)
        pygame.draw.circle(surface, self.color, (center_x + 10, center_y + 8 - int(paw_swing)), 4)
        
        # Draw health bar
        self._draw_health_bar(surface, screen_x, screen_y, 2)
    
    def _draw_health_bar(self, surface: pygame.Surface, screen_x: int, screen_y: int, max_health: int):
        """Draw health bar above enemy."""
        bar_width = config.TILE_SIZE
        bar_height = 4
        bar_x = screen_x
        bar_y = screen_y - 8
        
        # Background (black)
        pygame.draw.rect(surface, config.BLACK, (bar_x, bar_y, bar_width, bar_height))
        
        # Health bar color based on health percentage
        health_percent = self.health / max_health
        if health_percent > 0.6:
            bar_color = (0, 255, 0)  # Green
        elif health_percent > 0.3:
            bar_color = (255, 255, 0)  # Yellow
        else:
            bar_color = (255, 0, 0)  # Red
        
        # Draw filled portion
        filled_width = int(bar_width * health_percent)
        if filled_width > 0:
            pygame.draw.rect(surface, bar_color, (bar_x, bar_y, filled_width, bar_height))


class MadRabbit(Entity):
    """Mad Rabbit enemy - cute but tough, requires 3 hits to kill."""
    
    def __init__(self, x: float, y: float, speed: float):
        super().__init__(x, y, config.RABBIT_COLOR)
        self.speed = speed
        self.health = 3  # Takes 3 hits to kill
        self.max_health = 3
        self.last_attack_time = 0
        self.wander_direction = [random.choice([-1, 0, 1]), random.choice([-1, 0, 1])]
        self.wander_timer = 0
        self.hop_timer = 0
    
    def update(self, player: Player, dungeon_map, current_time: int):
        """Update rabbit AI and movement."""
        # Calculate distance to player
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # Update color based on health (bright → faded → almost grey)
        health_ratio = self.health / self.max_health
        if health_ratio > 0.66:  # Full health (3/3)
            self.color = config.RABBIT_COLOR  # Bright color
        elif health_ratio > 0.33:  # Medium health (2/3)
            self.color = config.RABBIT_DAMAGED_COLOR  # Faded color
        else:  # Low health (1/3)
            self.color = config.RABBIT_DYING_COLOR  # Almost grey
        
        self.hop_timer += 1
        
        # Check if player is in detection range
        if distance < config.RABBIT_DETECTION_RANGE / config.TILE_SIZE:
            # Chase player with hopping movement
            if distance > 0.5:
                move_x = (dx / distance) * self.speed * 0.018
                move_y = (dy / distance) * self.speed * 0.018
                
                # Try to move towards player
                new_x = self.x + move_x
                new_y = self.y + move_y
                
                if dungeon_map.is_walkable(int(new_x), int(self.y)):
                    self.x = new_x
                if dungeon_map.is_walkable(int(self.x), int(new_y)):
                    self.y = new_y
            
            # Attack if in range
            if distance < config.RABBIT_ATTACK_RANGE / config.TILE_SIZE:
                if current_time - self.last_attack_time > config.RABBIT_ATTACK_COOLDOWN:
                    player.take_damage(config.RABBIT_DAMAGE, current_time)
                    self.last_attack_time = current_time
        else:
            # Wander randomly with hopping
            self.wander_timer += 1
            
            if self.wander_timer > 50:  # Change direction periodically
                self.wander_direction = [random.choice([-1, 0, 1]), random.choice([-1, 0, 1])]
                self.wander_timer = 0
            
            move_x = self.wander_direction[0] * self.speed * 0.01
            move_y = self.wander_direction[1] * self.speed * 0.01
            
            new_x = self.x + move_x
            new_y = self.y + move_y
            
            if dungeon_map.is_walkable(int(new_x), int(self.y)):
                self.x = new_x
            else:
                self.wander_direction[0] = -self.wander_direction[0]
            
            if dungeon_map.is_walkable(int(self.x), int(new_y)):
                self.y = new_y
            else:
                self.wander_direction[1] = -self.wander_direction[1]
    
    def is_alive(self) -> bool:
        """Check if rabbit is alive."""
        return self.health > 0
    
    def draw(self, surface: pygame.Surface, camera_x: int, camera_y: int):
        """Draw the cute mad rabbit."""
        screen_x = int(self.x * config.TILE_SIZE - camera_x)
        screen_y = int(self.y * config.TILE_SIZE - camera_y)
        center_x = screen_x + config.TILE_SIZE // 2
        center_y = screen_y + config.TILE_SIZE // 2
        
        # Hopping animation
        hop = abs(math.sin(self.hop_timer * 0.15)) * 6
        center_y -= int(hop)
        
        # Draw body (round cute rabbit)
        pygame.draw.circle(surface, self.color, (center_x, center_y + 2), self.size // 2)
        
        # Draw fluffy chest
        chest_color = tuple(min(255, c + 40) for c in self.color)
        pygame.draw.circle(surface, chest_color, (center_x, center_y + 4), self.size // 3)
        
        # Draw head
        head_y = center_y - self.size // 3
        pygame.draw.circle(surface, self.color, (center_x, head_y), self.size // 3)
        
        # Draw long rabbit ears
        ear_offset = self.size // 5
        ear_length = 10
        ear_wiggle = math.sin(self.hop_timer * 0.1) * 2
        # Left ear
        pygame.draw.ellipse(surface, self.color,
                          (center_x - ear_offset - 3, head_y - ear_length - 5 + int(ear_wiggle), 6, ear_length))
        # Right ear
        pygame.draw.ellipse(surface, self.color,
                          (center_x + ear_offset - 3, head_y - ear_length - 5 - int(ear_wiggle), 6, ear_length))
        # Inner ear details
        pygame.draw.ellipse(surface, config.PINK,
                          (center_x - ear_offset - 2, head_y - ear_length - 3 + int(ear_wiggle), 4, ear_length - 3))
        pygame.draw.ellipse(surface, config.PINK,
                          (center_x + ear_offset - 2, head_y - ear_length - 3 - int(ear_wiggle), 4, ear_length - 3))
        
        # Draw cute eyes
        pygame.draw.circle(surface, config.BLACK, (center_x - 4, head_y), 3)
        pygame.draw.circle(surface, config.BLACK, (center_x + 4, head_y), 3)
        # Eye shine
        pygame.draw.circle(surface, config.WHITE, (center_x - 3, head_y - 1), 1)
        pygame.draw.circle(surface, config.WHITE, (center_x + 5, head_y - 1), 1)
        
        # Draw pink nose
        pygame.draw.circle(surface, config.PINK, (center_x, head_y + 4), 2)
        
        # Draw whiskers
        whisker_color = tuple(max(0, c - 50) for c in self.color)
        pygame.draw.line(surface, whisker_color, (center_x, head_y + 3), (center_x - 8, head_y + 2), 1)
        pygame.draw.line(surface, whisker_color, (center_x, head_y + 3), (center_x - 8, head_y + 4), 1)
        pygame.draw.line(surface, whisker_color, (center_x, head_y + 3), (center_x + 8, head_y + 2), 1)
        pygame.draw.line(surface, whisker_color, (center_x, head_y + 3), (center_x + 8, head_y + 4), 1)
        
        # Draw cute fluffy tail
        tail_x = center_x - self.size // 2 - 2
        tail_y = center_y + 5
        pygame.draw.circle(surface, chest_color, (tail_x, tail_y), 5)
        
        # Draw health bar
        self._draw_health_bar(surface, screen_x, screen_y, 3)
    
    def _draw_health_bar(self, surface: pygame.Surface, screen_x: int, screen_y: int, max_health: int):
        """Draw health bar above enemy."""
        bar_width = config.TILE_SIZE
        bar_height = 4
        bar_x = screen_x
        bar_y = screen_y - 8
        
        # Background (black)
        pygame.draw.rect(surface, config.BLACK, (bar_x, bar_y, bar_width, bar_height))
        
        # Health bar color based on health percentage
        health_percent = self.health / max_health
        if health_percent > 0.6:
            bar_color = (0, 255, 0)  # Green
        elif health_percent > 0.3:
            bar_color = (255, 255, 0)  # Yellow
        else:
            bar_color = (255, 0, 0)  # Red
        
        # Draw filled portion
        filled_width = int(bar_width * health_percent)
        if filled_width > 0:
            pygame.draw.rect(surface, bar_color, (bar_x, bar_y, filled_width, bar_height))


class Item(Entity):
    """Base class for collectible items."""
    
    def __init__(self, x: float, y: float, color: Tuple[int, int, int], item_type: str):
        super().__init__(x, y, color)
        self.item_type = item_type
        self.size = config.TILE_SIZE - 8
    
    def draw(self, surface: pygame.Surface, camera_x: int, camera_y: int):
        """Draw the item with a special effect."""
        screen_x = int(self.x * config.TILE_SIZE - camera_x)
        screen_y = int(self.y * config.TILE_SIZE - camera_y)
        
        # Pulsing effect
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.003))
        size_offset = int(pulse * 4)
        
        pygame.draw.circle(surface, self.color,
                          (screen_x + config.TILE_SIZE // 2, screen_y + config.TILE_SIZE // 2),
                          self.size // 2 + size_offset)
        pygame.draw.circle(surface, config.WHITE,
                          (screen_x + config.TILE_SIZE // 2, screen_y + config.TILE_SIZE // 2),
                          self.size // 2 + size_offset, 2)


class Coin(Item):
    """Collectible coin."""
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, config.COIN_COLOR, "coin")
    
    def draw(self, surface: pygame.Surface, camera_x: int, camera_y: int):
        """Draw coin with spinning animation."""
        screen_x = int(self.x * config.TILE_SIZE - camera_x)
        screen_y = int(self.y * config.TILE_SIZE - camera_y)
        center_x = screen_x + config.TILE_SIZE // 2
        center_y = screen_y + config.TILE_SIZE // 2
        
        # Spinning effect
        spin = abs(math.sin(pygame.time.get_ticks() * 0.003 + self.x + self.y))
        width = int(10 * spin + 3)
        
        # Draw coin (ellipse for 3D effect)
        pygame.draw.ellipse(surface, self.color,
                           (center_x - width // 2, center_y - 8, width, 16))
        pygame.draw.ellipse(surface, (200, 180, 0),
                           (center_x - width // 2, center_y - 8, width, 16), 2)
        
        # Add shine
        if spin > 0.7:
            pygame.draw.circle(surface, config.WHITE, (center_x, center_y - 3), 2)


class Treasure(Item):
    """Collectible treasure."""
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, config.TREASURE_COLOR, "treasure")
        # Velocity for flinging effect
        self.vx = 0.0
        self.vy = 0.0
        self.friction = 0.92  # Slow down over time
    
    def update(self):
        """Update treasure position if it has velocity."""
        if abs(self.vx) > 0.01 or abs(self.vy) > 0.01:
            self.x += self.vx
            self.y += self.vy
            self.vx *= self.friction
            self.vy *= self.friction
        else:
            self.vx = 0
            self.vy = 0
    
    def draw(self, surface: pygame.Surface, camera_x: int, camera_y: int):
        """Draw treasure chest."""
        screen_x = int(self.x * config.TILE_SIZE - camera_x)
        screen_y = int(self.y * config.TILE_SIZE - camera_y)
        center_x = screen_x + config.TILE_SIZE // 2
        center_y = screen_y + config.TILE_SIZE // 2
        
        # Pulsing glow
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.003))
        glow_size = int(pulse * 3)
        
        # Draw chest base
        chest_color = (150, 75, 0)
        pygame.draw.rect(surface, chest_color,
                        (center_x - 8, center_y - 4, 16, 12))
        
        # Draw chest lid
        pygame.draw.rect(surface, (180, 90, 0),
                        (center_x - 8, center_y - 8, 16, 4))
        
        # Draw lock
        pygame.draw.rect(surface, (200, 180, 0),
                        (center_x - 2, center_y - 2, 4, 4))
        
        # Draw glow effect
        if pulse > 0.6:
            pygame.draw.rect(surface, self.color,
                           (center_x - 8 - glow_size, center_y - 8 - glow_size,
                            16 + glow_size * 2, 16 + glow_size * 2), 2)


class Weapon(Item):
    """Collectible weapon."""
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, config.WEAPON_COLOR, "weapon")
    
    def draw(self, surface: pygame.Surface, camera_x: int, camera_y: int):
        """Draw the weapon as a sword."""
        screen_x = int(self.x * config.TILE_SIZE - camera_x)
        screen_y = int(self.y * config.TILE_SIZE - camera_y)
        center_x = screen_x + config.TILE_SIZE // 2
        center_y = screen_y + config.TILE_SIZE // 2
        
        # Rotation animation
        rotation = math.sin(pygame.time.get_ticks() * 0.003) * 30
        
        # Draw sword blade
        blade_length = 16
        handle_length = 6
        
        # Rotate points
        angle_rad = math.radians(rotation - 45)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        
        # Blade tip
        blade_x = center_x + int(blade_length * cos_a)
        blade_y = center_y + int(blade_length * sin_a)
        
        # Draw blade (silver/white)
        pygame.draw.line(surface, (220, 220, 240), (center_x, center_y), (blade_x, blade_y), 4)
        pygame.draw.line(surface, config.WHITE, (center_x, center_y), (blade_x, blade_y), 2)
        
        # Draw crossguard
        cross_x1 = center_x + int(6 * math.cos(angle_rad + math.pi/2))
        cross_y1 = center_y + int(6 * math.sin(angle_rad + math.pi/2))
        cross_x2 = center_x + int(6 * math.cos(angle_rad - math.pi/2))
        cross_y2 = center_y + int(6 * math.sin(angle_rad - math.pi/2))
        pygame.draw.line(surface, (180, 150, 50), (cross_x1, cross_y1), (cross_x2, cross_y2), 3)
        
        # Draw handle
        handle_x = center_x - int(handle_length * cos_a)
        handle_y = center_y - int(handle_length * sin_a)
        pygame.draw.line(surface, (100, 80, 50), (center_x, center_y), (handle_x, handle_y), 4)
        
        # Sparkle effect
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.005))
        if pulse > 0.7:
            pygame.draw.circle(surface, config.WHITE, (blade_x, blade_y), 3)


class BowAndArrow(Item):
    """Collectible bow weapon (enables arrow usage)."""
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, config.BOW_COLOR, "bow")
    
    def draw(self, surface: pygame.Surface, camera_x: int, camera_y: int):
        """Draw the bow with glowing effects."""
        screen_x = int(self.x * config.TILE_SIZE - camera_x)
        screen_y = int(self.y * config.TILE_SIZE - camera_y)
        center_x = screen_x + config.TILE_SIZE // 2
        center_y = screen_y + config.TILE_SIZE // 2
        
        # Floating animation
        center_y += int(math.sin(pygame.time.get_ticks() * 0.004 + self.x) * 3)
        
        # Pulsing animation
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.006))
        glow_size = int(pulse * 8)
        
        # Draw multiple layers of outer glow for more intensity
        for i in range(5):
            radius = 15 + glow_size + 4 - i * 2
            alpha_color = tuple(int(c * (0.4 + pulse * 0.5)) for c in self.color)
            pygame.draw.circle(surface, alpha_color, (center_x, center_y), radius, 2)
        
        # Draw bright inner glow ring
        glow_ring_color = tuple(min(255, int(c * 1.3)) for c in config.BOW_COLOR)
        pygame.draw.circle(surface, glow_ring_color, (center_x, center_y), 
                         18 + int(pulse * 3), 1)
        
        # Draw bow arc with thicker line for visibility
        bow_rect = pygame.Rect(center_x - 8, center_y - 10, 16, 20)
        pygame.draw.arc(surface, config.BOW_COLOR, bow_rect, -0.5, 3.64, 4)
        
        # Draw bowstring
        string_color = (220, 220, 255)  # Brighter string
        pygame.draw.line(surface, string_color,
                       (center_x - 6, center_y - 8),
                       (center_x - 6, center_y + 8), 2)
        
        # Draw arrow on bow with pulsing effect
        arrow_x = center_x - 10 - int(pulse * 3)
        pygame.draw.line(surface, config.ARROW_COLOR,
                       (arrow_x, center_y),
                       (arrow_x + 12, center_y), 2)
        # Arrow head
        pygame.draw.polygon(surface, (200, 200, 220), [
            (arrow_x + 12, center_y),
            (arrow_x + 15, center_y - 2),
            (arrow_x + 15, center_y + 2)
        ])
        
        # Add sparkle effects around the bow
        sparkle_angle = pygame.time.get_ticks() * 0.003
        for i in range(4):
            angle = sparkle_angle + (i * 3.14159 / 2)
            sparkle_x = center_x + int(math.cos(angle) * 22)
            sparkle_y = center_y + int(math.sin(angle) * 22)
            sparkle_size = 2 + int(pulse * 2)
            # Use bow color for sparkles
            sparkle_color = tuple(min(255, int(c * 1.5)) for c in config.BOW_COLOR)
            pygame.draw.circle(surface, sparkle_color, (sparkle_x, sparkle_y), sparkle_size)


class Arrow(Item):
    """Collectible arrow for bow weapon."""
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, config.ARROW_COLOR, "arrow")
    
    def draw(self, surface: pygame.Surface, camera_x: int, camera_y: int):
        """Draw a single arrow item."""
        screen_x = int(self.x * config.TILE_SIZE - camera_x)
        screen_y = int(self.y * config.TILE_SIZE - camera_y)
        center_x = screen_x + config.TILE_SIZE // 2
        center_y = screen_y + config.TILE_SIZE // 2
        
        # Floating animation
        float_offset = math.sin(pygame.time.get_ticks() * 0.003) * 3
        arrow_y = center_y + int(float_offset)
        
        # Draw arrow shaft
        pygame.draw.line(surface, config.ARROW_COLOR,
                       (center_x - 8, arrow_y),
                       (center_x + 8, arrow_y), 2)
        
        # Draw arrow head (triangle)
        pygame.draw.polygon(surface, (180, 180, 180), [
            (center_x + 8, arrow_y),
            (center_x + 12, arrow_y - 3),
            (center_x + 12, arrow_y + 3)
        ])
        
        # Draw feathers
        pygame.draw.line(surface, (200, 50, 50),
                       (center_x - 8, arrow_y - 2),
                       (center_x - 6, arrow_y), 2)
        pygame.draw.line(surface, (200, 50, 50),
                       (center_x - 8, arrow_y + 2),
                       (center_x - 6, arrow_y), 2)


class Heart(Item):
    """Collectible heart for health recovery."""
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, config.HEART_COLOR, "heart")
    
    def draw(self, surface: pygame.Surface, camera_x: int, camera_y: int):
        """Draw heart with pulsing animation."""
        screen_x = int(self.x * config.TILE_SIZE - camera_x)
        screen_y = int(self.y * config.TILE_SIZE - camera_y)
        center_x = screen_x + config.TILE_SIZE // 2
        center_y = screen_y + config.TILE_SIZE // 2
        
        # Pulsing animation
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.006))
        size_scale = 1.0 + pulse * 0.2
        
        # Floating animation
        float_offset = int(math.sin(pygame.time.get_ticks() * 0.004) * 3)
        center_y += float_offset
        
        # Draw heart shape
        base_size = 8
        heart_size = int(base_size * size_scale)
        
        # Left half of heart
        pygame.draw.circle(surface, self.color, 
                         (center_x - heart_size // 2, center_y - heart_size // 3), 
                         heart_size // 2)
        # Right half of heart
        pygame.draw.circle(surface, self.color, 
                         (center_x + heart_size // 2, center_y - heart_size // 3), 
                         heart_size // 2)
        # Bottom triangle of heart
        heart_points = [
            (center_x - heart_size, center_y - heart_size // 3),
            (center_x + heart_size, center_y - heart_size // 3),
            (center_x, center_y + heart_size)
        ]
        pygame.draw.polygon(surface, self.color, heart_points)
        
        # Add shine effect
        shine_color = (255, 150, 180)
        pygame.draw.circle(surface, shine_color, 
                         (center_x - heart_size // 4, center_y - heart_size // 2), 
                         2)
        
        # Glow effect when pulsing
        if pulse > 0.7:
            glow_size = int(heart_size * 1.5)
            pygame.draw.circle(surface, (255, 100, 150), (center_x, center_y), 
                             glow_size, 1)


class Door(Entity):
    """Door entity - can be teleport door or secret room door."""
    
    def __init__(self, x: float, y: float, door_type: str = "teleport"):
        # door_type can be "teleport", "secret", or "return"
        if door_type == "teleport":
            color = (128, 0, 128)  # Purple for teleport doors (hidden hallway shortcuts)
        elif door_type == "secret":
            color = config.SECRET_DOOR_COLOR  # Grey for secret room entrance doors
        else:  # "return"
            color = (101, 67, 33)  # Brown/wooden for return doors (exit from hidden rooms)
        super().__init__(x, y, color)
        self.door_type = door_type
        self.linked_secret_room_index: Optional[int] = None  # Which secret room this door leads to
        self.is_return_door: bool = False  # If true, this door returns to main dungeon
        # For teleport doors:
        self.target_x: Optional[int] = None
        self.target_y: Optional[int] = None
        # Animation state
        self.animation_cycle = 2000  # 2 seconds per open/close cycle
        self.animation_offset = random.randint(0, 2000)  # Random start offset
    
    def draw(self, surface: pygame.Surface, camera_x: int, camera_y: int):
        """Draw the door with enhanced graphics and opening/closing animation."""
        screen_x = int(self.x * config.TILE_SIZE - camera_x)
        screen_y = int(self.y * config.TILE_SIZE - camera_y)
        center_x = screen_x + config.TILE_SIZE // 2
        center_y = screen_y + config.TILE_SIZE // 2
        
        # Calculate opening animation (0.0 = closed, 1.0 = fully open)
        time = (pygame.time.get_ticks() + self.animation_offset) % self.animation_cycle
        if time < self.animation_cycle / 2:
            # Opening phase
            open_amount = time / (self.animation_cycle / 2)
        else:
            # Closing phase
            open_amount = 1.0 - (time - self.animation_cycle / 2) / (self.animation_cycle / 2)
        
        # Apply easing for smoother animation
        open_amount = open_amount * open_amount * (3.0 - 2.0 * open_amount)  # Smoothstep
        
        if self.door_type == "teleport":
            # Teleport door - PURPLE with glowing effect and opening animation
            # Door splits open from center
            door_width = int((self.size - 8) * (1.0 - open_amount * 0.7))
            left_x = center_x - door_width // 2
            
            pygame.draw.rect(surface, self.color,
                           (left_x, screen_y + 4, door_width, self.size - 4))
            # Mystical purple glow
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.003))
            glow_color = (int(150 + pulse * 80), 0, int(150 + pulse * 80))
            pygame.draw.rect(surface, glow_color,
                           (left_x, screen_y + 4, door_width, self.size - 4), 2)
            # Inner sparkle (brightest when open)
            sparkle_intensity = int(150 + open_amount * 50 + pulse * 55)
            sparkle_color = (sparkle_intensity, int(100 + pulse * 100), sparkle_intensity)
            pygame.draw.circle(surface, sparkle_color, (center_x, center_y), int(3 + pulse * 2 + open_amount * 2))
            
        elif self.door_type == "secret":
            # Secret room entrance door - GREY with shimmer and sliding animation
            door_height = int((self.size - 8) * (1.0 - open_amount * 0.7))
            top_y = screen_y + 4 + int((self.size - 8 - door_height) / 2)
            
            pygame.draw.rect(surface, self.color,
                           (screen_x + 4, top_y, self.size - 4, door_height))
            # Shimmer effect (more visible when opening)
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.004))
            shimmer_intensity = int(130 + pulse * 60 + open_amount * 40)
            shimmer_color = (shimmer_intensity, shimmer_intensity, shimmer_intensity)
            pygame.draw.rect(surface, shimmer_color,
                           (screen_x + 4, top_y, self.size - 4, door_height), 2)
            # Add mystical particles when open
            if open_amount > 0.5:
                particle_alpha = int(open_amount * 150)
                particle_color = (shimmer_intensity, shimmer_intensity, shimmer_intensity)
                for i in range(3):
                    offset = int(math.sin(pygame.time.get_ticks() * 0.005 + i) * 4)
                    pygame.draw.circle(surface, particle_color, 
                                     (center_x - 8 + i * 8, center_y + offset), 2)
                    
        else:
            # Return door - BROWN/WOODEN appearance with traditional door swing
            # Door swings open from left side
            door_width = int((self.size - 12) * (1.0 - open_amount * 0.6))
            
            # Door panel
            pygame.draw.rect(surface, (101, 67, 33),
                           (screen_x + 6, screen_y + 4, door_width, self.size - 4))
            # Door frame (always visible)
            pygame.draw.rect(surface, (100, 50, 0),
                           (screen_x + 6, screen_y + 4, self.size - 8, self.size - 4), 2)
            # Wood grain (only on door panel)
            if door_width > 10:
                for i in range(3):
                    pygame.draw.line(surface, (120, 60, 0),
                                   (screen_x + 8, screen_y + 10 + i * 8),
                                   (screen_x + 6 + door_width - 2, screen_y + 10 + i * 8), 1)
            # Door handle (moves with door)
            if door_width > 6:
                handle_x = screen_x + 6 + door_width - 4
                pygame.draw.circle(surface, (180, 150, 50),
                                 (handle_x, center_y), 3)
            # Show light coming through when open
            if open_amount > 0.3:
                light_intensity = int(open_amount * 100)
                light_color = (light_intensity + 155, light_intensity + 155, light_intensity + 50)
                light_width = int((self.size - 12 - door_width))
                if light_width > 0:
                    pygame.draw.rect(surface, light_color,
                                   (screen_x + 6 + door_width, screen_y + 6, light_width, self.size - 8))


class Exit(Entity):
    """Exit door."""
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, config.EXIT_COLOR)
    
    def draw(self, surface: pygame.Surface, camera_x: int, camera_y: int):
        """Draw the exit with an enhanced glowing portal effect."""
        screen_x = int(self.x * config.TILE_SIZE - camera_x)
        screen_y = int(self.y * config.TILE_SIZE - camera_y)
        center_x = screen_x + config.TILE_SIZE // 2
        center_y = screen_y + config.TILE_SIZE // 2
        
        # Glowing animation
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.005))
        
        # Draw multiple layers for glow effect
        for i in range(3):
            alpha = 255 - i * 60
            size = self.size // 2 - i * 3
            glow_color = tuple(int(c * (0.7 + pulse * 0.3)) for c in self.color)
            pygame.draw.circle(surface, glow_color, (center_x, center_y), size + int(pulse * 4))
        
        # Draw portal center
        pygame.draw.circle(surface, (150, 255, 150), (center_x, center_y), 8)
        pygame.draw.circle(surface, (200, 255, 200), (center_x, center_y), 5)
        
        # Draw swirling particles
        for i in range(4):
            angle = pygame.time.get_ticks() * 0.003 + i * math.pi / 2
            particle_x = center_x + int(math.cos(angle) * (10 + pulse * 3))
            particle_y = center_y + int(math.sin(angle) * (10 + pulse * 3))
            pygame.draw.circle(surface, (200, 255, 200), (particle_x, particle_y), 2)
        
        # Outer ring
        pygame.draw.circle(surface, self.color, (center_x, center_y), 
                          self.size // 2 + int(pulse * 5), 2)


class PowerUp(Item):
    """Base class for power-up items."""
    
    def __init__(self, x: float, y: float, color: Tuple[int, int, int], powerup_type: str):
        """
        Initialize a power-up.
        
        Args:
            x: X position in tiles
            y: Y position in tiles
            color: RGB color tuple
            powerup_type: Type identifier string
        """
        super().__init__(x, y, color, powerup_type)
        self.size = config.TILE_SIZE - 10
    
    def draw(self, surface: pygame.Surface, camera_x: int, camera_y: int):
        """Draw power-up with distinctive visual effect."""
        screen_x = int(self.x * config.TILE_SIZE - camera_x)
        screen_y = int(self.y * config.TILE_SIZE - camera_y)
        center_x = screen_x + config.TILE_SIZE // 2
        center_y = screen_y + config.TILE_SIZE // 2
        
        # Floating animation
        float_offset = int(math.sin(pygame.time.get_ticks() * 0.004 + self.x) * 3)
        center_y += float_offset
        
        # Pulsing glow
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.005))
        glow_size = int(pulse * 6)
        
        # Draw outer glow
        for i in range(3):
            radius = self.size // 2 + glow_size - i * 2
            alpha_color = tuple(int(c * (0.3 + pulse * 0.4)) for c in self.color)
            pygame.draw.circle(surface, alpha_color, (center_x, center_y), radius, 2)
        
        # Draw main circle
        pygame.draw.circle(surface, self.color, (center_x, center_y), self.size // 2)
        pygame.draw.circle(surface, config.WHITE, (center_x, center_y), self.size // 2, 2)


class SpeedBoost(PowerUp):
    """Speed boost power-up."""
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, config.SPEED_BOOST_COLOR, "speed_boost")
    
    def draw(self, surface: pygame.Surface, camera_x: int, camera_y: int):
        """Draw speed boost with lightning bolt symbol."""
        super().draw(surface, camera_x, camera_y)
        
        screen_x = int(self.x * config.TILE_SIZE - camera_x)
        screen_y = int(self.y * config.TILE_SIZE - camera_y)
        center_x = screen_x + config.TILE_SIZE // 2
        center_y = screen_y + config.TILE_SIZE // 2 + int(math.sin(pygame.time.get_ticks() * 0.004 + self.x) * 3)
        
        # Draw lightning bolt symbol
        bolt_points = [
            (center_x, center_y - 8),
            (center_x - 3, center_y),
            (center_x + 2, center_y),
            (center_x - 2, center_y + 8)
        ]
        pygame.draw.lines(surface, (255, 255, 255), False, bolt_points, 3)


class SpeedPill(PowerUp):
    """Speed pill power-up - increases speed for 4 seconds."""
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, config.SPEED_PILL_COLOR, "speed_pill")
    
    def draw(self, surface: pygame.Surface, camera_x: int, camera_y: int):
        """Draw speed pill as a sphere with lightning bolt graphic."""
        screen_x = int(self.x * config.TILE_SIZE - camera_x)
        screen_y = int(self.y * config.TILE_SIZE - camera_y)
        center_x = screen_x + config.TILE_SIZE // 2
        center_y = screen_y + config.TILE_SIZE // 2 + int(math.sin(pygame.time.get_ticks() * 0.004 + self.x) * 3)
        
        # Draw pulsing glow with enhanced intensity
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.006))
        glow_size = int(pulse * 8)
        
        # Draw multiple layers of outer glow for more intensity
        for i in range(5):
            radius = self.size // 2 + glow_size + 4 - i * 2
            alpha_color = tuple(int(c * (0.4 + pulse * 0.5)) for c in self.color)
            pygame.draw.circle(surface, alpha_color, (center_x, center_y), radius, 2)
        
        # Draw bright inner glow ring
        glow_ring_color = (255, 180, 50)  # Bright yellow-orange glow
        pygame.draw.circle(surface, glow_ring_color, (center_x, center_y), 
                         self.size // 2 + 3 + int(pulse * 3), 1)
        
        # Draw main sphere (with gradient effect using circles)
        pygame.draw.circle(surface, self.color, (center_x, center_y), self.size // 2)
        # Lighter top for 3D effect
        lighter_color = (255, 200, 100)  # Bright yellow-orange highlight
        pygame.draw.circle(surface, lighter_color, (center_x - 3, center_y - 3), self.size // 4)
        # White shine
        pygame.draw.circle(surface, config.WHITE, (center_x - 4, center_y - 4), 3)
        
        # Draw black lightning bolt symbol inside sphere
        bolt_points = [
            (center_x + 1, center_y - 6),
            (center_x - 2, center_y),
            (center_x + 3, center_y),
            (center_x - 1, center_y + 6)
        ]
        pygame.draw.lines(surface, config.BLACK, False, bolt_points, 3)
        
        # Add sparkle effects around the sphere
        sparkle_angle = pygame.time.get_ticks() * 0.003
        for i in range(4):
            angle = sparkle_angle + (i * 3.14159 / 2)
            sparkle_x = center_x + int(math.cos(angle) * (self.size // 2 + 8))
            sparkle_y = center_y + int(math.sin(angle) * (self.size // 2 + 8))
            sparkle_size = 2 + int(pulse * 2)
            pygame.draw.circle(surface, (255, 255, 100), (sparkle_x, sparkle_y), sparkle_size)
        
        # Draw outline
        pygame.draw.circle(surface, (255, 200, 0), (center_x, center_y), self.size // 2, 2)


class Shield(PowerUp):
    """Shield power-up."""
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, config.SHIELD_COLOR, "shield")
    
    def draw(self, surface: pygame.Surface, camera_x: int, camera_y: int):
        """Draw shield with shield symbol."""
        super().draw(surface, camera_x, camera_y)
        
        screen_x = int(self.x * config.TILE_SIZE - camera_x)
        screen_y = int(self.y * config.TILE_SIZE - camera_y)
        center_x = screen_x + config.TILE_SIZE // 2
        center_y = screen_y + config.TILE_SIZE // 2 + int(math.sin(pygame.time.get_ticks() * 0.004 + self.x) * 3)
        
        # Draw shield shape
        shield_points = [
            (center_x, center_y - 8),
            (center_x + 6, center_y - 4),
            (center_x + 6, center_y + 2),
            (center_x, center_y + 8),
            (center_x - 6, center_y + 2),
            (center_x - 6, center_y - 4)
        ]
        pygame.draw.polygon(surface, config.WHITE, shield_points, 2)


class DoublePoints(PowerUp):
    """Double points power-up."""
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, config.DOUBLE_POINTS_COLOR, "double_points")
    
    def draw(self, surface: pygame.Surface, camera_x: int, camera_y: int):
        """Draw double points with x2 symbol."""
        super().draw(surface, camera_x, camera_y)
        
        screen_x = int(self.x * config.TILE_SIZE - camera_x)
        screen_y = int(self.y * config.TILE_SIZE - camera_y)
        center_x = screen_x + config.TILE_SIZE // 2
        center_y = screen_y + config.TILE_SIZE // 2 + int(math.sin(pygame.time.get_ticks() * 0.004 + self.x) * 3)
        
        # Draw x2 text
        font = pygame.font.Font(None, 20)
        text = font.render("x2", True, config.WHITE)
        text_rect = text.get_rect(center=(center_x, center_y))
        surface.blit(text, text_rect)


class VisionBoost(PowerUp):
    """Vision boost power-up."""
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, config.VISION_BOOST_COLOR, "vision_boost")
    
    def draw(self, surface: pygame.Surface, camera_x: int, camera_y: int):
        """Draw vision boost with eye symbol."""
        super().draw(surface, camera_x, camera_y)
        
        screen_x = int(self.x * config.TILE_SIZE - camera_x)
        screen_y = int(self.y * config.TILE_SIZE - camera_y)
        center_x = screen_x + config.TILE_SIZE // 2
        center_y = screen_y + config.TILE_SIZE // 2 + int(math.sin(pygame.time.get_ticks() * 0.004 + self.x) * 3)
        
        # Draw eye symbol
        pygame.draw.ellipse(surface, config.WHITE, (center_x - 6, center_y - 4, 12, 8), 2)
        pygame.draw.circle(surface, config.WHITE, (center_x, center_y), 3)


# New Items: Gems, Scrolls, Artifacts

class Gem(Item):
    """Base class for collectible gems with animation."""
    
    def __init__(self, x: float, y: float, color: Tuple[int, int, int], gem_type: str, value: int):
        super().__init__(x, y, color, f"gem_{gem_type}")
        self.gem_type = gem_type
        self.value = value
    
    def draw(self, surface: pygame.Surface, camera_x: int, camera_y: int):
        """Draw animated gem with sparkles."""
        screen_x = int(self.x * config.TILE_SIZE - camera_x)
        screen_y = int(self.y * config.TILE_SIZE - camera_y)
        center_x = screen_x + config.TILE_SIZE // 2
        center_y = screen_y + config.TILE_SIZE // 2
        
        # Floating animation
        float_offset = int(math.sin(pygame.time.get_ticks() * 0.003 + self.x) * 4)
        center_y += float_offset
        
        # Rotation for sparkle effect
        rotation = pygame.time.get_ticks() * 0.002
        
        # Draw gem as diamond shape
        size = 10
        points = [
            (center_x, center_y - size),  # Top
            (center_x + size // 2, center_y),  # Right
            (center_x, center_y + size),  # Bottom
            (center_x - size // 2, center_y)  # Left
        ]
        pygame.draw.polygon(surface, self.color, points)
        
        # Add shine/highlight
        lighter_color = tuple(min(255, c + 80) for c in self.color)
        shine_points = [
            (center_x, center_y - size // 2),
            (center_x + size // 4, center_y),
            (center_x, center_y + size // 2),
            (center_x - size // 4, center_y)
        ]
        pygame.draw.polygon(surface, lighter_color, shine_points)
        
        # Draw sparkles around gem
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.005))
        for i in range(4):
            angle = rotation + (i * 3.14159 / 2)
            sparkle_dist = 15 + int(pulse * 3)
            sparkle_x = center_x + int(math.cos(angle) * sparkle_dist)
            sparkle_y = center_y + int(math.sin(angle) * sparkle_dist)
            pygame.draw.circle(surface, config.WHITE, (sparkle_x, sparkle_y), 2)
        
        # Draw outline
        pygame.draw.polygon(surface, config.WHITE, points, 2)


class RubyGem(Gem):
    """Ruby gem - highest value."""
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, config.GEM_RUBY_COLOR, "ruby", config.GEM_RUBY_VALUE)


class EmeraldGem(Gem):
    """Emerald gem - medium value."""
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, config.GEM_EMERALD_COLOR, "emerald", config.GEM_EMERALD_VALUE)


class SapphireGem(Gem):
    """Sapphire gem - lower value."""
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, config.GEM_SAPPHIRE_COLOR, "sapphire", config.GEM_SAPPHIRE_VALUE)


class FreezeScroll(Item):
    """Freeze scroll - freezes all enemies for a duration."""
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, config.FREEZE_SCROLL_COLOR, "freeze_scroll")
        # Velocity for flinging effect
        self.vx = 0.0
        self.vy = 0.0
        self.friction = 0.92  # Slow down over time
    
    def update(self):
        """Update scroll position if it has velocity."""
        if abs(self.vx) > 0.01 or abs(self.vy) > 0.01:
            self.x += self.vx
            self.y += self.vy
            self.vx *= self.friction
            self.vy *= self.friction
        else:
            self.vx = 0
            self.vy = 0
    
    def draw(self, surface: pygame.Surface, camera_x: int, camera_y: int):
        """Draw animated scroll with ice particles."""
        screen_x = int(self.x * config.TILE_SIZE - camera_x)
        screen_y = int(self.y * config.TILE_SIZE - camera_y)
        center_x = screen_x + config.TILE_SIZE // 2
        center_y = screen_y + config.TILE_SIZE // 2
        
        # Floating animation
        float_offset = int(math.sin(pygame.time.get_ticks() * 0.004 + self.x) * 3)
        center_y += float_offset
        
        # Draw scroll (parchment)
        scroll_color = (230, 230, 180)
        pygame.draw.rect(surface, scroll_color, (center_x - 8, center_y - 10, 16, 20))
        pygame.draw.rect(surface, (180, 180, 140), (center_x - 8, center_y - 10, 16, 20), 2)
        
        # Draw ice crystal symbol
        crystal_color = self.color
        # Vertical line
        pygame.draw.line(surface, crystal_color, (center_x, center_y - 6), (center_x, center_y + 6), 2)
        # Horizontal line
        pygame.draw.line(surface, crystal_color, (center_x - 5, center_y), (center_x + 5, center_y), 2)
        # Diagonals
        pygame.draw.line(surface, crystal_color, (center_x - 4, center_y - 4), (center_x + 4, center_y + 4), 1)
        pygame.draw.line(surface, crystal_color, (center_x - 4, center_y + 4), (center_x + 4, center_y - 4), 1)
        
        # Ice particles floating around
        pulse = pygame.time.get_ticks() * 0.003
        for i in range(3):
            angle = pulse + (i * 2.1)
            particle_x = center_x + int(math.cos(angle) * 12)
            particle_y = center_y + int(math.sin(angle) * 12)
            pygame.draw.circle(surface, self.color, (particle_x, particle_y), 2)


class ProtectionShield(Item):
    """Protection shield - absorbs 10 hits from enemies or wizards."""
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, config.SHIELD_COLOR, "protection_shield")
        # Velocity for flinging effect
        self.vx = 0.0
        self.vy = 0.0
        self.friction = 0.92  # Slow down over time
    
    def update(self):
        """Update shield position if it has velocity."""
        if abs(self.vx) > 0.01 or abs(self.vy) > 0.01:
            self.x += self.vx
            self.y += self.vy
            self.vx *= self.friction
            self.vy *= self.friction
        else:
            self.vx = 0
            self.vy = 0
    
    def draw(self, surface: pygame.Surface, camera_x: int, camera_y: int):
        """Draw animated shield with protective appearance."""
        screen_x = int(self.x * config.TILE_SIZE - camera_x)
        screen_y = int(self.y * config.TILE_SIZE - camera_y)
        center_x = screen_x + config.TILE_SIZE // 2
        center_y = screen_y + config.TILE_SIZE // 2
        
        # Floating animation
        float_offset = int(math.sin(pygame.time.get_ticks() * 0.004 + self.x) * 3)
        center_y += float_offset
        
        # Pulsing glow effect
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.005))
        glow_radius = 14 + int(pulse * 4)
        glow_color = tuple(min(255, c + int(50 * pulse)) for c in self.color)
        pygame.draw.circle(surface, glow_color, (center_x, center_y), glow_radius, 2)
        
        # Draw shield shape (medieval style)
        shield_points = [
            (center_x, center_y - 10),  # Top point
            (center_x + 8, center_y - 6),  # Top right
            (center_x + 8, center_y + 4),  # Bottom right
            (center_x, center_y + 12),  # Bottom point
            (center_x - 8, center_y + 4),  # Bottom left
            (center_x - 8, center_y - 6)   # Top left
        ]
        pygame.draw.polygon(surface, self.color, shield_points)
        pygame.draw.polygon(surface, config.WHITE, shield_points, 2)
        
        # Draw cross emblem on shield
        pygame.draw.line(surface, config.WHITE, (center_x, center_y - 6), (center_x, center_y + 6), 2)
        pygame.draw.line(surface, config.WHITE, (center_x - 4, center_y), (center_x + 4, center_y), 2)
        
        # Sparkle effects
        time_offset = pygame.time.get_ticks() * 0.006
        for i in range(3):
            angle = time_offset + (i * 2.1)
            sparkle_x = center_x + int(math.cos(angle) * 16)
            sparkle_y = center_y + int(math.sin(angle) * 16)
            pygame.draw.circle(surface, config.WHITE, (sparkle_x, sparkle_y), 2)


class Artifact(Item):
    """Base class for rare artifacts with special powers."""
    
    def __init__(self, x: float, y: float, artifact_type: str):
        super().__init__(x, y, config.ARTIFACT_COLOR, f"artifact_{artifact_type}")
        self.artifact_type = artifact_type
    
    def draw(self, surface: pygame.Surface, camera_x: int, camera_y: int):
        """Draw animated artifact with glowing effect."""
        screen_x = int(self.x * config.TILE_SIZE - camera_x)
        screen_y = int(self.y * config.TILE_SIZE - camera_y)
        center_x = screen_x + config.TILE_SIZE // 2
        center_y = screen_y + config.TILE_SIZE // 2
        
        # Floating animation
        float_offset = int(math.sin(pygame.time.get_ticks() * 0.003 + self.x) * 5)
        center_y += float_offset
        
        # Pulsing glow
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.004))
        glow_size = int(pulse * 6)
        
        # Draw multiple glow layers
        for i in range(4):
            radius = 12 + glow_size - i * 2
            alpha_color = tuple(int(c * (0.5 + pulse * 0.5)) for c in self.color)
            pygame.draw.circle(surface, alpha_color, (center_x, center_y), radius, 1)
        
        # Draw artifact center (star shape)
        star_points = []
        for i in range(8):
            angle = (i * 3.14159 / 4) + (pygame.time.get_ticks() * 0.001)
            if i % 2 == 0:
                r = 8
            else:
                r = 4
            x = center_x + int(math.cos(angle) * r)
            y = center_y + int(math.sin(angle) * r)
            star_points.append((x, y))
        
        pygame.draw.polygon(surface, self.color, star_points)
        pygame.draw.polygon(surface, config.WHITE, star_points, 2)
        
        # Draw center circle
        pygame.draw.circle(surface, config.WHITE, (center_x, center_y), 3)


class ArtifactMaxWeapons(Artifact):
    """Artifact that increases max weapons capacity."""
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, "max_weapons")


class ArtifactMaxArrows(Artifact):
    """Artifact that increases max arrows capacity."""
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, "max_arrows")


class ArtifactFullHealth(Artifact):
    """Artifact that restores full health."""
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, "full_health")


class ArtifactEnemyDestroyer(Artifact):
    """Artifact that destroys nearby enemies."""
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, "enemy_destroyer")


class WizardStaff(Item):
    """Wizard staff weapon dropped by Dark Wizard."""
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, config.WIZARD_STAFF_COLOR, "wizard_staff")
    
    def draw(self, surface: pygame.Surface, camera_x: int, camera_y: int):
        """Draw wizard staff with magical effect."""
        screen_x = int(self.x * config.TILE_SIZE - camera_x)
        screen_y = int(self.y * config.TILE_SIZE - camera_y)
        center_x = screen_x + config.TILE_SIZE // 2
        center_y = screen_y + config.TILE_SIZE // 2
        
        # Floating animation
        float_offset = int(math.sin(pygame.time.get_ticks() * 0.003 + self.x) * 4)
        center_y += float_offset
        
        # Draw staff handle (vertical line)
        pygame.draw.line(surface, (101, 67, 33), 
                        (center_x, center_y + 5), 
                        (center_x, center_y - 8), 4)
        
        # Draw magical orb at top
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.005))
        orb_size = 5 + int(pulse * 2)
        pygame.draw.circle(surface, self.color, (center_x, center_y - 10), orb_size)
        pygame.draw.circle(surface, config.WHITE, (center_x - 2, center_y - 11), 2)
        
        # Magic sparkles
        for i in range(3):
            angle = pygame.time.get_ticks() * 0.003 + (i * 2.1)
            sparkle_x = center_x + int(math.cos(angle) * 10)
            sparkle_y = center_y - 10 + int(math.sin(angle) * 10)
            pygame.draw.circle(surface, self.color, (sparkle_x, sparkle_y), 1)


# New Enemies: Skeleton and Dark Wizard

class ChillinSkeleton(Entity):
    """Skeleton enemy that takes 3 hits to destroy."""
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, config.SKELETON_COLOR)
        self.speed = config.SKELETON_SPEED
        self.health = config.SKELETON_HEALTH
        self.last_attack_time = 0
        self.wander_direction = [random.choice([-1, 0, 1]), random.choice([-1, 0, 1])]
        self.wander_timer = 0
    
    def update(self, player: Player, dungeon_map, current_time: int):
        """Update skeleton AI and movement."""
        # Calculate distance to player
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # Check if player is in detection range
        if distance < config.SKELETON_DETECTION_RANGE / config.TILE_SIZE:
            # Chase player slowly
            if distance > 0.5:
                move_x = (dx / distance) * self.speed * 0.02
                move_y = (dy / distance) * self.speed * 0.02
                
                new_x = self.x + move_x
                new_y = self.y + move_y
                
                if dungeon_map.is_walkable(int(new_x), int(self.y)):
                    self.x = new_x
                if dungeon_map.is_walkable(int(self.x), int(new_y)):
                    self.y = new_y
            
            # Attack if in range
            if distance < config.SKELETON_ATTACK_RANGE / config.TILE_SIZE:
                if current_time - self.last_attack_time > config.SKELETON_ATTACK_COOLDOWN:
                    player.take_damage(config.SKELETON_DAMAGE, current_time)
                    self.last_attack_time = current_time
        else:
            # Wander randomly
            self.wander_timer += 1
            
            if self.wander_timer > 80:
                self.wander_direction = [random.choice([-1, 0, 1]), random.choice([-1, 0, 1])]
                self.wander_timer = 0
            
            move_x = self.wander_direction[0] * self.speed * 0.01
            move_y = self.wander_direction[1] * self.speed * 0.01
            
            new_x = self.x + move_x
            new_y = self.y + move_y
            
            if dungeon_map.is_walkable(int(new_x), int(self.y)):
                self.x = new_x
            else:
                self.wander_direction[0] = -self.wander_direction[0]
            
            if dungeon_map.is_walkable(int(self.x), int(new_y)):
                self.y = new_y
            else:
                self.wander_direction[1] = -self.wander_direction[1]
    
    def is_alive(self) -> bool:
        """Check if skeleton is alive."""
        return self.health > 0
    
    def draw(self, surface: pygame.Surface, camera_x: int, camera_y: int):
        """Draw the chillin' skeleton."""
        screen_x = int(self.x * config.TILE_SIZE - camera_x)
        screen_y = int(self.y * config.TILE_SIZE - camera_y)
        center_x = screen_x + config.TILE_SIZE // 2
        center_y = screen_y + config.TILE_SIZE // 2
        
        # Draw skull (main body)
        pygame.draw.circle(surface, config.SKELETON_BONE_COLOR, (center_x, center_y - 5), 10)
        
        # Draw eye sockets (dark)
        pygame.draw.circle(surface, config.BLACK, (center_x - 4, center_y - 7), 3)
        pygame.draw.circle(surface, config.BLACK, (center_x + 4, center_y - 7), 3)
        
        # Glowing eyes inside sockets
        pygame.draw.circle(surface, config.RED, (center_x - 4, center_y - 7), 1)
        pygame.draw.circle(surface, config.RED, (center_x + 4, center_y - 7), 1)
        
        # Draw nose hole
        pygame.draw.polygon(surface, config.BLACK, [
            (center_x - 1, center_y - 3),
            (center_x + 1, center_y - 3),
            (center_x, center_y - 1)
        ])
        
        # Draw spine/body
        pygame.draw.line(surface, config.SKELETON_COLOR, 
                        (center_x, center_y + 5), 
                        (center_x, center_y + 15), 3)
        
        # Draw ribs
        for i in range(3):
            y_pos = center_y + 7 + i * 3
            pygame.draw.line(surface, config.SKELETON_COLOR,
                           (center_x - 5, y_pos),
                           (center_x + 5, y_pos), 1)
        
        # Draw arms (bones)
        pygame.draw.line(surface, config.SKELETON_COLOR,
                        (center_x - 8, center_y + 5),
                        (center_x - 3, center_y + 10), 2)
        pygame.draw.line(surface, config.SKELETON_COLOR,
                        (center_x + 8, center_y + 5),
                        (center_x + 3, center_y + 10), 2)
        
        # Draw health indicator (cracks on skull based on damage)
        if self.health == 2:
            pygame.draw.line(surface, config.BLACK, 
                           (center_x - 3, center_y - 10), 
                           (center_x + 2, center_y - 5), 1)
        elif self.health == 1:
            pygame.draw.line(surface, config.BLACK, 
                           (center_x - 3, center_y - 10), 
                           (center_x + 2, center_y - 5), 1)
            pygame.draw.line(surface, config.BLACK, 
                           (center_x + 3, center_y - 9), 
                           (center_x - 1, center_y - 6), 1)
        
        # Draw health bar
        self._draw_health_bar(surface, screen_x, screen_y, config.SKELETON_HEALTH)
    
    def _draw_health_bar(self, surface: pygame.Surface, screen_x: int, screen_y: int, max_health: int):
        """Draw health bar above enemy."""
        bar_width = config.TILE_SIZE
        bar_height = 4
        bar_x = screen_x
        bar_y = screen_y - 8
        
        # Background (black)
        pygame.draw.rect(surface, config.BLACK, (bar_x, bar_y, bar_width, bar_height))
        
        # Health bar color based on health percentage
        health_percent = self.health / max_health
        if health_percent > 0.6:
            bar_color = (0, 255, 0)  # Green
        elif health_percent > 0.3:
            bar_color = (255, 255, 0)  # Yellow
        else:
            bar_color = (255, 0, 0)  # Red
        
        # Draw filled portion
        filled_width = int(bar_width * health_percent)
        if filled_width > 0:
            pygame.draw.rect(surface, bar_color, (bar_x, bar_y, filled_width, bar_height))


class WizardBlast(Entity):
    """Projectile shot by Dark Wizard."""
    
    def __init__(self, x: float, y: float, target_x: float, target_y: float):
        super().__init__(x, y, config.WIZARD_BLAST_COLOR)
        self.size = 8
        
        # Calculate direction
        dx = target_x - x
        dy = target_y - y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > 0:
            self.vx = (dx / distance) * config.WIZARD_BLAST_SPEED * 0.02
            self.vy = (dy / distance) * config.WIZARD_BLAST_SPEED * 0.02
        else:
            self.vx = 0
            self.vy = 0
    
    def update(self, dungeon_map):
        """Move the blast."""
        self.x += self.vx
        self.y += self.vy
        
        # Check if hit wall
        return not dungeon_map.is_walkable(int(self.x), int(self.y))
    
    def draw(self, surface: pygame.Surface, camera_x: int, camera_y: int):
        """Draw the magical blast."""
        screen_x = int(self.x * config.TILE_SIZE - camera_x)
        screen_y = int(self.y * config.TILE_SIZE - camera_y)
        center_x = screen_x + config.TILE_SIZE // 2
        center_y = screen_y + config.TILE_SIZE // 2
        
        # Draw pulsing energy ball
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.01))
        size = self.size + int(pulse * 3)
        
        # Outer glow
        pygame.draw.circle(surface, self.color, (center_x, center_y), size)
        # Inner bright core
        pygame.draw.circle(surface, config.WHITE, (center_x, center_y), size // 2)


class DarkWizard(Entity):
    """Dark Wizard enemy that shoots projectiles."""
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, config.WIZARD_COLOR)
        self.speed = config.WIZARD_SPEED
        self.health = config.WIZARD_HEALTH
        self.last_attack_time = 0
        self.wander_direction = [random.choice([-1, 0, 1]), random.choice([-1, 0, 1])]
        self.wander_timer = 0
        self.blasts = []  # Store active projectiles
    
    def update(self, player: Player, dungeon_map, current_time: int):
        """Update wizard AI and movement."""
        # Calculate distance to player
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # Check if player is in detection range
        if distance < config.WIZARD_DETECTION_RANGE / config.TILE_SIZE:
            # Keep distance from player (stay back and shoot)
            if distance < 3:
                # Move away if too close
                move_x = -(dx / distance) * self.speed * 0.02
                move_y = -(dy / distance) * self.speed * 0.02
                
                new_x = self.x + move_x
                new_y = self.y + move_y
                
                if dungeon_map.is_walkable(int(new_x), int(self.y)):
                    self.x = new_x
                if dungeon_map.is_walkable(int(self.x), int(new_y)):
                    self.y = new_y
            
            # Shoot projectile if in range and cooldown expired
            if distance < config.WIZARD_ATTACK_RANGE / config.TILE_SIZE:
                if current_time - self.last_attack_time > config.WIZARD_ATTACK_COOLDOWN:
                    blast = WizardBlast(self.x, self.y, player.x, player.y)
                    self.blasts.append(blast)
                    self.last_attack_time = current_time
        else:
            # Wander randomly
            self.wander_timer += 1
            
            if self.wander_timer > 70:
                self.wander_direction = [random.choice([-1, 0, 1]), random.choice([-1, 0, 1])]
                self.wander_timer = 0
            
            move_x = self.wander_direction[0] * self.speed * 0.01
            move_y = self.wander_direction[1] * self.speed * 0.01
            
            new_x = self.x + move_x
            new_y = self.y + move_y
            
            if dungeon_map.is_walkable(int(new_x), int(self.y)):
                self.x = new_x
            else:
                self.wander_direction[0] = -self.wander_direction[0]
            
            if dungeon_map.is_walkable(int(self.x), int(new_y)):
                self.y = new_y
            else:
                self.wander_direction[1] = -self.wander_direction[1]
        
        # Update all blasts
        self.blasts = [blast for blast in self.blasts if not blast.update(dungeon_map)]
    
    def is_alive(self) -> bool:
        """Check if wizard is alive."""
        return self.health > 0
    
    def draw(self, surface: pygame.Surface, camera_x: int, camera_y: int):
        """Draw the dark wizard (scaled up to match CrazyBear size)."""
        screen_x = int(self.x * config.TILE_SIZE - camera_x)
        screen_y = int(self.y * config.TILE_SIZE - camera_y)
        center_x = screen_x + config.TILE_SIZE // 2
        center_y = screen_y + config.TILE_SIZE // 2
        
        # Floating animation
        float_offset = int(math.sin(pygame.time.get_ticks() * 0.003 + self.x) * 4)
        center_y += float_offset
        
        # Scale factor to match CrazyBear size (1.5x bigger)
        scale = 1.5
        
        # Draw robe (trapezoid) - scaled up
        robe_points = [
            (center_x - int(12 * scale), center_y + int(16 * scale)),
            (center_x + int(12 * scale), center_y + int(16 * scale)),
            (center_x + int(7 * scale), center_y - int(4 * scale)),
            (center_x - int(7 * scale), center_y - int(4 * scale))
        ]
        pygame.draw.polygon(surface, config.WIZARD_ROBE_COLOR, robe_points)
        pygame.draw.polygon(surface, config.WIZARD_COLOR, robe_points, 2)
        
        # Draw hood - scaled up
        pygame.draw.circle(surface, config.WIZARD_COLOR, (center_x, center_y - int(4 * scale)), int(11 * scale))
        
        # Draw dark face (shadowed) - scaled up
        pygame.draw.circle(surface, config.BLACK, (center_x, center_y - int(3 * scale)), int(8 * scale))
        
        # Draw glowing eyes - scaled up
        eye_glow = abs(math.sin(pygame.time.get_ticks() * 0.005))
        eye_color = tuple(int(c * eye_glow) for c in (255, 0, 255))
        pygame.draw.circle(surface, eye_color, (center_x - int(4 * scale), center_y - int(4 * scale)), int(3 * scale))
        pygame.draw.circle(surface, eye_color, (center_x + int(4 * scale), center_y - int(4 * scale)), int(3 * scale))
        
        # Draw wizard staff in hand - scaled up
        pygame.draw.line(surface, (101, 67, 33),
                        (center_x + int(10 * scale), center_y + int(7 * scale)),
                        (center_x + int(16 * scale), center_y - int(10 * scale)), int(4 * scale))
        # Staff orb - scaled up
        pygame.draw.circle(surface, config.WIZARD_STAFF_COLOR, (center_x + int(17 * scale), center_y - int(13 * scale)), int(5 * scale))
        
        # Draw magical aura when damaged
        if self.health < config.WIZARD_HEALTH:
            aura_pulse = abs(math.sin(pygame.time.get_ticks() * 0.008))
            aura_radius = int(20 * scale) + int(aura_pulse * 4)
            pygame.draw.circle(surface, config.WIZARD_ROBE_COLOR, (center_x, center_y), aura_radius, 2)
        
        # Draw health bar
        self._draw_health_bar(surface, screen_x, screen_y, config.WIZARD_HEALTH)
    
    def _draw_health_bar(self, surface: pygame.Surface, screen_x: int, screen_y: int, max_health: int):
        """Draw health bar above enemy."""
        bar_width = config.TILE_SIZE
        bar_height = 4
        bar_x = screen_x
        bar_y = screen_y - 8
        
        # Background (black)
        pygame.draw.rect(surface, config.BLACK, (bar_x, bar_y, bar_width, bar_height))
        
        # Health bar color based on health percentage
        health_percent = self.health / max_health
        if health_percent > 0.6:
            bar_color = (0, 255, 0)  # Green
        elif health_percent > 0.3:
            bar_color = (255, 255, 0)  # Yellow
        else:
            bar_color = (255, 0, 0)  # Red
        
        # Draw filled portion
        filled_width = int(bar_width * health_percent)
        if filled_width > 0:
            pygame.draw.rect(surface, bar_color, (bar_x, bar_y, filled_width, bar_height))

