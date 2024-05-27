import numpy as np
import pygame
from pygame.locals import *
from gym import Env, spaces

import generator

class RacetrackEnv(Env):
    def __init__(self, track_length=1000, track_width=10, num_curves=25, max_curvature=0.15, track_number=42):
        super(RacetrackEnv, self).__init__()
        self.track_length = track_length
        self.track_width = track_width
        self.num_curves = num_curves
        self.max_curvature = max_curvature
        self.track_number = track_number

        self.track = generator.generate_racetrack(self.track_length, self.track_width, self.num_curves, self.max_curvature, self.track_number)
        self.x_fine, self.y_fine, self.left_boundary_x, self.left_boundary_y, self.right_boundary_x, self.right_boundary_y = self.track

        self.screen_width = 800
        self.screen_height = 600

        self.action_space = spaces.Discrete(4)  # Forward, backward, left, right
        self.observation_space = spaces.Box(
            low=np.array([0, 0, -np.inf]), high=np.array([self.screen_width, self.screen_height, np.inf]), dtype=np.float32)

        self.car = pygame.Surface((10, 5), pygame.SRCALPHA)  # Smaller car
        pygame.draw.polygon(self.car, (0, 255, 0), [(0, 0), (10, 2.5), (0, 5)])

        self.reset()

    def reset(self):
        # Place the car at the starting point of the track
        self.car_x = self.x_fine[0]
        self.car_y = self.y_fine[0]
        self.car_velocity = 0
        self.car_angle = 0
        self.done = False
        return np.array([self.car_x, self.car_y, self.car_velocity])

    def step(self, action):
        max_velocity = 5  # Adjusted speed
        min_velocity = -2  # allowing for some reverse movement
        friction = 0.1  # friction coefficient

        if action == 0:  # Forward
            self.car_velocity = min(self.car_velocity + 0.5, max_velocity)
        elif action == 1:  # Backward
            self.car_velocity = max(self.car_velocity - 0.5, min_velocity)
        elif action == 2:  # Left
            self.car_angle -= 5
        elif action == 3:  # Right
            self.car_angle += 5

        # Apply friction to the car's velocity
        if self.car_velocity > 0:
            self.car_velocity = max(0, self.car_velocity - friction)
        elif self.car_velocity < 0:
            self.car_velocity = min(0, self.car_velocity + friction)

        # Update the car's position based on its velocity and angle
        self.car_x += int(self.car_velocity * np.cos(np.radians(self.car_angle)))
        self.car_y += int(self.car_velocity * np.sin(np.radians(self.car_angle)))

        state = np.array([self.car_x, self.car_y, self.car_velocity])
        reward = 0
        done = False
        info = {}

        return state, reward, done, info

    def render(self, mode='human'):
        pygame.init()
        screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Racetrack Environment")
        clock = pygame.time.Clock()

        zoom_factor = 1  # Adjust this factor to zoom in or out

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False

            keys = pygame.key.get_pressed()
            if keys[K_w]:  # Forward
                self.step(0)
            if keys[K_s]:  # Backward
                self.step(1)
            if keys[K_a]:  # Left
                self.step(2)
            if keys[K_d]:  # Right
                self.step(3)

            screen.fill((255, 255, 255))

            offset_x = self.screen_width // 2 - self.car_x * zoom_factor
            offset_y = self.screen_height // 2 - self.car_y * zoom_factor

            track_points = [(x * zoom_factor + offset_x, y * zoom_factor + offset_y) for x, y in zip(self.x_fine, self.y_fine)]
            left_boundary_points = [(x * zoom_factor + offset_x, y * zoom_factor + offset_y) for x, y in zip(self.left_boundary_x, self.left_boundary_y)]
            right_boundary_points = [(x * zoom_factor + offset_x, y * zoom_factor + offset_y) for x, y in zip(self.right_boundary_x, self.right_boundary_y)]

            # Draw the road as a filled polygon
            road_points = left_boundary_points + right_boundary_points[::-1]
            pygame.draw.polygon(screen, (128, 128, 128), road_points)

            # Draw the track boundaries
            pygame.draw.lines(screen, (0, 0, 255), False, left_boundary_points, 2)
            pygame.draw.lines(screen, (255, 0, 0), False, right_boundary_points, 2)
            # pygame.draw.lines(screen, (0, 255, 0), False, track_points, 2)

            # Rotate and draw the car
            rotated_car = pygame.transform.rotate(self.car, -self.car_angle)
            car_rect = rotated_car.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            screen.blit(rotated_car, car_rect.topleft)

            pygame.display.flip()
            clock.tick(30)

    def hasCollided(self):
        error_margin = 5

        # Check if collided with the right boundary
        for x, y in zip(self.right_boundary_x, self.right_boundary_y):
            if (
                abs(x - self.car_x) < error_margin
                and abs(y - self.car_y) < error_margin
            ):
                return True

        # Check if collided with the left boundary
        for x, y in zip(self.left_boundary_x, self.left_boundary_y):
            if (
                abs(x - self.car_x) < error_margin
                and abs(y - self.car_y) < error_margin
            ):
                return True

        return False

    def close(self):
        pygame.quit()


if __name__ == "__main__":
    env = RacetrackEnv()
    env.reset()
    done = False

    while not done:
        env.render()
        pygame.time.wait(100)

    env.close()
