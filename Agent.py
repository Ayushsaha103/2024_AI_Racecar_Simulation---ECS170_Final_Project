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
max_steer = np.radians(32.0)  # [rad] max steering angle
max_throttle = 1.0             # [?] max throttle force
max_v = 4.0                    # [?] max velocity

L = 7.9  # [m] Wheel base of vehicle
dt = 0.8
m = 1500.0  # kg


################################################################################################
# Car class
################################################################################################

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
        self.yaw_del = 0
        self.v = v
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
        if self.v == 0: throttle = 0.01

        self.x += self.v * np.cos(self.yaw) * dt
        self.y += self.v * np.sin(self.yaw) * dt
        self.yaw_del = self.v / L * np.tan(delta) * dt
        self.yaw += self.yaw_del
        self.yaw = normalize_angle(self.yaw)
        self.v += throttle * dt

        # print("velocity [m/s]: " + str(self.v))

        # print([throttle, delta, self.v])
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

    # # # OLD FUNCTION FROM PREVIOUS VERSION (ayush1 branch)
    # # return True if car collides with road (rd) edge
    # def check_cross_rd_bounds(self, rd):
    # l1 = len(rd.lanes) - 1
    # l2 = len(rd.lanes) - 2
    # l1 = rd.lanes[l1]; l2 = rd.lanes[l2]

    # mindist1, mindist2 = 99999, 99999
    # i1, i2 = 0, 0
    # mindist_midlane = 99999; imid = 0; lmid = rd.lanes[0]
    # for i in range(len(l1.points)-1):
    #     sum_pt_dist1 = distance(l1.points[i], [self.x, self.y]) + distance(l1.points[i+1],  [self.x, self.y])
    #     if sum_pt_dist1 < mindist1:
    #         mindist1 = sum_pt_dist1
    #         i1 = i
    #     sum_pt_dist2 = distance(l2.points[i], [self.x, self.y]) + distance(l2.points[i+1],  [self.x, self.y])
    #     if sum_pt_dist2 < mindist2:
    #         mindist2 = sum_pt_dist2
    #         i2 = i
    #     sum_pt_distmid = distance(lmid.points[i], [self.x, self.y]) + distance(lmid.points[i+1],  [self.x, self.y])
    #     if sum_pt_distmid < mindist_midlane:
    #         mindist_midlane = sum_pt_distmid
    #         imid = i
    # if is_point_to_left_or_right(l1.points[i1], l1.points[i1+1], [self.x, self.y]) != 'right':
    #     return True
    # if is_point_to_left_or_right(l2.points[i2], l2.points[i2+1], [self.x, self.y]) != 'left':
    #     return True
    # if is_yaw_opposite_to_vector(self.yaw, lmid.points[imid], lmid.points[imid+1]):
    #     return True

    # return False
