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
from Waypoints import *
from math_helpers import find_ey
# from metrics import plot
import math
from general_helpers import *
import time

os.system('cls' if os.name == 'nt' else 'clear') # Cleaning library loading information texts
print("Fetching Libraries.. Please Wait..")



################################################################################################
# Car Env Class
################################################################################################

class CarEnv(gym.Env):
    ############ KEY INIT. FUNC ############

    def __init__(self):
        super(CarEnv, self).__init__()

        self.num_rewards = 3
        self.game_cnt = -1
        self.frame_cnt = -1
        self.START_TIME = time.time()

        self.init_pygame_display()
        self.init_action_obs_spaces()
        self.init_history_variable()
        self.init_lap_counting_vars()

        # ADDED variables
        self.reset()

    ############ VARIABLE INIT. FUNCTIONS BELOW ############

    def init_pygame_display(self):
        pygame.init()
        
        # VIDEO SETTINGS
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.FramePerSec = pygame.time.Clock()

        # Font SETTINGS
        pygame.font.init()
        self.myfont = pygame.font.SysFont("Comic Sans MS", 20)

    def init_lap_counting_vars(self):
        # Lap count/time variables
        self.start_time = pygame.time.get_ticks()       # Start lap timer
        self.lap_count = -1          # Start lap counter
        self.crossed_finish_line = False        # Lap crossed boolean

    def init_action_obs_spaces(self):
        # GYM CONFIGURE
        self.action_space      = gym.spaces.Discrete(5)
        obs_size = 5 + (NUM_WAYPOINTS * 4)
        self.data = np.array([0]*obs_size)
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(obs_size,), dtype=np.float16)
        self.info = {}
        Constants.report(self)

    def init_history_variable(self):
        # data plotting variables
        self.history = {
            "frame": [],
            "game_cnt": [],
            "time": [],
            "v": [],
            "ey": [],
            "ephi": [],
            "s": [],
            "reward": [],
        }
        self.reward_components = [0] * self.num_rewards
        for i in range(self.num_rewards):
            self.history["reward_component" + str(i)] = []
        self.DATA_SAVING_TIMER_START = time.time()      # used to determine when to save history to file
        
    ############ VARIABLE RESET FUNCTIONS BELOW ############

    def save_and_reset_history_data(self):
        # every time_gap [mins], we'll save & reset history data
        # import pdb; pdb.set_trace()
        if (time.time() - self.DATA_SAVING_TIMER_START) / 60 > DATA_SAVING_TIME_GAP:
            self.DATA_SAVING_TIMER_START = time.time()
            dict_to_csv("history.csv", self.history)
            self.init_history_variable()

    def reset_car_pos(self):
        # reset car position and controlling variables
        inital_pos = self.rd.get_initial_position()
        initial_yaw = self.rd.get_initial_yaw()
        self.Agent.reset(inital_pos[0], inital_pos[1], initial_yaw)
        self.throttle, self.delta = 0,0


    ############ ALL THE FAMILIAR/ KEY-IMPORTANT FUNCTIONS BELOW ############

    # reset the game
    def reset(self):
        # re-initialize Agent
        self.Agent       = Car()
        self.Agent_image = spriter("Car")

        # re-initialize road and waypoints objects
        self.rd = Road()           # road object
        self.wp = Waypoints(NUM_WAYPOINTS, self.rd, self.Agent)        # waypoints (target points) object
        self.closest_track_coor = self.rd.orig_track_pts[(self.wp.closest_pt)]
        
        # reset car position & speed
        self.reset_car_pos()
        
        # general agent control vars
        self.action = 0; self.reward = 0

        # Reset lap timer
        self.start_time = pygame.time.get_ticks()
        self.crossed_finish_line = False
        self.lap_count = -1          # Start lap counter
        
        # save/reset history data every few mins
        self.save_and_reset_history_data()
        self.game_cnt += 1      # increment game cnt
        
        return self.get_obs()

    # return the state of the game (so Agent knows its surroundings)
    def get_obs(self) -> np.ndarray:

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
        n = len(self.rd.orig_track_pts)
        wp_coors = [ self.rd.orig_track_pts[(self.wp.closest_pt-1) % n], self.rd.orig_track_pts[(self.wp.closest_pt) % n], self.rd.orig_track_pts[(self.wp.closest_pt + 1) % n] ]
        car_pos = (self.Agent.x, self.Agent.y)
        ey, nearest_wps, self.closest_track_coor = find_ey(car_pos, wp_coors)
        (wp1_x, wp1_y), (wp2_x, wp2_y) = nearest_wps
        wp_yaw = np.arctan2(wp2_y - wp1_y, wp2_x - wp1_x)
        ephi = wp_yaw - self.Agent.yaw
        # get s, wz
        s, wz = self.wp.rd_dist_traversed, self.Agent.wz
        self.data = [self.Agent.v, ey, ephi] + [s, wz] + wp_distances + wp_angles

        # historical data/info accumulation
        if self.frame_cnt % FRAME_SEP == 0:
            # time counting vars
            if len(self.history["frame"]) == 0:
                self.history["frame"].append(0)
                
            else:
                self.history["frame"].append(self.history["frame"][-1]+FRAME_SEP)
            self.history["game_cnt"].append(self.game_cnt)
            self.history["time"].append(round(time.time() - self.START_TIME, 2))
            
            # car data vars
            self.history["v"].append((30/3.3) * self.Agent.v)
            self.history["ey"].append((1/3.3) * ey)
            self.history["ephi"].append(ephi)
            self.history["s"].append((1/3.3) * s)

            # add reward data info to history
            self.history["reward"].append(self.reward)
            for i in range(len(self.reward_components)):
                self.history["reward_component" + str(i)].append(self.reward_components[i])

        return np.array(self.data).astype(np.float16)

    # single timestep update of game
    def step(self, action):
        
        self.render()
        # self.frame_cnt += 1
        self.reward = 0.0
        
        # choose controlling action to either be self.action (manual) or action (agent-controlled)
        ctrl_action = int(action)       # agent control
        # ctrl_action = self.action     # manual control
        
        # Act every x frames. Range can be altered. 
        for _ in range(1):
            # specify agent operations for certain values of A2C's output 'action'
            if ctrl_action == 0:         # do nothing
                self.delta = 0
                self.throttle = 0
            elif ctrl_action == 1:       # increase throttle force
                self.throttle = min(max_throttle, self.throttle + 0.005)
            elif ctrl_action == 2:       # decrease throttle force
                self.throttle = max(-max_throttle, self.throttle - 0.005)
            elif ctrl_action == 3:       # increase delta angle
                self.delta = min(max_steer, self.delta + np.radians(.4))
            elif ctrl_action == 4:       # decrease delta angle
                self.delta = max(-max_steer, self.delta - np.radians(.4))
    
            # UPDATE CAR POSITION
            # self.Agent.pidv(7, self.delta)        # constant speed update
            self.throttle = self.Agent.update(self.throttle, self.delta)       # standard update
            # print([self.Agent.v])        # show action info
        
        # update road and waypoints
        player_x_trans = AGENTX - self.Agent.x
        player_y_trans = AGENTY - self.Agent.y
        self.rd.update(player_x_trans, player_y_trans)
        amt_wps_updated = self.wp.update()      # wps_updated is an int score for the wp update in the range [-1,0,1]

        # rewards -> NOTE: if you update self.reward_components, MAKE SURE TO also update self.num_rewards
        ey, err_yaw = self.data[1], self.data[2]
        self.reward_components = [0.02*(-ey), 0.03*(-err_yaw), 20*amt_wps_updated]
        self.reward += sum(self.reward_components)
        # 1/FPS        # reward for surviving
        # 0.1*self.Agent.v     # reward for moving fast

        # Check if the car has crossed the finish line
        if self.rd.get_intersect_finish_line(self.Agent):
            if not self.crossed_finish_line:
                self.lap_count += 1
                pygame.display.flip()
                self.start_time = pygame.time.get_ticks()
                self.crossed_finish_line = True
        else: self.crossed_finish_line = False

        # # collision detection
        if self.rd.get_has_collided(self.Agent.get_bounding_box()):
            self.reward -= 90      # collision penalty
            done = True
            return self.get_obs(), self.reward, done, self.info

        self.frame_cnt += 1     # increment frame counter
        return self.get_obs(), self.reward, False, self.info
    
    # render entire game to the screen
    # def render_text(self, text, bottom_right_coors):
    #     x, y = bottom_right_coors
    #     my_text = self.myfont.render(text, False, WHITE)
    #     text_rect = my_text.get_rect()
    #     text_rect.bottomright = (x, y)
    #     self.screen.blit(my_text, text_rect)

    # render text & value to the pygame screen
    def render_text_and_value(self, label, val, bottom_right_coors):
        # generate string for label & val
        if not isinstance(val, int):
            text = label + ": " + str(round(val, 2))
        else: text = label + ": " + str(val)

        # show the text
        x, y = bottom_right_coors
        my_text = self.myfont.render(text, False, WHITE)
        text_rect = my_text.get_rect()
        text_rect.bottomright = (x, y)
        self.screen.blit(my_text, text_rect)

    # render all items to the screen
    def render(self):
        # get user key inputs
        for event in pygame.event.get():
            if event.type == pygame.K_SPACE or event.type == pygame.QUIT:       # check if user quit
                pygame.display.quit()
                pygame.quit()
                dict_to_csv("history.csv", self.history)
                del(self)
                quit()
            # MANUAL keystroke car-control inputs
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

        self.rd.draw(self.screen, player_x_trans, player_y_trans)       # draw road
        self.wp.draw(self.screen)       # draw waypoints
        
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

        # Display lap time
        elapsed_time = (pygame.time.get_ticks() - self.start_time) / 1000  # in seconds
        self.render_text_and_value("elapsed time", elapsed_time, (WIDTH - 40, HEIGHT - 20))
        self.render_text_and_value("lap count", self.lap_count, (WIDTH - 40, HEIGHT - 40))
        self.render_text_and_value("reward", self.reward, (WIDTH - 40, HEIGHT - 60))
        self.render_text_and_value("game count", self.game_cnt, (WIDTH - 40, HEIGHT - 80))
        
        # plot(self.speeds, self.dists_from_center, self.rewards)

        pygame.display.flip()       # update display
        #pygame.display.update()
        #self.FramePerSec.tick(FPS)

    def close(self):
        pass
