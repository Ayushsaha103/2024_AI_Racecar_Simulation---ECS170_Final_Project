import os

import pygame
from pygame.locals import *

import numpy as np
import gymnasium as gym
from gymnasium import spaces

import Constants
from Constants import *
from Agent import *
from Road import *
from Waypoints import *
from math_helpers import *
from obs_data import *
from timer import *
from Training_dojo import *
import math


os.system(
    "cls" if os.name == "nt" else "clear"
)  # Cleaning library loading information texts
print("Fetching Libraries.. Please Wait..")


################################################################################################
# Car Env Class
################################################################################################


class CarEnv(gym.Env):
    def __init__(self, limit=0):
        super(CarEnv, self).__init__()
        pygame.init()

        # VIDEO SETTINGS
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.FramePerSec = pygame.time.Clock()

        # Font SETTINGS
        pygame.font.init()
        self.myfont = pygame.font.SysFont("Comic Sans MS", 20)

        # Physical CONSTANTS
        self.FPS = FPS

        # GAME CONFIGURE
        # self.reward = 0

        # initialize agent, road, waypoints, car, obs_data, and rewards_data
        self.car = Car()
        self.car_image = spriter("Car")

        self.rd = Road()  # road object
        self.wp = Waypoints(
            NUM_WAYPOINTS, self.rd, self.car
        )  # waypoints (target points) object
        self.obs = Obs_data(self.rd, self.wp, self.car, OBS_SIZE)
        self.tim = Timer()
        # self.rw = Rewards_data(self.obs, self.car, self.tim, NUM_REWARDS)
        self.dojo = Training_dojo(self.rd, self.wp, self.car, self.obs, self.tim)

        # GYM CONFIGURE
        self.action_space = gym.spaces.Discrete(5)
        self.obs_size = OBS_SIZE
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(self.obs_size,), dtype=np.float16
        )
        self.info = {}
        Constants.report(self)

        self.limit = limit
        self.counter = 0

        self.reset()

    # reset the game
    def reset(self, seed=None):
        # reset road, waypoints, and obs_data objects
        self.rd.reset()
        self.wp.reset()
        self.obs.reset()
        self.tim.reset()
        # self.rw.reset()
        self.dojo.reset()

        # reset car position
        inital_pos = self.rd.get_initial_position()
        initial_yaw = self.rd.get_initial_yaw()
        self.car.reset(inital_pos[0], inital_pos[1], initial_yaw)

        # car/game control variables
        self.throttle, self.delta = 0, 0
        self.action = 0
        self.reward = 0

        self.counter = 0

        return self.get_obs(), self.info

    # return the state of the game (so Agent knows its surroundings)
    def get_obs(self) -> np.ndarray:
        return self.obs.get_state()

    # single timestep update of game
    def step(self, action):
        self.counter += 1

        self.render()

        # choose controlling action to either be self.action (manual) or action (agent-controlled)
        # ctrl_action = self.action   # manual ctrl
        ctrl_action = int(action)  # agent ctrl

        # Act every x frames. Range can be altered.
        for _ in range(1):
            # specify agent operations for certain values of A2C's output 'action'
            if ctrl_action == 0:  # do nothing
                self.delta = 0
                self.throttle = 0
            elif ctrl_action == 1:  # increase throttle force
                self.throttle = min(max_throttle, self.throttle + 0.003)
            elif ctrl_action == 2:  # decrease throttle force
                self.throttle = max(-max_throttle, self.throttle - 0.004)
            elif ctrl_action == 3:  # increase delta angle
                self.delta = min(max_steer, self.delta + np.radians(0.4))
            elif ctrl_action == 4:  # decrease delta angle
                self.delta = max(-max_steer, self.delta - np.radians(0.4))

            # UPDATE CAR POSITION
            self.car.pidv(self.dojo.vary_speed(), self.delta)  # constant speed update
            # self.throttle = self.car.update(self.throttle, self.delta)       # standard update

            # update road & waypoints
            self.rd.update()
            self.wp.update()

            # check collision
            if self.rd.check_collision(self.car) or self.dojo.terminate():
                # print("COLLISION!")
                done = True
                return (
                    self.get_obs(),
                    self.dojo.collision_reward(),
                    done,
                    False,
                    self.info,
                )

        truncated = False

        if self.limit != 0 and self.counter >= self.limit:
            truncated = True

        # update reward value
        # self.reward = self.rw.get_reward()
        # return self.get_obs(), self.rw.get_reward(), False, self.info
        self.reward = self.dojo.reward()
        return self.get_obs(), self.reward, False, truncated, self.info

    # render text & value to the pygame screen
    def render_text_and_value(self, label, val, bottom_right_coors):
        # generate string for label & val
        if not isinstance(val, int):
            text = label + ": " + str(round(val, 4))
        else:
            text = label + ": " + str(val)

        # show the text
        x, y = bottom_right_coors
        my_text = self.myfont.render(text, False, WHITE)
        text_rect = my_text.get_rect()
        text_rect.bottomright = (x, y)
        self.screen.blit(my_text, text_rect)

    # render entire game to the screen
    def render(self):
        # get user key inputs
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # check if user quit
                pygame.display.quit()
                pygame.quit()
                del self
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
        player_x_trans = AGENTX - self.car.x
        player_y_trans = AGENTY - self.car.y

        # draw road
        self.rd.draw(self.screen, player_x_trans, player_y_trans)
        # draw waypoint
        self.wp.draw(self.screen, player_x_trans, player_y_trans)
        # draw player
        player_sprite = self.car_image[0]
        player_copy = pygame.transform.rotate(
            player_sprite, -math.degrees(self.car.yaw + (np.pi / 2))
        )
        self.screen.blit(
            player_copy,
            (
                AGENTX - int(player_copy.get_width() / 2),
                AGENTY - int(player_copy.get_height() / 2),
            ),
        )

        ## Update the display
        self.screen.blit(
            pygame.transform.flip(self.screen, False, True), (0, 0)
        )  # mirror screen vertical

        # display relevant info to screen
        self.render_text_and_value(
            "game time", self.tim.get_time_elapsed("game"), (WIDTH - 40, HEIGHT - 20)
        )
        self.render_text_and_value("speed", self.dojo.vset, (WIDTH - 40, HEIGHT - 40))
        self.render_text_and_value("reward", self.reward, (WIDTH - 40, HEIGHT - 60))

        pygame.display.flip()  # update display
        # pygame.display.update()
        # self.FramePerSec.tick(self.FPS)

    def close(self):
        pass
