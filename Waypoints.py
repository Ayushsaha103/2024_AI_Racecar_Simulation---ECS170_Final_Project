
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

    def update(self, rd, car):
        n = len(rd.track_points)
        car_pos = (agentx, agenty)     # since car is always @ center of screen    # (car.x, car.y)
        mindist = 999999999999
        closest_idx = -1

        for i in range(n):
            d = distance(rd.track_points[(self.closest_pt+i) % n], car_pos)
            if d < mindist:
                mindist = d
                closest_idx = i
        self.closest_pt = closest_idx
    
    def draw(self, screen, rd, pt_size=4):
        n = len(rd.track_points)
        pygame.draw.line(screen, RED, rd.track_points[(self.closest_pt)], (agentx, agenty), 5)

        for i in range(self.npts):
            point = rd.track_points[(self.closest_pt+i)  % n]
            # transformed_pt = (point[0]+player_x_trans, point[1]+player_y_trans)
            pygame.draw.circle(screen, GREEN, point, pt_size)

