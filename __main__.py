'''
Created on 15 May 2010

@author: David Schneider
'''

from pygame.locals import *
from pygame.surface import Surface
from pygame.time import Clock
from Vector2 import Vector2
import math
import pygame
import random
import sys


class Element(object):
    """Base class of all game elements."""
    def __init__(self, screen, image_path, position, velocity, acceleration=Vector2()):
        self.screen = screen
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.position = position
        self.velocity = velocity
        self.acceleration = acceleration
        self.alive = True
        
    def prepare(self, element_list):
        self.velocity += self.acceleration
        self.position += self.velocity        
        #print "Position X: %s\tPosition Y:%s" % (self.position.x, self.position.y)
        
    def render(self):
        draw_pos = self.image.get_rect().move(self.position.x - self.image.get_width()/2, self.position.y - self.image.get_height()/2)
        #print "Top:%s\tBottom:%s\tLeft:%s\tRight:%s" % (draw_pos.top, draw_pos.bottom, draw_pos.left, draw_pos.right)
        self.screen.blit(self.image, draw_pos)
    
        
class Meteor(Element):
    """Game contains one instance of the meteor class.
       The meteor's initial velocity is set by the player and can only be affected
       by planets after launch.
    """
    
    def __init__(self, screen, image_path, position, velocity):
        super(Meteor, self).__init__(screen, image_path, position, velocity)
        self.image = pygame.transform.scale(self.image, (15, 15))
        #self.image = Surface((5, 5))
        #self.image.fill((255, 255, 255))
    
    def prepare(self, element_list):
        super(Meteor, self).prepare(element_list)
        planet_list = [element for element in element_list if type(element) == Planet]
        # Iterate through list of planets and modify meteor velocity where the meteor
        # is affected by a planet's gravitational pull.
        for planet in planet_list:
            _detect_collision(self, planet)             


class Player(Element):
    
    def __init__(self, screen, image_path, position, velocity):
        super(Player, self).__init__(screen, image_path, position, velocity)
        self.base_image = pygame.transform.scale(self.image, (50, 50))
        self.yaw = 270
        self.boost_level = 30
        self.image = pygame.transform.rotate(self.base_image, self.yaw)
        self.is_boosting = False
        self.subject = Vector2()
        self.damper_x = 0.0
        self.damper_y = 0.0
        self.damper_count = 0
        self.score = 0
    
    def adjustYaw(self, angle):
        self.yaw += angle
        if self.yaw < 0:
            self.yaw = 359
        elif self.yaw > 359:
            self.yaw = 0
            
    def boost(self):
        if self.boost_level:
            self.is_boosting = True
            self.velocity.x += 0.1 * self.subject.x
            self.velocity.y += 0.1 * self.subject.y
            self.damper_x = -self.velocity.x / 30.0
            self.damper_y = -self.velocity.y / 30.0
            self.damper_count = 30
            self.boost_level -= 1        
    
    def prepare(self, element_list):
        super(Player, self).prepare(element_list)
        self._calculate_subject()
        self.image = pygame.transform.rotate(self.base_image, self.yaw)
        # Iterate through list of planets and modify player velocity where the player
        # is affected by a planet's gravitational pull.
        collision_list = [element for element in element_list if type(element) != Player]
        for element in collision_list:
            _detect_collision(self, element)        
        if not self.is_boosting:
            if self.boost_level < 10:
                self.boost_level += 1
            if self.damper_count:
                self.velocity.x += self.damper_x
                self.velocity.y += self.damper_y
                self.damper_count -= 1            
        self.is_boosting = False
        
    def _calculate_subject(self):
        self.subject.x = -math.sin(_degrees_to_radians(self.yaw))
        self.subject.y = -math.cos(_degrees_to_radians(self.yaw))
        self.subject.normalise()
        
    def reset(self):
        self.position.x = 20
        self.position.y = 300
        self.score = 0
        self.velocity.x = 0
        self.velocity.y = 0
        self.acceleration.x = 0
        self.acceleration.y = 0
    
class Planet(Element):
    """ Game contains several instances of the planet class.
        Planets orbit around a fixed point in the game world.
        Each planet has a gravitational pull that affects the meteor inside a given radius.
        Gravitational pull increases according to a quadratic formula (i.e. stronger nearer the planet)
    """
    
    def __init__(self, screen, image_path, position, velocity, radius, field_radius, field_quadratic, field_linear, orbital_focus, orbital_radius, orbital_speed):
        assert(field_radius > radius)
        super(Planet, self).__init__(screen, image_path, position, velocity)
        self.radius = radius
        self.field_radius = field_radius
        self.field_quadratic = field_quadratic
        self.field_linear = field_linear
        self.orbital_focus = orbital_focus
        self.orbital_radius = orbital_radius
        self.orbital_speed = orbital_speed
        self.angle = random.randint(0, 359)
        self.images = []
        for i in range(0, 360):
            self.images.append(pygame.transform.rotate(self.image, i))
        self.frame = 0
        #self.image = self.image
        #self.image.fill((255, 50, 120))
        
    def prepare(self, element_list):
        self.position.x = self.orbital_radius * math.cos(_degrees_to_radians(self.angle)) + self.orbital_focus.position.x
        self.position.y = self.orbital_radius * math.sin(_degrees_to_radians(self.angle)) + self.orbital_focus.position.y
        self.angle = (self.angle + self.orbital_speed) % 360
        self.image = self.images[self.frame]
        self.frame = (self.frame + 1) % 360
        #print "Position X: %s\tPosition Y:%s" % (self.position.x, self.position.y)
        
        
