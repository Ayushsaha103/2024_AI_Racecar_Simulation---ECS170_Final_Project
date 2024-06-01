
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
        

    def update_and_draw(self, screen, pt_size=4):
        self.update()
        self.draw(screen, pt_size)

    # update which points on the track are the waypoints
    def update(self):
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
        self.closest_pt = closest_idx
    
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
