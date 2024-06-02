import pygame
import Constants
import os


import math
import numpy as np
from collections import deque
from Agent_helpers import *
from math_helpers import *

from shapely.geometry import box
from shapely.affinity import rotate, translate

# Screen
WIDTH, HEIGHT =  Constants.WIDTH, Constants.HEIGHT


# car constants
max_steer = np.radians(16.0)  # [rad] max steering angle
max_throttle = 0.5            # [?] max throttle force
max_v = 7.0                   # [?] max velocity

L = 6  # [m] Wheel base of vehicle
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
        self.traveled = 0
        self.wz = 0
        self.prev_yaws = [yaw]*4
        self.pedals.reset()
    
    # update the car position so as to maintain const. velocity
    def pidv(self, vset, delta):
        throttle = 1*self.pedals.push(self.v,vset)
        self.update(throttle,delta)

    # update the car position, given throttle reset_posforce & delta
    def update(self, throttle, delta):
        delta = np.clip(delta, -max_steer, max_steer)
        throttle = np.clip(throttle, -max_throttle, max_throttle)
        self.v = np.clip(self.v, 0, max_v)
        # if self.v == 0: throttle = 0.01

        self.x += self.v * np.cos(self.yaw) * dt
        self.y += self.v * np.sin(self.yaw) * dt
        self.traveled += self.v * dt
        yaw_del = min(self.v, 1.5) / L * np.tan(delta) * dt
        self.yaw += yaw_del
        self.yaw = normalize_angle(self.yaw)
        self.v += throttle * dt
        self.traveled += self.v * dt

        # calculate wz
        self.prev_yaws.pop(0)
        self.prev_yaws.append(self.yaw)
        self.wz = calc_av_dyaw_dt(self.prev_yaws)

        return throttle

    def get_bounding_box(self):
        # these values found in Constants.py
        width = 80 / 10
        height = (8 / 30) * 621 / 10

        # create a rectangle from the point, width, height, and angle
        bounding_box = box(-width / 2, -height / 2, width / 2, height / 2)
        bounding_box = rotate(bounding_box, self.yaw, use_radians=True)
        bounding_box = translate(bounding_box, self.x, self.y)

        return bounding_box
