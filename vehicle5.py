import pygame
import random
import math

pygame.init()

WIDTH, HEIGHT = 800, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Braitenberg Vehicle 5 - Explorer")

pygame.font.init()
font = pygame.font.SysFont("Arial", 16)

clock = pygame.time.Clock()
fps = 120

WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)


MONO = False
FRICTION = True  # Vehicle 5 has some randomness/friction
INHIBITION = False
CROSS = False
EXPLORATION_NOISE = 0.3  # Adds exploratory behavior
MEMORY_DECAY = 0.95  # For interest decay in explored areas
NUM_LIGHTS = 4  # Multiple light sources

def inverse_distance(distance):
    return 1 / max(distance, 1)  

def sinusoid(d):
    x = (math.sin(d / 80) + 1) * 0.5
    return max(0.05, x * 0.8)  # Reduced max response for exploration

def exploration_function(d, interest_level):
    # Vehicle 5's exploration response - combines attraction with curiosity
    base_response = sinusoid(d)
    curiosity_boost = interest_level * 0.5
    return base_response + curiosity_boost

class LightSource:
    def __init__(self, position, radius=25, color=YELLOW, intensity=1.0):
        self.position = pygame.math.Vector2(position)
        self.radius = radius
        self.color = color
        self.intensity = intensity
        self.visited_count = 0  # Track how often this light has been visited

    def draw(self, surface):
        # Draw light with intensity-based brightness
        alpha = int(255 * self.intensity)
        color_with_alpha = (*self.color[:3], alpha)
        
        # Draw outer glow
        for i in range(3):
            glow_radius = self.radius + (i * 10)
            glow_alpha = max(20, alpha // (i + 2))
            glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*self.color[:3], glow_alpha), 
                            (glow_radius, glow_radius), glow_radius)
            surface.blit(glow_surface, 
                        (self.position.x - glow_radius, self.position.y - glow_radius))
        
        # Draw main light
        pygame.draw.circle(surface, self.color, self.position, self.radius)
        
        # Draw visit counter
        text = font.render(str(self.visited_count), True, WHITE)
        surface.blit(text, (self.position.x - 10, self.position.y - 8))

class Vehicle:
    def __init__(self, position, direction, radius=20, color=RED):
        self.position = pygame.math.Vector2(position)
        self.direction = direction
        self.radius = radius
        self.color = color
        
        # Vehicle 5 has reduced speed for more careful exploration
        self.speed_scaling = 1.5
        self.rotation_scaling = 0.8
        
        # Sensor configuration
        self.sensor_radius = 8
        self.sensor_offset = self.radius + self.sensor_radius
        self.sensor_spacing = 40 if not MONO else 0
        
        # Vehicle 5 specific attributes
        self.interest_map = {}  # Track interest in different areas
        self.exploration_timer = 0
        self.last_light_visit = None
        self.visit_threshold = 30  # Distance to consider a light "visited"
        
        self.sensor_color = GREEN
        self.update_sensor_positions()
    
    def update_sensor_positions(self):
        forward = pygame.math.Vector2(0, -1).rotate(self.direction)
        right = forward.rotate(-90)
        
        self.left_sensor_position = (
            self.position + forward * self.sensor_offset - right * (self.sensor_spacing / 2)
        )
        self.right_sensor_position = (
            self.position + forward * self.sensor_offset + right * (self.sensor_spacing / 2)
        )

    def draw(self, surface):
        # Draw vehicle body
        pygame.draw.circle(surface, self.color, self.position, self.radius)
        
        # Draw direction indicator
        forward = pygame.math.Vector2(0, -1).rotate(self.direction)
        end_pos = self.position + forward * (self.radius - 5)
        pygame.draw.circle(surface, WHITE, end_pos, 3)
        
        # Draw sensors
        pygame.draw.circle(surface, self.sensor_color, self.left_sensor_position, self.sensor_radius)
        pygame.draw.circle(surface, self.sensor_color, self.right_sensor_position, self.sensor_radius)
        
        # Draw exploration trail (fading)
        trail_length = min(len(self.trail), 20)
        for i, pos in enumerate(self.trail[-trail_length:]):
            alpha = int(255 * (i / trail_length) * 0.3)
            if alpha > 10:
                trail_surface = pygame.Surface((4, 4), pygame.SRCALPHA)
                pygame.draw.circle(trail_surface, (*self.color[:3], alpha), (2, 2), 2)
                surface.blit(trail_surface, pos)

    def calculate_combined_stimulus(self, light_sources):
        # Vehicle 5 processes multiple light sources with exploration behavior
        left_total = 0
        right_total = 0
        closest_light = None
        min_distance = float('inf')
        
        for light in light_sources:
            left_dist = self.left_sensor_position.distance_to(light.position)
            right_dist = self.right_sensor_position.distance_to(light.position)
            
            # Track closest light for visit detection
            center_dist = self.position.distance_to(light.position)
            if center_dist < min_distance:
                min_distance = center_dist
                closest_light = light
            
            # Calculate interest level based on visit history
            interest_level = max(0.1, 1.0 - (light.visited_count * 0.1))
            
            # Apply Vehicle 5's exploration function
            left_response = exploration_function(left_dist, interest_level) * light.intensity
            right_response = exploration_function(right_dist, interest_level) * light.intensity
            
            left_total += left_response
            right_total += right_response
        
        # Check if we're visiting a light source
        if closest_light and min_distance < self.visit_threshold:
            if self.last_light_visit != closest_light:
                closest_light.visited_count += 1
                self.last_light_visit = closest_light
        elif min_distance > self.visit_threshold * 2:
            self.last_light_visit = None
        
        return left_total, right_total

    def move(self, light_sources):
        self.sensor_spacing = 40 if not MONO else 0
        
        # Calculate stimulus from all light sources
        left_stimulus, right_stimulus = self.calculate_combined_stimulus(light_sources)
        
        # Apply Vehicle 5's exploration modifications
        exploration_noise = random.uniform(-EXPLORATION_NOISE, EXPLORATION_NOISE)
        
        left_speed = self.speed_scaling * left_stimulus
        right_speed = self.speed_scaling * right_stimulus
        
        # Add exploration behavior - occasional random movements
        self.exploration_timer += 1
        if self.exploration_timer > 60:  # Every second at 60fps
            if random.random() < 0.3:  # 30% chance to explore
                exploration_boost = random.uniform(0.5, 1.5)
                if random.random() < 0.5:
                    left_speed *= exploration_boost
                else:
                    right_speed *= exploration_boost
            self.exploration_timer = 0
        
        speed = (left_speed + right_speed) / 2
        
        if INHIBITION:
            speed = max(0.1, 1 - speed)
        
        rotation = (right_speed - left_speed) * self.rotation_scaling
        
        if CROSS:
            rotation *= -1
        
        # Add exploration noise to rotation
        rotation += exploration_noise
        
        self.direction += rotation
        direction = pygame.math.Vector2(0, -1).rotate(self.direction)
        
        # Update position with boundary wrapping
        self.position += direction * speed
        self.position.x %= WIDTH
        self.position.y %= HEIGHT
        
        # Update trail for visualization
        if hasattr(self, 'trail'):
            self.trail.append(self.position.copy())
            if len(self.trail) > 50:
                self.trail.pop(0)
        else:
            self.trail = [self.position.copy()]
        
        self.update_sensor_positions()
        
        if FRICTION:
            self.direction += random.uniform(-2, 2)

    def draw_debug_info(self, surface, light_sources):
        debug_text = [
            f"Vehicle 5 - Explorer",
            f"Sensors: {'1' if MONO else '2'}",
            f"Friction: {'on' if FRICTION else 'off'}",
            f"Inhibition: {'on' if INHIBITION else 'off'}",
            f"Connection: {'ipsi' if CROSS else 'contra'}",
            f"Lights: {len(light_sources)}",
            f"Exploration: {EXPLORATION_NOISE:.1f}"
        ]
        
        y_offset = 10
        for line in debug_text:
            text_surface = font.render(line, True, WHITE)
            surface.blit(text_surface, (10, y_offset))
            y_offset += 20

