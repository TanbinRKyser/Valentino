import pygame
import random
pygame.init()

WIDTH, HEIGHT = 1200, 600
screen = pygame.display.set_mode(( WIDTH, HEIGHT ))
pygame.display.set_caption("Vehicle Simulation")

pygame.font.init()
font = pygame.font.SysFont("Arial", 20)
#pygame.time.wait(3000)
fps = 60

WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

class Circle:
    def __init__(self,position,radius=50,color=RED):

        ## Vector2 is a class in pygame that represents a 2D vector.
        ## It is used to store the position of the circle in 2D space.
        self.position = pygame.math.Vector2(position)
        self.radius = radius
        self.color = color

    def move(self):
        self.position.x = self.position.x + 1
        self.position.y = self.position.y + 1

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, self.position, self.radius)


class Vehicle:
    def __init__(self,position, direction=0, radius=50,color=RED):
        ## Vector2 is a class in pygame that represents a 2D vector.
        self.position = pygame.math.Vector2(position)
        self.direction = direction
        self.radius = radius
        self.color = color
        self.speed_scaling = 50
        self.rotation_scaling = 10
        ## sensors
        self.sensor_radius = 10
        self.sensor_offset = self.radius + self.sensor_radius

        # self.sensor_position.y = self.position.y - self.sensor_offset
        
        ## unit vector pointing up
        # self.sensor_position = pygame.math.Vector2( 0,-1)
        
        # now that we have the unit vector, we can multiply it by the offset to get the position of the sensor
        self.sensor_position = self.position + pygame.math.Vector2( 0, -self.sensor_offset ).rotate( self.direction )   
        
        self.sensor_color = GREEN

    def draw(self, surface):
        pygame.draw.circle( surface, self.color, self.position, self.radius )

        ## recalculating the sensor position based on the vehicle's position and direction
        self.sensor_position = self.position + pygame.math.Vector2( 0, -self.sensor_offset ).rotate( self.direction )

        pygame.draw.circle( surface, self.sensor_color, self.sensor_position, self.sensor_radius )    


    def calculate_distance_to_sun(self,sun_position):
        return self.sensor_position.distance_to(sun_position)

    def move(self,sun_position):

        modded_direction = self.direction + self.rotation_scaling * random.randint(-10,10) 

        direction = pygame.math.Vector2(0,-1).rotate(self.direction)
        # moving magnitude pixels in the direction of the source
        # magnitude = 3
        magnitude = self.calculate_distance_to_sun( sun_position )
        speed = self.speed_scaling * (1 / magnitude)

        text = f"distance to sun: {magnitude:.2f}\n speed: {speed:.2f}"
        text_surface = font.render(text, True, WHITE)
        screen.blit(text_surface, (10, 10))

        # self.position += direction * magnitude
        self.position += direction * speed


#circle = Circle((600, 300))
sun = Circle((600, 300), radius=40, color=YELLOW)
# vehicle = Vehicle((300, 500),radius = 30 )
vehicle = Vehicle( (300, 500), direction=45, radius = 30 )

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # screen.fill((255, 255, 255))
    # screen.fill(GREEN)
    # screen.fill(WHITE)

    # pygame.draw.circle( screen, RED, (600,300),100)
    # ## render the screen to frame
    # pygame.display.flip()

    screen.fill((0,0,0))
    #circle.move()
    #circle.draw(screen)
    sun.draw(screen)
    vehicle.draw(screen)
    vehicle.move(sun.position)
    # vehicle.move()
    pygame.display.flip()
    ## Controlls the frame rate of the game, by controlling the for loop speed.
    ## The clock.tick(fps) method will wait for the next frame to be ready, 
    # and it will limit the frame rate to fps frames per second.
    pygame.time.Clock().tick( fps )

pygame.quit()