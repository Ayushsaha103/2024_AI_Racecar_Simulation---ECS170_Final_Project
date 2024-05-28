
import numpy as np
import pygame
import generator

class Racetrack():
    def __init__(self, track_length=1000, track_width=30, num_curves=25, max_curvature=0.1, track_number=42):
        self.track_length = track_length
        self.track_width = track_width
        self.num_curves = num_curves
        self.max_curvature = max_curvature
        self.track_number = track_number

        self.reset()

    def reset(self):
        self.done = False
        self.track = generator.generate_racetrack(self.track_length, self.track_width, self.num_curves, self.max_curvature, self.track_number)
        self.x_fine, self.y_fine, self.left_boundary_x, self.left_boundary_y, self.right_boundary_x, self.right_boundary_y = self.track

    def update(self):
        pass
    def check_for_update(self, car_pos):
        pass

    def draw(self, screen, player_x_trans, player_y_trans, zoom_factor=1.0):
        track_points = [(x * zoom_factor + player_x_trans, y * zoom_factor + player_y_trans) for x, y in zip(self.x_fine, self.y_fine)]
        left_boundary_points = [(x * zoom_factor + player_x_trans, y * zoom_factor + player_y_trans) for x, y in zip(self.left_boundary_x, self.left_boundary_y)]
        right_boundary_points = [(x * zoom_factor + player_x_trans, y * zoom_factor + player_y_trans) for x, y in zip(self.right_boundary_x, self.right_boundary_y)]

        # Draw the road as a filled polygon
        road_points = left_boundary_points + right_boundary_points[::-1]
        pygame.draw.polygon(screen, (128, 128, 128), road_points)

        # Draw the track boundaries
        pygame.draw.lines(screen, (0, 0, 255), False, left_boundary_points, 2)
        pygame.draw.lines(screen, (255, 0, 0), False, right_boundary_points, 2)
        pygame.draw.lines(screen, (0, 255, 0), False, track_points, 2)
