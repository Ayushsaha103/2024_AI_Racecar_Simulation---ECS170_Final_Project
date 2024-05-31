import os
from math import sin, cos, pi, sqrt
from random import randrange

import pygame
from pygame.locals import *

import numpy as np
import gymnasium as gym
from gymnasium import spaces

from Constants import *
from Agent import *
from Road import *
from Waypoints import *
from math_helpers import angle_between_vectors, angle2vect, vectsub, normalize
import math


os.system('cls' if os.name == 'nt' else 'clear') # Cleaning library loading information texts
print("Fetching Libraries.. Please Wait..")



################################################################################################
# Car Env Class
################################################################################################

class CarEnv(gym.Env):
    def __init__(self):
        super(CarEnv, self).__init__()
        pygame.init()
        
        # VIDEO SETTINGS
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.FramePerSec = pygame.time.Clock()

        # Font SETTINGS
        pygame.font.init()
        self.myfont = pygame.font.SysFont("Comic Sans MS", 20)

        # Physical CONSTANTS
        self.FPS         =  Constants.FPS

        # GAME CONFIGURE
        self.reward = 0
        # self.time   = 0
        # self.pace   = 0
        # self.time_limit = 20
        # self.target_counter = 0

        # Agent SETTINGS
        self.Agent       = Car()
        self.Agent_image = spriter("Car")
        
        # GYM CONFIGURE
        self.action_space      = gym.spaces.Discrete(5)
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(6,), dtype=np.float16)
        self.info = {}
        Constants.report(self)
        
        # ADDED variables
        self.reset()

    # reset the game
    def reset(self):
        # reset car position and controlling variables
        self.Agent.reset()
        self.throttle, self.delta = 0,0
        self.action = 0
        
        # # re-initialize road and waypoints objects
        self.rd = Road()           # road object
        self.wp = Waypoints(10, self.rd, self.Agent)        # waypoints (target points) object

        # reset general game state counters
        # self.target_counter = 0
        self.reward = 0
        # self.time   = 0

        return self.get_state()

    # return the state of the game (so Agent knows its surroundings)
    # Agent x and y coordinates
    # Agent velocity
    # Agent steering angle
    # list of distances to nearest Waypoints
    # list of angles to nearest Waypoints
    def get_state(self):
        wp_distances = []
        wp_yaws = []
        n = len(self.rd.track_points)
        for i in range(self.wp.npts):
            wp_x, wp_y = self.rd.track_points[(self.wp.closest_pt + i) % n]
            wp_dist = distance([self.Agent.x, self.Agent.y], [wp_x, wp_y])
            wp_yaw = np.arctan2(wp_y - self.Agent.y, wp_x - self.Agent.x)
            err_yaw = wp_yaw - self.Agent.yaw
            wp_distances.append(wp_dist)
            wp_yaws.append(err_yaw)
        
        return [self.Agent.x, self.Agent.y, self.Agent.v, self.Agent.yaw, wp_distances, wp_yaws]

    # single timestep update of game
    def step(self, action):
        
        self.render()
        self.reward = 0.0
        # self.pace += 1
        # self.pace %= 20
        
        # choose controlling action to either be self.action (manual) or action (agent-controlled)
        ctrl_action = self.action   # int(action)
        
        # Act every x frames. Range can be altered. 
        for _ in range(1):
            # self.time += 1 / Constants.FPS

            # specify agent operations for certain values of A2C's output 'action'
            if ctrl_action == 0:         # do nothing
                self.delta = 0
            elif ctrl_action == 1:       # increase throttle force
                self.throttle = min(max_throttle, self.throttle + 0.02)
            elif ctrl_action == 2:       # decrease throttle force
                self.throttle = max(-max_throttle, self.throttle - 0.03)
            elif ctrl_action == 3:       # increase delta angle
                self.delta = min(max_steer, self.delta + np.radians(.4))
            elif ctrl_action == 4:       # decrease delta angle
                self.delta = max(-max_steer, self.delta - np.radians(.4))
    
            # UPDATE CAR POSITION
            # self.Agent.pidv(7, self.delta)        # constant speed update
            self.throttle = self.Agent.update(self.throttle, self.delta)       # standard update

            print("Has Collided", self.rd.get_has_collided(self.Agent.get_bounding_box()))
            
            # todo: add rewards, penalties, game termination

        return self.get_state(), self.reward, False, self.info
    
    # render entire game to the screen
    def render(self):
        # get user key inputs
        for event in pygame.event.get():
            if event.type == pygame.QUIT:       # check if user quit
                pygame.display.quit()
                pygame.quit()
                del(self)
                quit()
            keys = pygame.key.get_pressed()
            if keys[K_w]:  # Accelerate
                self.action = 1
            elif keys[K_s]:  # Brake
                self.action = 2
            elif keys[K_a]:  # Right
                self.action = 3
            elif keys[K_d]:  # Left
                self.action = 4
            else:
                self.action = 0

        # fill screen black
        self.screen.fill(BLACK)
        
        # get player's transformed coordinates
        player_x_trans = AGENTX - self.Agent.x
        player_y_trans = AGENTY - self.Agent.y

        # draw road
        self.rd.update_and_draw(self.screen, player_x_trans, player_y_trans)
        # draw waypoint
        self.wp.update_and_draw(self.screen, pt_size=4)
        # draw player
        player_sprite = self.Agent_image[0]
        player_copy   = pygame.transform.rotate(player_sprite, -math.degrees(self.Agent.yaw + (np.pi/2)))
        self.screen.blit( player_copy, (
            AGENTX - int(player_copy.get_width() / 2),
            AGENTY - int(player_copy.get_height() / 2),
        ), )

        ## Update the display
        self.screen.blit(pygame.transform.flip(self.screen, False, True), (0, 0))     # mirror screen vertical

        # # print info to screen
        # textsurface = self.myfont.render("Collected: " + str(self.target_counter), False, WHITE)
        # textsurface3 = self.myfont.render("Time: " + str(int(self.time)), False, WHITE)
        # self.screen.blit(textsurface, (20, 20))
        # self.screen.blit(textsurface3, (20, 50))

        pygame.display.flip()       # update display
        #pygame.display.update()
        #self.FramePerSec.tick(self.FPS)

    def close(self):
        pass
