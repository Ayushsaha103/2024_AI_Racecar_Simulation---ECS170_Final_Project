
import numpy as np
import pygame
import generator
from Constants import *
from math_helpers import distance
from shapely.geometry import Point
from shapely.geometry.polygon import LineString


class Road():
    def __init__(self, track_length=1000, track_width=50, num_curves=25, max_curvature=0.1, track_number=42, num_pts=400):
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
        self.generate_track_pts(0,0)

        # # tell whether car is inside road (does NOT work)
        # road_points = self.left_boundary_points + self.right_boundary_points[::-1]
        # from shapely.geometry import Point
        # from shapely.geometry.polygon import Polygon
        # point = Point(AGENTX, AGENTY)
        # polygon = Polygon(road_points)
        # print("THIS: " + str(polygon.contains(point)))
    
    def generate_track_pts(self, player_x_trans, player_y_trans):
        # translate the original road points by player_x_trans, player_y_trans
        self.track_points = [(x + player_x_trans, y + player_y_trans) for x, y in zip(self.x_fine, self.y_fine)]
        self.left_boundary_points = [(x + player_x_trans, y + player_y_trans) for x, y in zip(self.left_boundary_x, self.left_boundary_y)]
        self.right_boundary_points = [(x + player_x_trans, y + player_y_trans) for x, y in zip(self.right_boundary_x, self.right_boundary_y)]

    def update_and_draw(self, screen, player_x_trans, player_y_trans):
        # generate the transformed track points
        self.generate_track_pts(player_x_trans, player_y_trans)

        # Draw the track boundaries
        pygame.draw.lines(screen, RED, False, self.left_boundary_points, 2)
        pygame.draw.lines(screen, RED, False, self.right_boundary_points, 2)
        pygame.draw.lines(screen, BLUE, False, self.track_points, 2)

        # draw road points
        for i in range(len(self.left_boundary_points)):
            l,m,r = self.left_boundary_points[i], self.track_points[i], self.right_boundary_points[i]
            pygame.draw.circle(screen, RED, l, 4)
            pygame.draw.circle(screen, BLUE, m, 4)
            pygame.draw.circle(screen, RED, r, 4)

    def get_has_collided(self, car):
        # create a polygon from the road boundaries
        left_boundary_points = list(zip(self.left_boundary_x, self.left_boundary_y))
        right_boundary_points = list(zip(self.right_boundary_x, self.right_boundary_y))

        # Create separate linestrings for the left and right boundaries
        left_linestring = LineString(left_boundary_points)
        right_linestring = LineString(right_boundary_points)

        # Check if the car intersects with either linestring
        return left_linestring.intersects(car) or right_linestring.intersects(car)