class Sun(Element):
    """ Game contains one instance of the sun class.
        The sun is situated at the centre of the solar system and must be large enough
        to block line-of-sight from the entry point to the exit point.
    """
    
    def __init__(self, screen, image_path, position, velocity, radius):
        super(Sun, self).__init__(screen, image_path, position, velocity)
        self.radius = radius
        #self.image = Surface((2*self.radius, 2*self.radius))
        #self.image.fill((255, 255, 255))


class Particle(Element):
    
    def __init__(self, screen, image_path, position, velocity, acceleration=Vector2(), lifetime=0.0):
        self.screen = screen
        self.image = pygame.image.load(image_path).convert_alpha()        
        self.position = position
        self.velocity = velocity
        self.acceleration = acceleration
        self.lifetime = lifetime
        self.time_alive = 0.0
        self.alive = True
        
    def prepare(self, time_passed):
        # If particle has non-zero lifetime, add time elapsed since last frame to counter
        # and kill the particle if its lifetime has been exceeded.
        if self.lifetime:
            self.time_alive += time_passed
            if self.time_alive > self.lifetime:
                self.alive = False        


def _detect_collision(obj1, obj2):
    if type(obj2) == Planet:
        if type(obj1) == Player:
            l = (obj2.position - obj1.position).length()            
            if l < obj2.radius + 25:
                obj1.reset()
        if _is_point_in_circle(obj1.position, obj2.position, obj2.field_radius):            
                if type(obj1) == Player:
                    obj1.score += 10
                v = obj2.position - obj1.position
                d = v.length()
                v.normalise()
                obj1.velocity += v * ((d * math.pow(obj2.field_quadratic, 2)) + (d * obj2.field_linear))

def _is_point_in_circle(point, circle_centre, circle_radius):    
    return math.pow(point.x - circle_centre.x, 2) + math.pow(point.y - circle_centre.y, 2) <= math.pow(circle_radius, 2)

def _degrees_to_radians(degrees):
    return degrees * 3.14 / 180

def runGame():
    SCREEN_WIDTH, SCREEN_HEIGHT = 1024, 768
    BG_COLOR = 15, 15, 20
        
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
    clock = Clock()
    
    pygame.font.init()
    my_font = pygame.font.SysFont('arial', 20)
    score_rect = pygame.Rect(900, 50, 100, 100)
    
    # Set up starfield
    starfield = []
    for i in range(1, 500):
        starfield.append(Particle(screen, "sprites/sparkle01.png", Vector2(random.randint(1, 1024), random.randint(1, 768)), Vector2()))
    
    # Set up game elements
    element_list = []
    
    #meteor = Meteor(screen, "sprites/asteroid-001.png", Vector2(0,300), Vector2(1.8, -0.4))
    #element_list.append(meteor)

    sun = Sun(screen, "sprites/planet-004.png", Vector2(512, 384), Vector2(), 50)
    element_list.append(sun)
    
    player = Player(screen, "sprites/Su-55.png", Vector2(20, 300), Vector2())
    element_list.append(player)
    
    for i in (80, 150, 220, 290, 370):
        planet = Planet(screen, 
                        "sprites/planet-%s.png" % random.choice(("001", "002", "003", "004")), 
                        Vector2(i,300), 
                        Vector2(), 
                        10, 
                        90, 
                        0.01, 
                        0.0005, 
                        sun, 
                        i,
                        (random.random() + 0.8) % 1.0)
        element_list.append(planet)

    while True:
        # Limit to 50 FPS
        time_passed = clock.tick(50)
        
        # Handle event queue
        for event in pygame.event.get():            
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    sys.exit()                
                    
        keys = pygame.key.get_pressed()
        if keys[K_UP]:
            player.boost()
        if keys[K_LEFT]:
            player.adjustYaw(2)
        if keys[K_RIGHT]:
            player.adjustYaw(-2)
                
        # Handle starfield particles
        for star in starfield:
            star.prepare(time_passed)            
                
        # Handle game elements
        for element in element_list:
            element.prepare(element_list)
            
        # Render background
        screen.fill(BG_COLOR)
        
        # Render starfield
        for star in starfield:
            star.render()
            
        # Render game elements
        for element in element_list:
            element.render()
            
        # Render score
        score = my_font.render("Score: %s" % player.score, True, (255, 0, 0))
        screen.blit(score, score_rect)
        
        pygame.display.flip()

if __name__ == '__main__':
    runGame()    
    