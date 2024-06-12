import pygame
import random
import numpy as np
import math
from math_helpers import *
from Constants import *


class Waypoints:
    def __init__(self, npts, rd, car):
        self.npts = npts  # num. of points included in "Waypoints"

        # references to road and car objects
        self.rd = rd
        self.car = car
        self.reset()

    def reset(self):
        self.rd_dist_traversed = 0  # total distance traversed along road
        self.closest_pt = 0  # idx of closest point on road track to the car
        self.TARGET_PT_DISPLACEMENT = 1
        self.first_target_pt = self.TARGET_PT_DISPLACEMENT
        self.just_updated = False

    # update the waypoints
    # return the number of progressive indices moved forward (IF UPDATE OCCURS)
    def update(self):
        idxs_updated = 0
        stepwise_dist_traversed = 0
        self.just_updated = False
        n = len(self.rd.track_points)
        car_pos = (self.car.x, self.car.y)
        mindist = 999999999999
        closest_idx = -1

        # find closest point on road track points to car
        for i in range(n):
            d = distance(self.rd.track_points[(i) % n], car_pos)
            if d <= mindist:
                mindist = d
                closest_idx = i

        # set "self.closest_pt" as the closest track index
        if self.closest_pt != closest_idx:
            idxs_updated = 1
            stepwise_dist_traversed = distance(
                self.rd.track_points[self.closest_pt % n],
                self.rd.track_points[closest_idx % n],
            )

            # negate update counters if waypoints updated in wrong direction
            if self.closest_pt > closest_idx and not (
                self.closest_pt > 0.75 * n and closest_idx < 0.25 * n
            ):
                idxs_updated *= -1
                stepwise_dist_traversed *= -1

            # update total road dist traversed and closest_idx
            self.rd_dist_traversed += stepwise_dist_traversed
            self.closest_pt = closest_idx
            self.first_target_pt = (self.closest_pt + self.TARGET_PT_DISPLACEMENT) % n
            self.just_updated = True

        return stepwise_dist_traversed
        # return idxs_updated     # num. of indices the waypoints obj has moved by

    # draw the waypoints onto the screen
    def draw(self, screen, player_x_trans, player_y_trans):
        # # draw line to nearest waypoint
        # pygame.draw.line(screen, RED, self.rd.translated_track_pts[(self.closest_pt)], (AGENTX, AGENTY), 5)
        # translation = (player_x_trans, player_y_trans)

        n = len(self.rd.track_points)
        for i in range(self.npts):
            m = self.rd.trans_mid_pts[(self.first_target_pt + i) % n]
            pygame.draw.circle(screen, GREEN, m, 4)

            # l = self.rd.trans_left_pts[(self.closest_pt+i)  % n]
            # r = self.rd.trans_right_pts[(self.closest_pt+i)  % n]
            # pygame.draw.circle(screen, GREEN, l, 4)
            # pygame.draw.circle(screen, GREEN, r, 4)
