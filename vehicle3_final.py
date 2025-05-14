import pygame
import random

pygame.init()

WIDTH, HEIGHT = 600, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Braitenberg Vehicle")

pygame.font.init()
font = pygame.font.SysFont("Arial", 20)

clock = pygame.time.Clock()
fps = 120

WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

MONO = False  # Set to True for one sensor vehicle
FRICTION = False  # Set to True for friction
INHIBITION = False  # Set to True for inhibition sensor
CROSS = False  # Set to True for cross connection

class Circle:
    def __init__(self, position, radius=50, color=RED):
        self.position = pygame.math.Vector2(position)
        self.radius = radius
        self.color = color

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, self.position, self.radius)


class Vehicle:
    def __init__(self, position, direction, radius=30, color=RED):
        self.position = pygame.math.Vector2(position)
        self.direction = direction

        self.radius = radius
        self.color = color

        self.speed_scaling = 50
        self.rotation_scaling = 5

        # sensor
        self.sensor_radius = 10
        self.sensor_offset = self.radius + self.sensor_radius

        self.sensor_spacing = 50 if not MONO else 0



        self.left_sensor_position = (
            self.position
            + pygame.math.Vector2(0, -self.sensor_offset) 
            + pygame.math.Vector2(1, -self.sensor_spacing)
        )

        self.right_sensor_position = (
            self.position 
            + pygame.math.Vector2(0, -self.sensor_offset)
            + pygame.math.Vector2(1, self.sensor_spacing)
        )

        self.sensor_color = GREEN

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, self.position, self.radius)
        pygame.draw.circle(
            surface, self.sensor_color, self.left_sensor_position, self.sensor_radius
        )
        pygame.draw.circle(
            surface, self.sensor_color, self.right_sensor_position, self.sensor_radius
        )

    def calculate_distance_to_sun(self, sun_position):
        return self.sensor_position.distance_to(sun_position)

    def move(self, sun_position):

        self.sensor_spacing = 50 if not MONO else 0

        forward = pygame.math.Vector2(0,-1).rotate(self.direction)
        right = forward.rotate(-90)

        left_distance = self.left_sensor_position.distance_to(sun_position)
        right_distance = self.right_sensor_position.distance_to(sun_position)

        left_speed = self.speed_scaling * (1 / left_distance)
        right_speed = self.speed_scaling * (1 / right_distance)

        speed = (left_speed + right_speed) / 2

        if INHIBITION:
            speed = 1 - speed
            
        rotation = (right_speed - left_speed) * self.rotation_scaling

        if CROSS:
            rotation *= -1
        
        self.direction += rotation
        direction = pygame.math.Vector2(0, -1).rotate(self.direction)

        self.position += direction * speed
        self.position.x %= WIDTH
        self.position.y %= HEIGHT

        self.left_sensor_position = (
            self.position
            + forward * self.sensor_offset
            - right * (self.sensor_spacing / 2)
        )

        self.right_sensor_position = (
            self.position
            + forward * self.sensor_offset
            + right * (self.sensor_spacing / 2)
        )

        if FRICTION:
            self.direction += random.randint(-5,5)

        # debug
        text = f"sensors: {'1' if MONO else '2'}"
        text += f"\nfriction: {'on' if FRICTION else 'off'}"
        text += f"\ninhibition: {'on' if INHIBITION else 'off'}"
        text += f"\nconnection: {'ipsi' if CROSS else 'contra'}"

        text += f"\nspeed: {speed:.4f}"
        text_surface = font.render(text, True, (255, 255, 255))
        screen.blit(text_surface, (10, 10))


sun = Circle((WIDTH // 2, HEIGHT // 2), radius=30, color=YELLOW)
vehicle = Vehicle((300, 500), 55)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                MONO = not MONO
            if event.key == pygame.K_r:
                FRICTION = not FRICTION
            if event.key == pygame.K_i:
                INHIBITION = not INHIBITION
            if event.key == pygame.K_c:
                CROSS = not CROSS
                
    screen.fill((0, 0, 0))
    sun.draw(screen)
    vehicle.move(sun.position)
    vehicle.draw(screen)

    pygame.display.flip()

    clock.tick(fps)

pygame.quit()