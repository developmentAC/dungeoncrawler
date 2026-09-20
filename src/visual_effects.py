"""
Visual effects system for particles, damage numbers, combo text, and screen effects.
"""

import pygame
import math
import random
from typing import List, Tuple
import config


class Arrow:
    """Arrow projectile that flies from player to target."""
    
    def __init__(self, start_x: float, start_y: float, target_x: float, target_y: float):
        """
        Initialize an arrow projectile.
        
        Args:
            start_x: Starting x position (player)
            start_y: Starting y position (player)
            target_x: Target x position
            target_y: Target y position
        """
        self.x = start_x
        self.y = start_y
        self.start_x = start_x
        self.start_y = start_y
        self.target_x = target_x
        self.target_y = target_y
        
        # Calculate direction and distance
        dx = target_x - start_x
        dy = target_y - start_y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > 0:
            # Normalize direction
            self.velocity_x = (dx / distance) * 15  # Arrow speed
            self.velocity_y = (dy / distance) * 15
            self.angle = math.atan2(dy, dx)
        else:
            self.velocity_x = 0
            self.velocity_y = 0
            self.angle = 0
        
        self.creation_time = pygame.time.get_ticks()
        self.max_lifetime = 500  # milliseconds
        
    def update(self) -> bool:
        """
        Update arrow position.
        
        Returns:
            True if arrow is still alive, False if expired
        """
        # Check lifetime
        if pygame.time.get_ticks() - self.creation_time > self.max_lifetime:
            return False
        
        # Move arrow
        self.x += self.velocity_x
        self.y += self.velocity_y
        
        # Check if arrow reached or passed target
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance_to_target = math.sqrt(dx * dx + dy * dy)
        
        # Stop if very close to target
        if distance_to_target < 10:
            return False
        
        return True
    
    def draw(self, surface: pygame.Surface, camera_x: int, camera_y: int):
        """
        Draw the arrow.
        
        Args:
            surface: Pygame surface to draw on
            camera_x: Camera x offset
            camera_y: Camera y offset
        """
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        
        # Arrow is a triangle pointing in direction of travel
        arrow_length = 12
        arrow_width = 4
        
        # Calculate arrow tip and tail
        tip_x = screen_x + math.cos(self.angle) * arrow_length
        tip_y = screen_y + math.sin(self.angle) * arrow_length
        
        # Calculate perpendicular offset for arrow wings
        perp_x = -math.sin(self.angle) * arrow_width
        perp_y = math.cos(self.angle) * arrow_width
        
        # Arrow points
        tip = (int(tip_x), int(tip_y))
        left_wing = (int(screen_x + perp_x), int(screen_y + perp_y))
        right_wing = (int(screen_x - perp_x), int(screen_y - perp_y))
        
        # Draw arrow shaft (line)
        pygame.draw.line(surface, (139, 69, 19), (screen_x, screen_y), tip, 2)
        
        # Draw arrow head (triangle)
        pygame.draw.polygon(surface, (200, 200, 200), [tip, left_wing, right_wing])


