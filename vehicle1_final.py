import pygame
import random

pygame.init()

WIDTH, HEIGHT = 600, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Braitenberg Vehicle 1")

pygame.font.init()
font = pygame.font.SysFont("Arial", 20)

clock = pygame.time.Clock()
fps = 120

WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)


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

        self.sensor_position = self.position + pygame.math.Vector2(
            0, -self.sensor_offset
        ).rotate(self.direction)

        self.sensor_color = GREEN

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, self.position, self.radius)
        pygame.draw.circle(
            surface, self.sensor_color, self.sensor_position, self.sensor_radius
        )

    def calculate_distance_to_sun(self, sun_position):
        return self.sensor_position.distance_to(sun_position)

    def move(self, sun_position):
        distance = self.calculate_distance_to_sun(sun_position)
        speed = self.speed_scaling * (1 / distance)
        direction = pygame.math.Vector2(0, -1).rotate(self.direction)

        self.position += direction * speed
        self.position.x %= WIDTH
        self.position.y %= HEIGHT
        self.sensor_position = self.position + pygame.math.Vector2(
            0, -self.sensor_offset
        ).rotate(self.direction)
        
        # debug
        text = f"distance to sun: {distance:.4f}"
        text += f"\nspeed: {speed:.4f}"
        text_surface = font.render(text, True, (255, 255, 255))
        screen.blit(text_surface, (10, 10))

    def update_direction(self):
    ## added brownian motion to the vehicle
        self.direction += random.randint(-1,1)

def check_collision( vehicle1, vehicle2 ):
    distance = vehicle1.position.distance_to( vehicle2.position )
    if distance < vehicle1.radius + vehicle2.radius:
        return True
    return False

sun = Circle((WIDTH // 2, HEIGHT // 2), radius=30, color=YELLOW)
# vehicle = Vehicle((300, 500), 55)
vehicles = []
for _ in range(10):
    x,y = random.randint(0, WIDTH), random.randint(0, HEIGHT)
    direction = random.randint(0, 360)
    color = (random.randint(0,255), random.randint(0, 255), random.randint(0, 255))
    radius = 30
    vehicle = Vehicle( (x, y), direction, radius, color)
    vehicles.append(vehicle)

last_update_time = 0
update_interval = 60

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))
    sun.draw(screen)
    
    current_time = pygame.time.get_ticks() 

    if current_time - last_update_time >= update_interval:
        for vehicle in vehicles:
            vehicle.update_direction()
        last_update_time = current_time
    
    for i in range( len(vehicles) ):
        for j in range( i+1, len(vehicles) ):
            if check_collision( vehicles[i], vehicles[j] ):
                collision_vector = vehicles[j].position - vehicles[i].position
                collision_vector.normalize_ip()

                up = pygame.math.Vector2(0, -1) 

                direction1 = pygame.math.Vector2(0,-1).rotate( vehicles[i].direction )
                direction2 = pygame.math.Vector2(0,-1).rotate( vehicles[j].direction )

                reflected1 = (direction1 - 2 * ( direction1.dot( collision_vector ) * collision_vector) )
                reflected2 = (direction2 - 2 * ( direction2.dot( -collision_vector ) * -collision_vector) )

                vehicles[i].direction = reflected1.angle_to( up )
                vehicles[j].direction = reflected2.angle_to( up)


    for vehicle in vehicles:
        vehicle.move( sun.position )
        vehicle.draw( screen )

    pygame.display.flip()

    clock.tick( fps )

pygame.quit()