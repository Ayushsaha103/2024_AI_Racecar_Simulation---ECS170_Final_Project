
import pygame
import numpy as np
import math
import random
#import time
#import sys
#import matplotlib.pyplot as plt
from Constants import *
#from collections import deque
from math_helpers import *


############################################################################################################
# road lanes class

class LaneLine():
    def __init__(self, npoints=50, status='side'):
        self.points = [[agentx,i+agenty-(npoints*1.1)] for i in range(npoints)]
        self.start_pt = [agentx, agenty-(npoints*1.1)]
        self.v = [0, 4]
        self.lane_turning = False
        self.lane_turning_cnter = 0
        self.turn_right = False
        self.status = status

    def draw(self, screen, player_x_trans, player_y_trans):
        if self.status == 'side': color = WHITE
        elif self.status == 'main': color = RED
        for i in range(len(self.points) - 1):
            x1, y1 = self.points[i]
            x2, y2 = self.points[i + 1]
            start_point = (x1+player_x_trans, y1+player_y_trans)
            end_point = (x2+player_x_trans, y2+player_y_trans)
            pygame.draw.aaline(screen, color, start_point, end_point)
    def update_mainLane(self):
        self.start_pt = self.points[int(len(self.points) * 0.8)]

        for i in range(len(self.points)):
            self.points[i] = self.start_pt.copy()
            self.start_pt = add(self.start_pt, self.v)
            if self.lane_turning == True:
                self.v = turn_vector(self.v, self.turn_right)

                if self.lane_turning_cnter == random.randint(20,40) or self.lane_turning_cnter > 40:
                    self.lane_turning_cnter = 0
                    self.lane_turning = False
                self.lane_turning_cnter += 1
                
            elif self.lane_turning == False and random.randint(0,40) == 0:
                self.lane_turning = True

                self.turn_right = 0
                if random.randint(0,1): self.turn_right = 1
    
    #self.start_pt = self.points[-1]
    #def reset_mainLane(self):
    #    self.
    def update_sideLane(self, mainLane, dist=1, right_dir=True):
        p2 = [0,0]
        for i in range(len(self.points)-1):
            p1, p2 = calculate_parallel_points(mainLane.points[i], mainLane.points[i+1], dist, right_dir)
            self.points[i] = list(p1)
        self.points[-1] = list(p2)
    def reset_pos(self, dx, dy):
        for i in range(len(self.points)):
            self.points[i][0] += dx
            self.points[i][1] += dy
        self.start_pt[0] += dx
        self.start_pt[1] += dy

class Road():
    def __init__(self, nlanes=10, npoints=70):
        self.lanes = [LaneLine(npoints) for i in range(nlanes + 1)]
        self.lanes[0] = LaneLine(npoints, status='main')


        ###### LANE NUMBERS #######
        #           M
        # |    |    |   |   |   |
        # | -2 | -1 | 0 | 1 | 2 |
        # |    |    |   |   |   |

        self.lanums = {0:[0,1]}
        for i in range(1, len(self.lanes)):
            if (i-1)*2 + 3 >= len(self.lanes): break
            self.lanums[i] = [(i-1)*2 + 1, (i-1)*2 + 3]

            if i*2 >= len(self.lanes): break
            self.lanums[-i] = [i*2, i*2 - 2]
        print(self.lanums)


    def draw(self, screen, player_x_trans, player_y_trans):
        for i in range(len(self.lanes)):
            self.lanes[i].draw(screen, player_x_trans, player_y_trans)
    def update(self):
        
        self.lanes[0].update_mainLane()

        nright_lanes = (len(self.lanes) - 1) // 2
        #nleft_lanes = (len(self.lanes) - 1) - nright_lanes

        #for i in range(1, nright_lanes):
            #self.lanes[i].update_sideLane(self.lanes[0], dist = i*6, right_dir=True)

        for i in range(1, len(self.lanes)):
            #self.lanes[i].update_sideLane(self.lanes[0], dist = i*6, right_dir=True)
            if i%2 == 1: self.lanes[i].update_sideLane(self.lanes[0], dist = 0.5*(i+1)*12, right_dir=True)
            else: self.lanes[i].update_sideLane(self.lanes[0], dist = (0.5*i)*12, right_dir=False)

        #for i in range(nright_lanes, len(self.lanes)):
        #    self.lanes[i].update_sideLane(self.lanes[0], dist = (i+1-nright_lanes)*6, right_dir=False)
    def check_for_update(self, car_pos):
        for i in range(len(self.lanes)):
            if distance(car_pos, self.lanes[i].points[-1]) < 30:
                return True
        return False
    def reset_pos(self, dx, dy):
        for i in range(len(self.lanes)):
            self.lanes[i].reset_pos(dx, dy)
