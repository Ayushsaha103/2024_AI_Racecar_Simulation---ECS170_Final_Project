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
from math_helpers import find_ey
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
        self.action_space      = gym.spaces.Discrete(9)
        obs_size = 5 + (NUM_WAYPOINTS * 4)
        self.data = np.array([0]*obs_size)
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(obs_size,), dtype=np.float16)
        self.info = {}
        Constants.report(self)

        # Initialize Road
        self.road = Road()

        # Start lap timer
        self.start_time = pygame.time.get_ticks()

        # Start lap counter
        self.lap_count = 0
        
        # ADDED variables
        self.reset()

    # reset the game
    def reset(self):
        # re-initialize road and waypoints objects
        self.rd = Road()           # road object
        self.wp = Waypoints(NUM_WAYPOINTS, self.rd, self.Agent)        # waypoints (target points) object
        self.closest_track_coor = self.rd.orig_track_pts[(self.wp.closest_pt)]
        
        # reset car position and controlling variables
        inital_pos = self.rd.get_initial_position()
        initial_yaw = self.rd.get_initial_yaw()
        self.Agent.reset(inital_pos[0], inital_pos[1], initial_yaw)
        self.throttle, self.delta = 0,0
        
        self.action = 0
        # reset general game state counters
        # self.target_counter = 0
        self.reward = 0
        # self.time   = 0

        # Reset lap timer
        self.start_time = 0

        return self.get_state()

    # return the state of the game (so Agent knows its surroundings)
    # Agent x and y coordinates
    # Agent velocity
    # Agent steering angle
    # distance error and angle disance error to nearest Waypoint
    # list of distances to nearest Waypoints
    # list of angles to nearest Waypoints
    def get_state(self) -> np.ndarray:
        # get distance, angle to all waypoints
        wp_distances = []
        wp_angles = []
        n = len(self.rd.orig_track_pts)

        for i in range(NUM_WAYPOINTS):
            wp1_x, wp1_y = self.rd.orig_left_pts[(self.wp.closest_pt + i) % n]
            wp1_dist = distance([self.Agent.x, self.Agent.y], [wp1_x, wp1_y])
            wp1_angle = np.arctan2(wp1_y - self.Agent.y, wp1_x - self.Agent.x)
            
            wp2_x, wp2_y = self.rd.orig_right_pts[(self.wp.closest_pt + i) % n]
            wp2_dist = distance([self.Agent.x, self.Agent.y], [wp2_x, wp2_y])
            wp2_angle = np.arctan2(wp2_y - self.Agent.y, wp2_x - self.Agent.x)
            
            wp_distances += [wp1_dist, wp2_dist]
            wp_angles += [wp1_angle, wp2_angle]
        
        # get ey, ephi to the NEAREST coordinate within track
        wp_coors = [ self.rd.orig_track_pts[(self.wp.closest_pt-1) % n], self.rd.orig_track_pts[(self.wp.closest_pt) % n], self.rd.orig_track_pts[(self.wp.closest_pt + 1) % n] ]
        car_pos = (self.Agent.x, self.Agent.y)
        ey, nearest_wps, self.closest_track_coor = find_ey(car_pos, wp_coors)
        (wp1_x, wp1_y), (wp2_x, wp2_y) = nearest_wps
        wp_yaw = np.arctan2(wp2_y - wp1_y, wp2_x - wp1_x)
        ephi = wp_yaw - self.Agent.yaw
        s, wz = self.Agent.traveled, self.Agent.wz

        self.data = [self.Agent.x, self.Agent.y, self.Agent.v, self.Agent.yaw, ey, ephi, s, wz] + wp_distances + wp_angles
        return np.array(self.data).astype(np.float16)

    # single timestep update of game
    def step(self, action):
        
        self.render()
        self.reward = 0.0
        # self.pace += 1
        # self.pace %= 20
        
        # choose controlling action to either be self.action (manual) or action (agent-controlled)
        ctrl_action = int(action)       # agent control
        # ctrl_action = self.action     # manual control
        
        # Act every x frames. Range can be altered. 
        for _ in range(1):
            # self.time += 1 / Constants.FPS

            # specify agent operations for certain values of A2C's output 'action'
            if ctrl_action < 3:
                self.throttle = 0
            elif ctrl_action < 6:       # increase throttle force
                self.throttle = min(max_throttle, self.throttle + 0.01)
            else:                       # decrease throttle force
                self.throttle = max(-max_throttle, self.throttle - 0.01)
            if ctrl_action % 3 == 1:    # increase delta angle
                self.delta = min(max_steer, self.delta + np.radians(0.5))
            elif ctrl_action % 3 == 2:  # decrease delta angle
                self.delta = max(-max_steer, self.delta - np.radians(0.5))
            else:
                self.delta = 0
    
            # UPDATE CAR POSITION
            # self.Agent.pidv(7, self.delta)        # constant speed update
            self.throttle = self.Agent.update(self.throttle, self.delta)       # standard update
            # print([self.throttle, self.delta, self.Agent.v])        # show action info
        
        # rewards
        # self.reward += 1/FPS        # reward for surviving

        self.reward += 0.1*self.Agent.v     # reward for moving fast

        ey, err_yaw = self.data[1], self.data[2]
        self.reward += 0.05*(-ey - err_yaw)     # penalize for not moving in direction of nearest track point

        # # collision detection
        if self.rd.get_has_collided(self.Agent.get_bounding_box()):
            self.reward -= 400      # collision penalty
            done = True
            return self.get_state(), self.reward, done, self.info

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
            # MANUAL keystroke car-control inputs
            keys = pygame.key.get_pressed()
            if keys[K_w]:    # Accelerate
                self.action = 3
            elif keys[K_s]:  # Brake
                self.action = 6
            else:
                self.action = 0
            if keys[K_a]:    # Right
                self.action += 1
            elif keys[K_d]:  # Left
                self.action += 2

        # fill screen black
        self.screen.fill(BLACK)
        
        # get player's transformed coordinates
        player_x_trans = AGENTX - self.Agent.x
        player_y_trans = AGENTY - self.Agent.y

        # draw road
        self.rd.update_and_draw(self.screen, player_x_trans, player_y_trans)
        # draw waypoints
        self.wp.update_and_draw(self.screen, pt_size=4)
        # draw line to nearest track coor
        translated_closest_track_coor = (self.closest_track_coor[0]+player_x_trans, self.closest_track_coor[1]+player_y_trans)
        pygame.draw.line(self.screen, GREEN, translated_closest_track_coor, (AGENTX, AGENTY), 3)

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

        # Display lap time
        elapsed_time = (pygame.time.get_ticks() - self.start_time) / 1000  # in seconds
        lap_time_text = self.myfont.render(f"Lap Time: {elapsed_time:.2f}s", False, WHITE)
        text_rect = lap_time_text.get_rect()
        text_rect.bottomright = (WIDTH - 20, HEIGHT - 20)
        self.screen.blit(lap_time_text, text_rect)

        # # Display lap count
        # print("Agent x: ", self.Agent.x, "\tAgent y: ", self.Agent.y)
        # print("initial position: ", self.road.get_initial_position())
        initial_pos = self.rd.get_initial_position()
        agent_pos = (self.Agent.x, self.Agent.y)
        
        # Check if agent is within a 10x10 box of the initial position
        if (initial_pos[0] - 5 <= agent_pos[0] <= initial_pos[0] + 5 and
            initial_pos[1] - 5 <= agent_pos[1] <= initial_pos[1] + 5):
            self.lap_count += 1
            self.start_time = pygame.time.get_ticks()
        lap_count_text = self.myfont.render(f"Lap Count: {self.lap_count}", False, WHITE)
        count_rect = lap_count_text.get_rect()
        count_rect.bottomright = (WIDTH - 40, HEIGHT - 40)
        self.screen.blit(lap_count_text, count_rect)



        pygame.display.flip()       # update display
        #pygame.display.update()
        #self.FramePerSec.tick(self.FPS)

    def close(self):
        pass
