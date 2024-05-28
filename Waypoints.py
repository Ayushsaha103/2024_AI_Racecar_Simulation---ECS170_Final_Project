
import pygame
import random
import numpy as np
import math
from math_helpers import *
from Constants import *

class Waypoints():
    def __init__(self, npts, rd, car):
        self.closest_pt = 0
        # self.rd = rd
        # self.car = car
        self.npts = npts
    def update_and_draw(self, screen, rd, car, pt_size=4):
        self.update(rd, car)
        self.draw(screen, rd, pt_size)

# waypoints class
class WayPoints():
    # initialization
    def __init__(self, rd):

        self.lanum = 0                  # (initial) lane number to be followed
        l1 = rd.lanes[ rd.lanums[self.lanum][0] ]       # laneline to left of chosen lane
        l2 = rd.lanes[ rd.lanums[self.lanum][1] ]       # laneline to right of chosen lane

        # initial (x,y) coordinate of waypoint
        self.x, self.y = (l1.points[lane_pts_ahead ][0] + l2.points[lane_pts_ahead ][0]) / 2, \
                (l1.points[lane_pts_ahead ][1] + l2.points[lane_pts_ahead ][1]) / 2
        self.nextx, self.nexty = (l1.points[2 * lane_pts_ahead ][0] + l2.points[2 * lane_pts_ahead ][0]) / 2, \
                (l1.points[2 * lane_pts_ahead ][1] + l2.points[2 * lane_pts_ahead ][1]) / 2
        self.s = 0

    # check if waypoint needs to be updated (occurs if car closes in on waypoint)
    def check_for_update(self, car_pos):
        if distance([self.x, self.y], car_pos) < 5: return True
        return False
    
    # update waypoint position
    def update(self, rd, car):
        # # conditionally update the lane which is to be followed
        # if random.randint(0,20) == 0:
        #     if random.randint(0,1) == 0:
        #         if self.lanum + 2 in rd.lanums:
        #             self.lanum += 1
        #     else:
        #         if self.lanum - 1 >= 1:
        #             self.lanum -= 1
        
        # get the two surrounding lanelines (l1 & l2) of our chosen lane
        l1 = rd.lanes[ rd.lanums[self.lanum][0] ]
        l2 = rd.lanes[ rd.lanums[self.lanum][1] ]
        my_pos = [self.x, self.y]

        # find closest index of lane lines to current waypoint position
        mindist = 99999; imin = 0
        for i in range(len(l1.points)):
            dist = distance(l1.points[i], my_pos) + distance(l2.points[i], my_pos)
            if dist < mindist:
                mindist = dist
                imin = i

        # choose a next index of lane lines to set waypoint position close to
        target_idx = imin + lane_pts_ahead
        if target_idx >= len(l1.points): target_idx = -1
        self.x, self.y = self.nextx, self.nexty
        self.nextx, self.nexty = (l1.points[target_idx ][0] + l2.points[target_idx ][0]) / 2, \
                        (l1.points[target_idx ][1] + l2.points[target_idx ][1]) / 2
        self.s += 1

    # draw waypoint on screen
    def draw(self, screen, x_trans, y_trans):
        pygame.draw.circle(screen, RED, (self.x + x_trans, self.y + y_trans), 3)  # Draw a single pixel
    
    def draw(self, screen, rd, pt_size=4):
        n = len(rd.track_points)
        pygame.draw.line(screen, RED, rd.track_points[(self.closest_pt)], (agentx, agenty), 5)

        for i in range(self.npts):
            point = rd.track_points[(self.closest_pt+i)  % n]
            # transformed_pt = (point[0]+player_x_trans, point[1]+player_y_trans)
            pygame.draw.circle(screen, GREEN, point, pt_size)

