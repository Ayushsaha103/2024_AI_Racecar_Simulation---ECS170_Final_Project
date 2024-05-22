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
        self.time   = 0
        self.pace   = 0
        self.time_limit = 20
        self.target_counter = 0

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
        
        # re-initialize road and waypoints objects
        self.rd = Road(nlanes=10)           # road object
        self.rd.update()
        self.wp = WayPoints(self.rd)        # waypoints (target points) object

        # reset general game state counters
        self.target_counter = 0
        self.reward = 0
        self.time   = 0

        return self.get_obs()

    # return the state of the game (so Agent knows its surroundings)
    def get_obs(self) -> np.ndarray:
        
        # angle_y = angle between yaw vector and next waypoint
        #           note: this angle is converted s.t. 180deg => '0', 90deg => '0.5', 0deg => '1'
        # dir_y = (bool) is the waypoint to left/right of car's yaw vector
        angle_y, dir_y = angle_between_vectors(angle2vect(self.Agent.yaw), normalize(vectsub([self.Agent.x, self.Agent.y],[self.wp.x, self.wp.y])))
        
        # dist_to_wp = distance to next waypoint
        dist_to_wp = sqrt((self.wp.x - self.Agent.x) ** 2 + (self.wp.y - self.Agent.y) ** 2) / 500
        
        # angle_d = angle between wheel's direction vector and next waypoint
        #           note: this angle is converted s.t. 180deg => '0', 90deg => '0.5', 0deg => '1'
        # dir_d = (bool) is the waypoint to left/right of wheel's direction vector
        angle_d, dir_d = angle_between_vectors(angle2vect(normalize_angle(self.Agent.yaw + self.delta)), normalize(vectsub([self.Agent.x, self.Agent.y],[self.wp.x, self.wp.y])))
        
        # car velocity
        v = self.Agent.v

        return np.array(
            [
                angle_y, dir_y, dist_to_wp, angle_d, dir_d, v,
            ]
        ).astype(np.float16)

    # single timestep update of game
    def step(self, action):
        
        self.render()
        self.reward = 0.0
        self.pace += 1
        self.pace %= 20
        
        action = int(action)
            
        # Act every x frames. Range can be altered. 
        for _ in range(1):
            self.time += 1 / 60

            # specify agent operations for certain values of A2C's output 'action'
            if action == 0:         # do nothing
                self.delta = 0
            
            elif action == 1:       # increase throttle force
                self.throttle = min(max_throttle, self.throttle + 1)

            elif action == 2:       # decrease throttle force
                self.throttle = max(-max_throttle, self.throttle - 1)

            elif action == 3:       # increase delta angle
                self.delta = min(max_steer, self.delta + np.radians(2))

            elif action == 4:       # decrease delta angle
                self.delta = max(-max_steer, self.delta - np.radians(2))
    
            # UPDATE CAR POSITION
            self.Agent.pidv(7, self.delta)        # constant speed update
            #self.throttle = self.Agent.update(self.throttle, self.delta)       # standard update

            # conditionally update road to next positioning (if car is about to reach the end of road)
            if self.rd.check_for_update([self.Agent.x, self.Agent.y]): self.rd.update()
            
            # Euclidean distance between Agent and waypoint
            dist_to_wp = sqrt((self.Agent.x - self.wp.x) ** 2 + (self.Agent.y - self.wp.y) ** 2)

            # Reward per step if survived
            self.reward += 1 / 60
            
            # Penalizing to the distance to target (0.00016 is for normalize)
            self.reward -= dist_to_wp * 0.000166 # (100*60)

            # penalty for going slow (-=)
            #self.reward -= (0.04/(self.Agent.v + 1))

            # conditionally update waypoint position
            if self.wp.check_for_update([self.Agent.x, self.Agent.y]):
                # Reward if agent closes to target
                self.reward += 100
                self.target_counter += 1
                self.time = 0

                self.wp.update(self.rd, self.Agent)
        
            # penalty if time's up
            if self.time > self.time_limit:
                # ADDED
                del self.rd
                self.rd = Road(nlanes=10)
                self.rd.update()

                done = True
                return self.get_obs(), self.reward, done, self.info


            # calculate angle_y, angle_d (see get_obs() function for details on these variables)
            angle_y, dir_y = angle_between_vectors(angle2vect(self.Agent.yaw), normalize(vectsub([self.Agent.x, self.Agent.y],[self.wp.x, self.wp.y])))
            angle_d, dir_d = angle_between_vectors(angle2vect(normalize_angle(self.Agent.yaw + self.delta)), normalize(vectsub([self.Agent.x, self.Agent.y],[self.wp.x, self.wp.y])))
            
            # penalize agent for facing away from waypoint
            self.reward -= (0.2 / angle_d)

            # terminate game/penalize agent if crosses road bounds or really faces away from waypoint, or gets far from waypoint
            if self.Agent.check_cross_rd_bounds(self.rd) or angle_y < 0.2 or dist_to_wp > 180:
                # reset road 
                del self.rd, self.wp
                self.reset()

                self.reward -= 200
                done = True
                return self.get_obs(), self.reward, done, self.info

        return self.get_obs(), self.reward, False, self.info
    
    # render entire game to the screen
    def render(self):
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

        ## draw screen bounds
        #bounds = [[0, HEIGHT], [WIDTH, HEIGHT], [WIDTH, 0],  [0,0]]
        #for i in range(len(bounds)):
        #    bound = bounds[i]
        #    bound[0] += player_x_trans
        #    bound[1] += player_y_trans
        #    pygame.draw.circle(self.screen, WHITE, bound, 3)
        #for i in range(len(bounds)-1):
        #    pygame.draw.aaline(self.screen, WHITE, bounds[i], bounds[i+1])
        #pygame.draw.aaline(self.screen, WHITE, bounds[-1], bounds[0])


        # draw target
        pygame.draw.circle(self.screen, RED, [self.wp.x + player_x_trans, self.wp.y+player_y_trans], 4)

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

        # draw waypoint
        self.wp.draw(self.screen, player_x_trans, player_y_trans)

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
