
import numpy as np
import pygame
import generator
from Constants import *
from math_helpers import distance
from shapely.geometry import Point
from shapely.geometry.polygon import LineString
from shapely.geometry import Polygon

class Road():
    def __init__(self, track_length=1000, track_width=60, num_curves=25, max_curvature=0.1, track_number=42, num_pts=300):
        self.track_length = track_length
        self.track_width = track_width
        self.num_curves = num_curves
        self.max_curvature = max_curvature
        self.track_number = track_number
        self.num_pts = num_pts

        self.reset()

    def reset(self):
        self.done = False

        # generate the original track points
        self.track = generator.generate_racetrack(self.track_length, self.track_width, self.num_curves, self.max_curvature, self.track_number, self.num_pts)
        self.x_fine, self.y_fine, self.left_boundary_x, self.left_boundary_y, self.right_boundary_x, self.right_boundary_y = self.track

        # generate the non-translated track points
        self.track_points = np.array([(x, y) for x, y in zip(self.x_fine, self.y_fine)])
        self.left_boundary_points = np.array([(x, y) for x, y in zip(self.left_boundary_x, self.left_boundary_y)])
        self.right_boundary_points = np.array([(x, y) for x, y in zip(self.right_boundary_x, self.right_boundary_y)])

        # Create separate linestrings for the left and right boundaries
        # This is used for collision detection
        self.left_linestring = LineString(self.left_boundary_points)
        self.right_linestring = LineString(self.right_boundary_points)

        # save the original non-translated track points into road points
        road_points = self.left_boundary_points + self.right_boundary_points[::-1]
        self.rd_pts_polygon = Polygon(road_points)

        # translated points (originally, without translation)
        self.trans_left_pts = self.left_boundary_points.copy()
        self.trans_right_pts = self.right_boundary_points.copy()
        self.trans_mid_pts = self.track_points.copy()

    # this func. is a place-holder; no updates are needed
    def update(self):
        pass

    def draw(self, screen, player_x_trans, player_y_trans):
        # translate the track points
        translation = (player_x_trans, player_y_trans)
        self.trans_left_pts = self.left_boundary_points+translation
        self.trans_right_pts = self.right_boundary_points+translation
        self.trans_mid_pts = self.track_points+translation

        # draw the translated points
        pygame.draw.lines(screen, RED, False, self.trans_left_pts, 2)
        pygame.draw.lines(screen, RED, False, self.trans_right_pts, 2)
        pygame.draw.lines(screen, BLUE, False, self.trans_mid_pts, 2)

        # # draw road points
        # for i in range(len(trans_mid_pts)):
        #     l = trans_left_pts[i]
        #     m = trans_right_pts[i]
        #     r = trans_mid_pts[i]
        #     pygame.draw.circle(screen, RED, l, 4)
        #     pygame.draw.circle(screen, BLUE, m, 4)
        #     pygame.draw.circle(screen, RED, r, 4)
    def get_initial_position(self):
        # Return the initial position of the car
        return [self.x_fine[0], self.y_fine[0]]
    
    def get_initial_yaw(self):
        # Return the initial yaw of the car
        return np.arctan2(self.y_fine[1] - self.y_fine[0], self.x_fine[1] - self.x_fine[0])

    def check_collision(self, car):
        # Check if the car intersects with either linestring
        return self.left_linestring.intersects(car.get_bounding_box()) or \
            self.right_linestring.intersects(car.get_bounding_box())
        
        # point = Point(car.x, car.y)
        # return not self.rd_pts_polygon.contains(point)


