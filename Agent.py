import pygame
from Constants import *
import os


import math
import numpy as np
from collections import deque
from Agent_helpers import *
from math_helpers import *

from shapely.geometry import box
from shapely.affinity import rotate, translate


# car constants
max_steer = np.radians(32.0)  # [rad] max steering angle
max_throttle = 1.0             # [?] max throttle force
max_v = 4.0                    # [?] max velocity
# max_v * (30) = v [pixels/s]
# 1 [m] = 3.3 [pixels]
# max_v * (30/3.3) = true max speed = 36 [m/s]

L = 7.9  # [m] Wheel base of vehicle
dt = 0.8
m = 1500.0  # kg


################################################################################################
# Car class
################################################################################################

def calc_av_dyaw_dt(values):
    # Convert the input to a numpy array if it isn't already
    values = np.array(values)
    # Calculate the differences between consecutive elements
    differences = np.diff(values)
    # Calculate and return the average of these differences
    average_diff = np.mean(differences) / dt
    return average_diff

class Car(pygame.sprite.Sprite):
    # init.
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.pedals = PID(0.8,0.1,0.05, 6)      # pid controller initialization (this is a controller used to maintain const. velocity)
        self.reset()

    # reset car position, speed, and yaw
    def reset(self, x=WIDTH / 2, y=HEIGHT / 2, yaw=math.pi/2, v=0.0):
        self.x = x
        self.y = y
        self.yaw = yaw
        self.v = v
        self.tot_dist_traveled = 0
        self.wz = 0
        self.prev_yaws = [yaw]*4
        self.delta = 0; self.throttle = 0
        self.update_bounding_box()
        # self.pedals.reset()

    # update the car position so as to maintain const. velocity
    def pidv(self, vset, delta):
        throttle = 1*self.pedals.push(self.v,vset)
        self.update(throttle,delta)

    # update the car position, given throttle reset_posforce & delta
    def update(self, throttle, delta):
        delta = np.clip(delta, -max_steer, max_steer)
        throttle = np.clip(throttle, -max_throttle, max_throttle)
        self.v = np.clip(self.v, 0, max_v)
        if self.v == 0: throttle = 0.00001

        self.x += self.v * np.cos(self.yaw) * dt
        self.y += self.v * np.sin(self.yaw) * dt
        yaw_del = (0.0067*L / (0.01*self.v+0.1)) * np.tan(delta) * dt
        self.yaw += yaw_del
        self.yaw = normalize_angle(self.yaw)
        self.v += throttle * dt
        self.tot_dist_traveled += self.v * dt

        # calculate wz
        self.prev_yaws.pop(0)
        self.prev_yaws.append(self.yaw)
        # self.wz = yaw_del       # todo: change this to be an average of the last few yaw_del's
        self.wz = calc_av_dyaw_dt(self.prev_yaws)
        self.delta = delta
        self.throttle = throttle
        self.update_bounding_box()

        return throttle

    def update_bounding_box(self):
        # create a rectangle from the point, width, height, and angle
        bounding_box = box(-CAR_WIDTH / 2, -CAR_HEIGHT / 2, CAR_WIDTH / 2, CAR_HEIGHT / 2)
        self.bounding_box = rotate(bounding_box, self.yaw, use_radians=True)
        self.bounding_box = translate(self.bounding_box, self.x, self.y)