class Fireball:
    """Fireball projectile from wizard staff - more powerful than arrows."""
    
    def __init__(self, start_x: float, start_y: float, target_x: float, target_y: float):
        """
        Initialize a fireball projectile.
        
        Args:
            start_x: Starting x position (player)
            start_y: Starting y position (player)
            target_x: Target x position
            target_y: Target y position
        """
        self.x = start_x
        self.y = start_y
        self.start_x = start_x
        self.start_y = start_y
        self.target_x = target_x
        self.target_y = target_y
        
        # Calculate direction and distance
        dx = target_x - start_x
        dy = target_y - start_y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > 0:
            # Normalize direction
            self.velocity_x = (dx / distance) * 18  # Faster than arrows
            self.velocity_y = (dy / distance) * 18
            self.angle = math.atan2(dy, dx)
        else:
            self.velocity_x = 0
            self.velocity_y = 0
            self.angle = 0
        
        self.creation_time = pygame.time.get_ticks()
        self.max_lifetime = 600  # milliseconds - slightly longer than arrows
        self.trail_particles = []  # Fire trail effect
        
    def update(self) -> bool:
        """
        Update fireball position.
        
        Returns:
            True if fireball is still alive, False if expired
        """
        # Check lifetime
        if pygame.time.get_ticks() - self.creation_time > self.max_lifetime:
            return False
        
        # Move fireball
        self.x += self.velocity_x
        self.y += self.velocity_y
        
        # Add trail particle
        if random.random() < 0.5:
            self.trail_particles.append({
                'x': self.x,
                'y': self.y,
                'time': pygame.time.get_ticks(),
                'lifetime': 200
            })
        
        # Update trail particles
        self.trail_particles = [p for p in self.trail_particles 
                               if pygame.time.get_ticks() - p['time'] < p['lifetime']]
        
        # Check if fireball reached or passed target
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance_to_target = math.sqrt(dx * dx + dy * dy)
        
        # Stop if very close to target
        if distance_to_target < 15:
            return False
        
        return True
    
    def draw(self, surface: pygame.Surface, camera_x: int, camera_y: int):
        """
        Draw the fireball with flame effects.
        
        Args:
            surface: Pygame surface to draw on
            camera_x: Camera x offset
            camera_y: Camera y offset
        """
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        
        # Draw fire trail
        for particle in self.trail_particles:
            p_screen_x = int(particle['x'] - camera_x)
            p_screen_y = int(particle['y'] - camera_y)
            age = pygame.time.get_ticks() - particle['time']
            alpha = 1.0 - (age / particle['lifetime'])
            
            # Fade from bright yellow to orange to red
            if alpha > 0.7:
                color = (255, 255, int(100 * alpha))  # Bright yellow
            elif alpha > 0.4:
                color = (255, int(165 * alpha), 0)  # Orange
            else:
                color = (int(255 * alpha), 0, 0)  # Red
            
            radius = int(4 * alpha)
            if radius > 0:
                pygame.draw.circle(surface, color, (p_screen_x, p_screen_y), radius)
        
        # Draw main fireball (larger than arrow)
        # Outer glow (orange)
        pygame.draw.circle(surface, (255, 140, 0), (screen_x, screen_y), 10)
        # Inner core (bright yellow)
        pygame.draw.circle(surface, (255, 255, 100), (screen_x, screen_y), 6)
        # Center (white hot)
        pygame.draw.circle(surface, (255, 255, 255), (screen_x, screen_y), 3)


class Particle:
    """Single particle for visual effects."""
    
    def __init__(self, x: float, y: float, color: Tuple[int, int, int], 
                 velocity_x: float, velocity_y: float, lifetime: int):
        """
        Initialize a particle.
        
        Args:
            x: Starting x position
            y: Starting y position
            color: RGB color tuple
            velocity_x: Horizontal velocity
            velocity_y: Vertical velocity
            lifetime: How long the particle lasts in milliseconds
        """
        self.x = x
        self.y = y
        self.color = color
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.lifetime = lifetime
        self.creation_time = pygame.time.get_ticks()
        self.size = random.randint(2, 5)
    
    def update(self) -> bool:
        """
        Update particle position and check if still alive.
        
        Returns:
            True if particle is still alive, False if expired
        """
        # Apply velocity
        self.x += self.velocity_x
        self.y += self.velocity_y
        
        # Apply gravity
        self.velocity_y += 0.2
        
        # Check if expired
        return pygame.time.get_ticks() - self.creation_time < self.lifetime
    
    def draw(self, surface: pygame.Surface, camera_x: int, camera_y: int):
        """Draw the particle with fade effect."""
        # Calculate alpha based on remaining lifetime
        elapsed = pygame.time.get_ticks() - self.creation_time
        alpha = max(0.0, min(1.0, 1.0 - (elapsed / self.lifetime)))  # Clamp alpha to [0, 1]
        
        # Draw particle with fading color (clamp color values to valid range)
        faded_color = tuple(max(0, min(255, int(c * alpha))) for c in self.color)
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        pygame.draw.circle(surface, faded_color, (screen_x, screen_y), 
                          max(1, int(self.size * alpha)))