# Initialize multiple light sources for Vehicle 5
def create_light_sources():
    lights = []
    positions = [
        (150, 150), (650, 150), (150, 650), (650, 650)
    ]
    colors = [YELLOW, ORANGE, (255, 200, 100), (255, 255, 150)]
    
    for i, pos in enumerate(positions):
        intensity = random.uniform(0.7, 1.0)
        lights.append(LightSource(pos, color=colors[i], intensity=intensity))
    
    return lights

# Initialize simulation
light_sources = create_light_sources()
vehicle = Vehicle((WIDTH // 2, HEIGHT // 2), random.randint(0, 360))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                MONO = not MONO
            elif event.key == pygame.K_r:
                FRICTION = not FRICTION
            elif event.key == pygame.K_i:
                INHIBITION = not INHIBITION
            elif event.key == pygame.K_c:
                CROSS = not CROSS
            elif event.key == pygame.K_SPACE:
                # Reset simulation
                light_sources = create_light_sources()
                vehicle = Vehicle((WIDTH // 2, HEIGHT // 2), random.randint(0, 360))
            elif event.key == pygame.K_UP:
                EXPLORATION_NOISE = min(1.0, EXPLORATION_NOISE + 0.1)
            elif event.key == pygame.K_DOWN:
                EXPLORATION_NOISE = max(0.0, EXPLORATION_NOISE - 0.1)
    
    # Clear screen
    screen.fill((20, 20, 40))  # Dark blue background
    
    # Draw light sources
    for light in light_sources:
        light.draw(screen)
    
    # Update and draw vehicle
    vehicle.move(light_sources)
    vehicle.draw(screen)
    
    # Draw debug information
    vehicle.draw_debug_info(screen, light_sources)
    
    # Draw controls
    controls = [
        "Controls:",
        "M - Toggle mono/dual sensors",
        "R - Toggle friction",
        "I - Toggle inhibition", 
        "C - Toggle cross connections",
        "SPACE - Reset simulation",
        "UP/DOWN - Adjust exploration"
    ]
    
    y_offset = HEIGHT - 140
    for line in controls:
        text_surface = font.render(line, True, (150, 150, 150))
        screen.blit(text_surface, (WIDTH - 250, y_offset))
        y_offset += 18
    
    pygame.display.flip()
    clock.tick(fps)

pygame.quit()