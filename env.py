import os
from math import sin, cos, pi, sqrt
from random import randrange

import pygame
from pygame.locals import *

import numpy as np
import gym
from gym import spaces

from Constants import *
from Agent import *
from Road import *
import math


os.system('cls' if os.name == 'nt' else 'clear') # Cleaning library loading information texts
print("Fetching Libraries.. Please Wait..")

#WIDTH, HEIGHT = Constants.WIDTH, Constants.HEIGHT
#TIME_LIMIT = Constants.TIME_LIMIT
#BACKGROUND = Constants.BACKGROUND 
#spriter = Constants.spriter #Image displayer


################################################################################################
# Helper funcs
################################################################################################

def angle_between_vectors(vector1, vector2):
    # calculate angle between vect1 and vect2
    dot_product = sum(v1 * v2 for v1, v2 in zip(vector1, vector2))
    magnitude1 = math.sqrt(sum(v ** 2 for v in vector1))
    magnitude2 = math.sqrt(sum(v ** 2 for v in vector2))
    angle_radians = math.acos(dot_product / (magnitude1 * magnitude2))

    # determine whether vect2 is pointing to left/right/neither of vect1
    cross_product = np.cross(vector1, vector2)
    dir = -1
    if cross_product > 0: dir = 0   # left
    elif cross_product < 0: dir = 1     # right
    else: dir = 2     # "Parallel or Collinear"

    return 1 - (angle_radians / np.pi), dir

def angle2vect(angle, magnitude=1):
    return [magnitude*math.cos(angle), magnitude*math.sin(angle)]
def vectsub(pt1, pt2):    # pt2 - pt1
    return [pt2[i] - pt1[i] for i in range(len(pt2))]
def normalize(vect):
    magnitude = math.sqrt(sum(v ** 2 for v in vect))
    return [ vect[i] / magnitude for i in range(len(vect)) ]


################################################################################################
# Drone Env Class
################################################################################################