class DamageNumber:
    """Floating damage number that rises and fades."""
    
    def __init__(self, x: float, y: float, damage: int, color: Tuple[int, int, int]):
        """
        Initialize a damage number.
        
        Args:
            x: Starting x position
            y: Starting y position
            damage: Damage amount to display
            color: RGB color tuple
        """
        self.x = x
        self.y = y
        self.damage = damage
        self.color = color
        self.creation_time = pygame.time.get_ticks()
        self.font = pygame.font.Font(None, config.FONT_MEDIUM)
    
    def update(self) -> bool:
        """
        Update position and check if still alive.
        
        Returns:
            True if still alive, False if expired
        """
        # Rise upward
        self.y -= config.DAMAGE_NUMBER_RISE_SPEED
        
        # Check if expired
        return pygame.time.get_ticks() - self.creation_time < config.DAMAGE_NUMBER_LIFETIME
    
    def draw(self, surface: pygame.Surface, camera_x: int, camera_y: int):
        """Draw the damage number with fade effect."""
        # Calculate alpha (clamped to valid range)
        elapsed = pygame.time.get_ticks() - self.creation_time
        alpha = max(0.0, min(1.0, 1.0 - (elapsed / config.DAMAGE_NUMBER_LIFETIME)))
        
        # Apply fade (clamp color values to valid range)
        faded_color = tuple(max(0, min(255, int(c * alpha))) for c in self.color)
        text = self.font.render(str(self.damage), True, faded_color)
        
        # Draw at world position
        screen_x = int(self.x - camera_x - text.get_width() // 2)
        screen_y = int(self.y - camera_y)
        surface.blit(text, (screen_x, screen_y))


class ComboText:
    """Floating combo text that displays kill streak."""
    
    def __init__(self, combo_count: int):
        """
        Initialize combo text display.
        
        Args:
            combo_count: Number of consecutive kills
        """
        self.combo_count = combo_count
        self.creation_time = pygame.time.get_ticks()
        self.lifetime = 2000  # 2 seconds
        self.font = pygame.font.Font(None, 48)  # Larger font for emphasis
        self.text = f"{combo_count}x COMBO!"
    
    def is_alive(self) -> bool:
        """Check if combo text should still be displayed."""
        return pygame.time.get_ticks() - self.creation_time < self.lifetime
    
    def draw(self, surface: pygame.Surface):
        """Draw the combo text with scaling and fade effect."""
        elapsed = pygame.time.get_ticks() - self.creation_time
        progress = elapsed / self.lifetime
        
        # Scale effect: start large, shrink to normal size
        scale = 1.5 - (0.5 * min(progress, 0.3) / 0.3)  # 1.5x to 1.0x in first 30%
        
        # Fade out in last 50%
        if progress > 0.5:
            alpha = 1.0 - ((progress - 0.5) / 0.5)
        else:
            alpha = 1.0
        
        # Render text with scale
        if scale != 1.0:
            font = pygame.font.Font(None, int(48 * scale))
            text_surface = font.render(self.text, True, config.GOLD)
        else:
            text_surface = self.font.render(self.text, True, config.GOLD)
        
        # Apply alpha
        text_surface.set_alpha(int(255 * alpha))
        
        # Position at top-center of screen (get width from surface)
        x = surface.get_width() // 2 - text_surface.get_width() // 2
        y = 50
        
        # Draw with shadow for visibility
        shadow = self.font.render(self.text, True, (0, 0, 0))
        shadow.set_alpha(int(255 * alpha * 0.5))
        surface.blit(shadow, (x + 2, y + 2))
        surface.blit(text_surface, (x, y))


class VisualEffectsManager:
    """Manages all visual effects in the game."""
    
    def __init__(self):
        """Initialize the effects manager."""
        self.particles: List[Particle] = []
        self.damage_numbers: List[DamageNumber] = []
        self.arrows: List[Arrow] = []
        self.fireballs: List[Fireball] = []
        self.combo_texts: List[ComboText] = []
        self.screen_shake_end_time = 0
        self.shake_offset_x = 0
        self.shake_offset_y = 0
    
    def create_arrow(self, start_x: float, start_y: float, target_x: float, target_y: float):
        """
        Create an arrow projectile.
        
        Args:
            start_x: Starting x position (player)
            start_y: Starting y position (player)
            target_x: Target x position
            target_y: Target y position
        """
        arrow = Arrow(start_x, start_y, target_x, target_y)
        self.arrows.append(arrow)
    
    def create_hit_particles(self, x: float, y: float, color: Tuple[int, int, int], count: int = 10):
        """
        Create particle explosion for hit effects.
        
        Args:
            x: Center x position
            y: Center y position
            color: Particle color
            count: Number of particles to spawn
        """
        for _ in range(count):
            # Random velocity in all directions
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 6)
            vel_x = math.cos(angle) * speed
            vel_y = math.sin(angle) * speed
            
            # Create particle
            particle = Particle(x, y, color, vel_x, vel_y, config.PARTICLE_LIFETIME)
            self.particles.append(particle)
    
    def create_collection_sparkles(self, x: float, y: float, color: Tuple[int, int, int]):
        """
        Create sparkle effect when collecting items.
        
        Args:
            x: Center x position
            y: Center y position
            color: Sparkle color
        """
        for _ in range(8):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 3)
            vel_x = math.cos(angle) * speed
            vel_y = math.sin(angle) * speed - 2  # Upward bias
            
            particle = Particle(x, y, color, vel_x, vel_y, 800)
            self.particles.append(particle)
    
    def create_bow_pickup_effect(self, x: float, y: float):
        """
        Create bright visual effect around player when bow is collected.
        
        Args:
            x: Center x position (player center)
            y: Center y position (player center)
        """
        # Create multiple rings of bright particles
        bright_colors = [
            (255, 255, 100),  # Bright yellow
            (255, 255, 200),  # Brighter yellow-white
            (200, 255, 255),  # Bright cyan
            (255, 200, 100),  # Bright orange
        ]
        
        # Create outer ring burst
        for i in range(24):
            angle = (i / 24.0) * 2 * math.pi
            speed = random.uniform(4, 7)
            vel_x = math.cos(angle) * speed
            vel_y = math.sin(angle) * speed
            color = bright_colors[i % len(bright_colors)]
            
            particle = Particle(x, y, color, vel_x, vel_y, 1200)
            self.particles.append(particle)
        
        # Create inner ring burst
        for i in range(16):
            angle = (i / 16.0) * 2 * math.pi
            speed = random.uniform(2, 4)
            vel_x = math.cos(angle) * speed
            vel_y = math.sin(angle) * speed
            color = bright_colors[i % len(bright_colors)]
            
            particle = Particle(x, y, color, vel_x, vel_y, 1000)
            self.particles.append(particle)
        
        # Create upward sparkles
        for _ in range(20):
            angle = random.uniform(-math.pi / 4, -3 * math.pi / 4)  # Upward cone
            speed = random.uniform(3, 6)
            vel_x = math.cos(angle) * speed
            vel_y = math.sin(angle) * speed
            color = bright_colors[random.randint(0, len(bright_colors) - 1)]
            
            particle = Particle(x, y, color, vel_x, vel_y, 1500)
            self.particles.append(particle)
    
    def create_sword_swirl_effect(self, x: float, y: float):
        """
        Create red swirl effect around player when sword is swung.
        
        Args:
            x: Center x position (player center)
            y: Center y position (player center)
        """
        # Red color variations for the swirl
        red_colors = [
            (255, 0, 0),      # Pure red
            (255, 50, 50),    # Lighter red
            (200, 0, 0),      # Dark red
            (255, 100, 100),  # Pink-red
        ]
        
        # Create circular swirl pattern
        for i in range(18):
            angle = (i / 18.0) * 2 * math.pi
            # Swirl particles move in a circular pattern
            speed = random.uniform(5, 8)
            vel_x = math.cos(angle) * speed
            vel_y = math.sin(angle) * speed
            color = red_colors[i % len(red_colors)]
            
            particle = Particle(x, y, color, vel_x, vel_y, 400)
            self.particles.append(particle)
        
        # Add some faster particles for dynamic effect
        for _ in range(12):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(8, 12)
            vel_x = math.cos(angle) * speed
            vel_y = math.sin(angle) * speed
            color = red_colors[random.randint(0, len(red_colors) - 1)]
            
            particle = Particle(x, y, color, vel_x, vel_y, 300)
            self.particles.append(particle)
    
    def create_freeze_wave_effect(self, x: float, y: float):
        """
        Create blue ice waves emanating from player when freeze scroll is used.
        
        Args:
            x: Center x position (player center)
            y: Center y position (player center)
        """
        # Blue/cyan color variations for ice waves
        ice_colors = [
            (100, 200, 255),  # Light blue
            (150, 220, 255),  # Lighter cyan
            (80, 180, 255),   # Medium blue
            (200, 240, 255),  # Very light blue
            (120, 200, 240),  # Cyan
        ]
        
        # Create multiple expanding wave rings
        for ring in range(4):
            ring_offset = ring * 50  # Stagger the waves
            num_particles = 24 + ring * 6
            
            for i in range(num_particles):
                angle = (i / num_particles) * 2 * math.pi
                # Waves move outward in circular pattern
                speed = random.uniform(6, 9) + ring * 1.5
                vel_x = math.cos(angle) * speed
                vel_y = math.sin(angle) * speed
                color = ice_colors[i % len(ice_colors)]
                
                # Longer lifetime for wave effect
                particle = Particle(x, y, color, vel_x, vel_y, 800 + ring * 100)
                self.particles.append(particle)
        
        # Add swirling ice crystals
        for _ in range(20):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(4, 7)
            vel_x = math.cos(angle) * speed
            vel_y = math.sin(angle) * speed
            color = ice_colors[random.randint(0, len(ice_colors) - 1)]
            
            particle = Particle(x, y, color, vel_x, vel_y, 1000)
            self.particles.append(particle)
    
    def create_damage_number(self, x: float, y: float, damage: int, is_critical: bool = False):
        """
        Create floating damage number.
        
        Args:
            x: Position x
            y: Position y
            damage: Damage amount
            is_critical: Whether this was a critical hit
        """
        color = (255, 255, 0) if is_critical else (255, 100, 100)
        damage_num = DamageNumber(x, y, damage, color)
        self.damage_numbers.append(damage_num)
    
    def create_combo_text(self, combo_count: int):
        """
        Create combo text display for kill streaks.
        
        Args:
            combo_count: Number of consecutive kills
        """
        combo_text = ComboText(combo_count)
        self.combo_texts.append(combo_text)
    
    def trigger_screen_shake(self):
        """Trigger screen shake effect."""
        self.screen_shake_end_time = pygame.time.get_ticks() + config.SCREEN_SHAKE_DURATION
    
    def update(self):
        """Update all visual effects."""
        # Update particles
        self.particles = [p for p in self.particles if p.update()]
        
        # Update damage numbers
        self.damage_numbers = [d for d in self.damage_numbers if d.update()]
        
        # Update arrows
        self.arrows = [a for a in self.arrows if a.update()]
        
        # Update fireballs
        self.fireballs = [f for f in self.fireballs if f.update()]
        
        # Update combo texts
        self.combo_texts = [c for c in self.combo_texts if c.is_alive()]
        
        # Update screen shake
        if pygame.time.get_ticks() < self.screen_shake_end_time:
            # Random shake offset
            self.shake_offset_x = random.randint(-config.SCREEN_SHAKE_INTENSITY, 
                                                 config.SCREEN_SHAKE_INTENSITY)
            self.shake_offset_y = random.randint(-config.SCREEN_SHAKE_INTENSITY, 
                                                 config.SCREEN_SHAKE_INTENSITY)
        else:
            self.shake_offset_x = 0
            self.shake_offset_y = 0
    
    def draw(self, surface: pygame.Surface, camera_x: int, camera_y: int):
        """
        Draw all visual effects.
        
        Args:
            surface: Pygame surface to draw on
            camera_x: Camera x offset
            camera_y: Camera y offset
        """
        # Draw particles
        for particle in self.particles:
            particle.draw(surface, camera_x, camera_y)
        
        # Draw arrows
        for arrow in self.arrows:
            arrow.draw(surface, camera_x, camera_y)
        
        # Draw fireballs
        for fireball in self.fireballs:
            fireball.draw(surface, camera_x, camera_y)
        
        # Draw damage numbers
        for damage_num in self.damage_numbers:
            damage_num.draw(surface, camera_x, camera_y)
        
        # Draw combo texts (screen-space, no camera offset)
        for combo_text in self.combo_texts:
            combo_text.draw(surface)
    
    def get_shake_offset(self) -> Tuple[int, int]:
        """
        Get current screen shake offset.
        
        Returns:
            Tuple of (x_offset, y_offset)
        """
        return (self.shake_offset_x, self.shake_offset_y)
