
import pygame
import random
import numpy as np
import math
from math_helpers import *
from Constants import *

class Waypoints():
    def __init__(self, npts, rd, car):
        self.closest_pt = 0     # idx of closest point on road track to the car
        self.npts = npts        # num. of points included in "Waypoints"
        
        # references to road and car objects
        self.rd = rd
        self.car = car
        self.rd_dist_traversed = 0
        
    # update & draw the waypoints obj
    def update_and_draw(self, screen, pt_size=4):
        num_idxs_updated = self.update()     # this value indicates the number of progressive steps taken forward by the entire waypoints system
        self.draw(screen, pt_size)
        return num_idxs_updated

    # update the waypoints
    # return the number of progressive indices moved forward
    def update(self):
        idxs_updated = 0
        n = len(self.rd.translated_track_pts)
        car_pos = (AGENTX, AGENTY)
        mindist = 999999999999
        closest_idx = -1

        # find closest point on road track points to car
        for i in range(n):
            d = distance(self.rd.translated_track_pts[(i) % n], car_pos)
            if d <= mindist:
                mindist = d
                closest_idx = i
        # set "self.closest_pt" as the closest track index
        if self.closest_pt != closest_idx:
            idxs_updated = min_distance(self.closest_pt, closest_idx, n)
            stepwise_dist_traversed = distance(self.rd.translated_track_pts[self.closest_pt % n], self.rd.translated_track_pts[closest_idx % n])

            if self.closest_pt > closest_idx and not (self.closest_pt > 0.75*n and closest_idx < 0.25*n):
                idxs_updated *= (-1)
                stepwise_dist_traversed *= (-1)
            self.rd_dist_traversed += stepwise_dist_traversed
            
            self.closest_pt = closest_idx
            

        return idxs_updated     # num. of indices the waypoints obj has moved by
    
    # draw the waypoints onto the screen
    def draw(self, screen, pt_size=4):
        # # draw line to nearest waypoint
        # pygame.draw.line(screen, RED, self.rd.translated_track_pts[(self.closest_pt)], (AGENTX, AGENTY), 5)

        # draw the waypoints
        n = len(self.rd.translated_track_pts)
        for i in range(self.npts):
            point1 = self.rd.translated_left_pts[(self.closest_pt+i)  % n]
            point2 = self.rd.translated_right_pts[(self.closest_pt+i)  % n]
            pygame.draw.circle(screen, GREEN, point1, pt_size)
            pygame.draw.circle(screen, GREEN, point2, pt_size)