class droneEnv(gym.Env):
    def __init__(self):
        super(droneEnv, self).__init__()
        pygame.init()
            # VIDEO SETTINGS
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.FramePerSec = pygame.time.Clock()
        self.background = pygame.image.load(BACKGROUND)
        self.background = pygame.transform.scale(self.background, (WIDTH, HEIGHT))

            # Agent and Target SETTINGS
        self.Agent       = Drone()
        self.Agent_image = spriter("Drone")
        
        self.x_target = randrange(50, WIDTH - 50)
        self.y_target = randrange(75, HEIGHT - 75)
        self.target   = spriter("Baloon")

            # Font SETTINGS
        pygame.font.init()
        self.myfont = pygame.font.SysFont("Comic Sans MS", 20)
        
            # Physical CONSTANTS
        self.FPS         =  Constants.FPS

            # GAME CONFIGURE
        self.reward = 0
        self.time   = 0
        self.pace   = 0
        self.time_limit = 20
        self.target_counter = 0
        
            # GYM CONFIGURE
        self.action_space      = gym.spaces.Discrete(5)
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(6,), dtype=np.float16)
        
        self.info = {}
        Constants.report(self)
        
        # ADDED
        self.throttle, self.delta = 0,0
        self.rd = Road(nlanes=10)
        self.rd.update()

    def reset(self):
        
        self.Agent.reset()
        self.x_target = randrange(50, WIDTH - 50)
        self.y_target = randrange(75, HEIGHT - 75)

        self.target_counter = 0
        self.reward = 0
        self.time   = 0

        self.throttle, self.delta = 0,0
        self.d_delta_dt = 0.0

        return self.get_obs()

    def get_obs(self) -> np.ndarray:

        angle_y, dir_y = angle_between_vectors(angle2vect(self.Agent.yaw), normalize(vectsub([self.Agent.x, self.Agent.y],[self.x_target, self.y_target])))
        dist = sqrt((self.x_target - self.Agent.x) ** 2 + (self.y_target - self.Agent.y) ** 2) / 500
        angle_d, dir_d = angle_between_vectors(angle2vect(normalize_angle(self.Agent.yaw + self.delta)), normalize(vectsub([self.Agent.x, self.Agent.y],[self.x_target, self.y_target])))
        v = self.Agent.v

        return np.array(
            [
                angle_y, dir_y, dist, angle_d, dir_d, v,
            ]
        ).astype(np.float16)


    def step(self, action):
        
        self.render()
        self.reward = 0.0
        self.pace += 1
        self.pace %= 20
        
        action = int(action)
            
        # Act every x frames. Range can be altered. 
        for _ in range(1):
            self.time += 1 / 60

                # Initialize accelerations
            self.Agent.angular_acceleration = 0
            self.Agent.x_acceleration       = 0
            self.Agent.y_acceleration       = 0

            if action == 0:
                self.delta = 0
            
            elif action == 1:
                self.throttle = min(max_throttle, self.throttle + 1)

            elif action == 2:
                self.throttle = max(-max_throttle, self.throttle - 1)

            elif action == 3:
                self.delta = min(max_steer, self.delta + np.radians(5))

            elif action == 4:
                self.delta = max(-max_steer, self.delta - np.radians(5))
    
            #self.Agent.pidv(10, self.delta)
            self.throttle = self.Agent.update(self.throttle, self.delta)
            #self.Agent.pidv(20, self.delta)



            # conditionally update road
            if self.rd.check_for_update([self.Agent.x, self.Agent.y]): self.rd.update()
            
            ## check that car is within road bounds
            #if c.check_bounds():
            #    dx, dy = c.reset_pos()
            #    self.rd.reset_pos(dx, dy)
            #if c.check_cross_rd_bounds(self.rd):
            #    break




            # Euclidean distance between Agent and Target 
            dist = sqrt((self.Agent.x - self.x_target) ** 2 + (self.Agent.y - self.y_target) ** 2)

                # Reward per step if survived
            self.reward += 1 / 60
            
                # Penalizing to the distance to target (0.00016 is for normalize)
            self.reward -= dist * 0.000166 # (100*60)

            # CHECKME
            self.reward -= 0.2*(1/self.Agent.v)

            if dist < 10:
                # Reward if agent closes to target
                self.x_target = randrange(50, WIDTH - 50)
                self.y_target = randrange(75, HEIGHT - 75)
                self.reward += 100
                self.target_counter += 1
                self.time = 0
        
            # If times up
            if self.time > self.time_limit:
                # ADDED
                del self.rd
                self.rd = Road(nlanes=10)
                self.rd.update()

                done = True
                return self.get_obs(), self.reward, done, self.info

            #dist > 1000: 
            if self.Agent.x < 0 or self.Agent.x > WIDTH or \
                self.Agent.y < 0 or self.Agent.y > HEIGHT: 

                # ADDED
                del self.rd
                self.rd = Road(nlanes=10)
                self.rd.update()


                self.reward -= 800
                done = True
                return self.get_obs(), self.reward, done, self.info

        return self.get_obs(), self.reward, False, self.info

    def render(self):
        # Agent: x_pos, y_pos, angle

        # check if user quit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.display.quit()
                pygame.quit()
                del(self)
                quit()
        
        # fill screen black
        self.screen.fill(BLACK)
        
        # get player's transformed coordinates

        player_x_trans = agentx - self.Agent.x
        player_y_trans = agenty - self.Agent.y

        # draw screen bounds
        bounds = [[0, HEIGHT], [WIDTH, HEIGHT], [WIDTH, 0],  [0,0]]
        for i in range(len(bounds)):
            bound = bounds[i]
            bound[0] += player_x_trans
            bound[1] += player_y_trans
            pygame.draw.circle(self.screen, WHITE, bound, 3)
        for i in range(len(bounds)-1):
            pygame.draw.aaline(self.screen, WHITE, bounds[i], bounds[i+1])
        pygame.draw.aaline(self.screen, WHITE, bounds[-1], bounds[0])

        # draw target
        pygame.draw.circle(self.screen, RED, [self.x_target + player_x_trans, self.y_target+player_y_trans], 4)

        # draw player
        player_sprite = self.Agent_image[int(self.pace * 0.1) % len(self.Agent_image)]
        player_copy   = pygame.transform.rotate(player_sprite, -math.degrees(self.Agent.yaw + (np.pi/2)))
        self.screen.blit(
            player_copy,
            (
                agentx - int(player_copy.get_width() / 2),
                agenty - int(player_copy.get_height() / 2),
            ),
        )

        # draw road
        self.rd.draw(self.screen, player_x_trans, player_y_trans)

        ## Update the display
        self.screen.blit(pygame.transform.flip(self.screen, False, True), (0, 0))     # mirror screen vertical

        # print info to screen
        textsurface = self.myfont.render("Collected: " + str(self.target_counter), False, WHITE)
        textsurface3 = self.myfont.render("Time: " + str(int(self.time)), False, WHITE)
        self.screen.blit(textsurface, (20, 20))
        self.screen.blit(textsurface3, (20, 50))

        pygame.display.flip()       # update display
        #pygame.display.update()
        #self.FramePerSec.tick(self.FPS)

    def close(self):
        pass
