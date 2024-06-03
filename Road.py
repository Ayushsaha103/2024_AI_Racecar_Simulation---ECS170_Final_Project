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
        self.finish_line_coords = None

        self.reset()

    def reset(self):
        self.done = False

        # generate the original track points
        self.track = generator.generate_racetrack(self.track_length, self.track_width, self.num_curves, self.max_curvature, self.track_number, self.num_pts)
        self.x_fine, self.y_fine, self.left_boundary_x, self.left_boundary_y, self.right_boundary_x, self.right_boundary_y = self.track

        # generate the non-translated track points
        self.orig_track_pts = [(x, y) for x, y in zip(self.x_fine, self.y_fine)]
        self.orig_left_pts = [(x,y) for x, y in zip(self.left_boundary_x, self.left_boundary_y)]
        self.orig_right_pts = [(x,y) for x, y in zip(self.right_boundary_x, self.right_boundary_y)]
        self.generate_translated_track_pts(0,0)

        # zip the original coordinates into a list of points
        self.left_boundary_points = list(zip(self.left_boundary_x, self.left_boundary_y))
        self.right_boundary_points = list(zip(self.right_boundary_x, self.right_boundary_y))

        # Create separate linestrings for the left and right boundaries
        # This is used for collision detection
        self.left_linestring = LineString(self.left_boundary_points)
        self.right_linestring = LineString(self.right_boundary_points)

        
        # Save finish line coordinates
        self.finish_line_coords = (self.left_boundary_points[0], self.right_boundary_points[0])
        
    def generate_translated_track_pts(self, player_x_trans, player_y_trans):
        # translate the original road points by player_x_trans, player_y_trans
        self.translated_track_pts = [(x + player_x_trans, y + player_y_trans) for x, y in zip(self.x_fine, self.y_fine)]
        self.translated_left_pts = [(x + player_x_trans, y + player_y_trans) for x, y in zip(self.left_boundary_x, self.left_boundary_y)]
        self.translated_right_pts = [(x + player_x_trans, y + player_y_trans) for x, y in zip(self.right_boundary_x, self.right_boundary_y)]

    def update(self, player_x_trans, player_y_trans):
        # generate the transformed track points
        self.generate_translated_track_pts(player_x_trans, player_y_trans)
    
    def draw(self, screen, player_x_trans, player_y_trans):
        # Draw the track boundaries
        pygame.draw.lines(screen, RED, False, self.translated_left_pts, 2)
        pygame.draw.lines(screen, RED, False, self.translated_right_pts, 2)
        pygame.draw.lines(screen, BLUE, False, self.translated_track_pts, 2)

        # draw road points
        for i in range(len(self.translated_left_pts)):
            l,m,r = self.translated_left_pts[i], self.translated_track_pts[i], self.translated_right_pts[i]
            pygame.draw.circle(screen, RED, l, 4)
            pygame.draw.circle(screen, BLUE, m, 4)
            pygame.draw.circle(screen, RED, r, 4)
        
        # Draw starting / finish line
        # pygame.draw.line(screen, GREEN, self.left_boundary_points[0]+player_x_trans, self.right_boundary_points[0]+player_y_trans, 5)
        self.finish_line_coords = (self.left_boundary_points[0], self.right_boundary_points[0])

    def update_and_draw(self, screen, player_x_trans, player_y_trans):
        self.update(player_x_trans, player_y_trans)
        self.draw(screen, player_x_trans, player_y_trans)

    def get_initial_position(self):
        # Return the initial position of the car
        return [self.x_fine[0], self.y_fine[0]]
    
    def get_initial_yaw(self):
        # Return the initial yaw of the car
        return np.arctan2(self.y_fine[1] - self.y_fine[0], self.x_fine[1] - self.x_fine[0])

    def get_has_collided(self, car):
        # Check if the car intersects with either linestring
        return self.left_linestring.intersects(car) or self.right_linestring.intersects(
            car
        )
    def get_intersect_finish_line(self, car):
        # Check if the car intersects with the finish line
        car_box = Polygon(car.get_bounding_box())
        finish_line = LineString(self.finish_line_coords)
        return finish_line.intersects(car_box)