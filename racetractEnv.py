import numpy as np
import pygame
from pygame.locals import *
from gymnasium import Env, spaces
import generator
from typing import Optional
import utils
import gymnasium
import random

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
MAX_VELOCITY = 12
MIN_VELOCITY = 0
FRICTION = 0.0

# Assumed boundaries for the different observations
x_min, x_max = -1000, 1000  # For car_x and car_y
velocity_min, velocity_max = MIN_VELOCITY, MAX_VELOCITY  # For car_velocity
angle_min, angle_max = 0, 360  # For car_angle
distance_min, distance_max = 0, 50  # For distance to boundaries
lidar_min, lidar_max = 0, 600  # For LiDAR readings
time_min, time_max = 0, 100  # For lap time
angular_velocity_min, angular_velocity_max = -360, 360  # For angular velocity

# Number of waypoints (fixed)
num_waypoints = 10

# Number of LiDAR readings
num_lidar_readings = 8

# Extend the observation space
observation_space = spaces.Box(
    low=np.array([
        velocity_min,  # car_velocity
        angular_velocity_min,  # angular_velocity
        distance_min,  # distance_traveled
        distance_min,  # distance_from_center
        time_min,  # current_lap_time
        -np.inf,  # curvature
        *([lidar_min] * num_lidar_readings)  # LiDAR readings
    ]),
    high=np.array([
        velocity_max,  # car_velocity
        angular_velocity_max,  # angular_velocity
        distance_max,  # distance_traveled
        distance_max,  # distance_from_center
        time_max,  # current_lap_time
        np.inf,  # curvature
        *([lidar_min] * num_lidar_readings)  # LiDAR readings
    ]),
    dtype=np.float32
)

class RacetrackEnv(gymnasium.Env):
    def __init__(self, track_length=1000, track_width=40, num_curves=20, max_curvature=0.12, track_number=random.randint(0,1000), render_mode='human'):
        super(RacetrackEnv, self).__init__()
        self.track_length = track_length
        self.track_width = track_width
        self.num_curves = num_curves
        self.max_curvature = max_curvature
        self.track_number = track_number
        self.render_mode = render_mode

        pygame.init()
        self.clock = None
        self.game_time = 0
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        self.track = generator.generate_racetrack(self.track_length, self.track_width, self.num_curves, self.max_curvature, self.track_number)
        self.x_fine, self.y_fine, self.left_boundary_x, self.left_boundary_y, self.right_boundary_x, self.right_boundary_y = self.track

        # Continuous action space: [steering, acceleration]
        self.action_space = spaces.Box(low=np.array([-1, -1]), high=np.array([1, 1]), dtype=np.float32)

        self.observation_space = observation_space
        self.car = pygame.image.load('car_sprite.png')  # Make sure 'car_sprite.png' exists
        self.car = pygame.transform.scale(self.car, (30, 20))  # Adjust size as necessary

        self.reset()

    def reset(self, *, seed: Optional[int] = None, options: Optional[dict] = None):
        super().reset(seed=seed)
        self.clock = pygame.time.Clock()
        self.car_x = self.x_fine[0]
        self.car_y = self.y_fine[0]
        self.car_velocity = 0
        self.reward = 0

        self.track_number = random.randint(0, 100000)

        self.track = generator.generate_racetrack(self.track_length, self.track_width, self.num_curves, self.max_curvature, self.track_number)
        self.x_fine, self.y_fine, self.left_boundary_x, self.left_boundary_y, self.right_boundary_x, self.right_boundary_y = self.track
        # Reset car position and angle
        self.car_x = self.x_fine[0]
        self.car_y = self.y_fine[0]
        self.last_action = np.array([0, 0], dtype=np.float32)  # Initialize last_action
        self.current_action = np.array([0, 0], dtype=np.float32)  # Initialize current_action
        self.distance_to_left_boundary, self.distance_to_right_boundary = self.calculate_distances_to_boundaries()
        
        # Start facing the first waypoint
        first_waypoint = np.array([self.x_fine[1], self.y_fine[1]])
        car_to_waypoint = first_waypoint - np.array([self.car_x, self.car_y])
        self.car_angle = np.degrees(np.arctan2(car_to_waypoint[1], car_to_waypoint[0])) % 360

        self.total_distance = 0
        self.previous_waypoint_index = 0
        self.prev_position = [self.car_x, self.car_y]

        self.lap_start_time = self.get_game_time()
        self.lap_time = 0
        self.game_time = 0
        self.lap_count = 0
        self.checkpoint_index = 0
        self.terminated = False

        self.prev_car_angle = self.car_angle
        self.angular_velocity = 0

        # Initialize the spatial grid for fast boundary lookup
        self.init_spatial_grid()

        self.observation = self.get_observation()
        return self.observation, {}
    
    def init_spatial_grid(self, grid_size=1):
        """Initialize spatial grid for boundary segments."""
        self.grid_size = grid_size
        self.spatial_grid = {}
        self.boundary_segments = []

        # Store boundary segments
        for i in range(len(self.left_boundary_x) - 1):
            self.boundary_segments.append(
                ((self.left_boundary_x[i], self.left_boundary_y[i]), (self.left_boundary_x[i+1], self.left_boundary_y[i+1]))
            )
        for i in range(len(self.right_boundary_x) - 1):
            self.boundary_segments.append(
                ((self.right_boundary_x[i], self.right_boundary_y[i]), (self.right_boundary_x[i+1], self.right_boundary_y[i+1]))
            )

        # Populate spatial grid
        for segment in self.boundary_segments:
            min_x = min(segment[0][0], segment[1][0])
            max_x = max(segment[0][0], segment[1][0])
            min_y = min(segment[0][1], segment[1][1])
            max_y = max(segment[0][1], segment[1][1])
            
            for x in range(int(min_x // grid_size), int(max_x // grid_size) + 1):
                for y in range(int(min_y // grid_size), int(max_y // grid_size) + 1):
                    if (x, y) not in self.spatial_grid:
                        self.spatial_grid[(x, y)] = []
                    self.spatial_grid[(x, y)].append(segment)
        
    def get_spacial_grid(self):
        return self.spatial_grid

    def step(self, action):
        self.current_action = action
        steering, velocity = action
        self.car_velocity = np.clip(self.car_velocity + velocity, MIN_VELOCITY, MAX_VELOCITY)
        self.car_angle = (self.car_angle + steering * 20) % 360


        self.angular_velocity = (self.car_angle - self.prev_car_angle) / self.get_game_time() if self.get_game_time() > 0 else 0
        self.prev_car_angle = self.car_angle

        # Apply friction to the car's velocity
        if self.car_velocity > 0:
            self.car_velocity = max(0, self.car_velocity - FRICTION)
        elif self.car_velocity < 0:
            self.car_velocity = min(0, self.car_velocity + FRICTION)

        # Update the car's position based on its velocity and angle
        self.car_x += self.car_velocity * np.cos(np.radians(self.car_angle))
        self.car_y += self.car_velocity * np.sin(np.radians(self.car_angle))

        current_position = np.array([self.car_x, self.car_y])
        self.update_absolute_distance()
        self.prev_position = [self.car_x, self.car_y]  # Update previous position for next step

        self.observation = self.get_observation()
        self.reward = self.calculate_reward()
        terminated = self.lap_count == 3  # End the episode after 3 laps
        truncated = not self.check_on_track()
        # done = terminated or truncated
        info = {}

        # Check if the car has completed a lap
        if self.check_crossed_start_line() and self.award_lap_time():
            print(f"Lap {self.lap_count} completed in {self.lap_time:.2f} seconds.")
            lap_time_reward = 1000 / max(self.lap_time, 1e-4)  # Large reward for completing a lap quickly
            self.reward += lap_time_reward
            print(f"Lap time reward: {lap_time_reward:.2f}")

            self.total_distance = 0  # Reset the distance traveled
            self.previous_waypoint_index = 0

        self.render(mode=self.render_mode)
        return self.observation, self.reward, terminated, truncated, info

    def display_info(self, font, screen, text_items):
        for i, (label, value) in enumerate(text_items):
            info_text = f"{label}: {value:.2f}"
            text = font.render(info_text, True, (255, 255, 255))
            screen.blit(text, (10, 10 + i * 20))

    def render(self, mode='human'):
        if mode == 'human':
            pygame.display.set_caption("Racetrack Environment")
            font = pygame.font.SysFont(None, 24)
            zoom_factor = 2.5

            self.screen.fill((0, 0, 0))

            offset_x = SCREEN_WIDTH // 2 - self.car_x * zoom_factor
            offset_y = SCREEN_HEIGHT // 2 - self.car_y * zoom_factor

            left_boundary_points = [(x * zoom_factor + offset_x, y * zoom_factor + offset_y) for x, y in zip(self.left_boundary_x, self.left_boundary_y)]
            right_boundary_points = [(x * zoom_factor + offset_x, y * zoom_factor + offset_y) for x, y in zip(self.right_boundary_x, self.right_boundary_y)]

            # Draw the road as a filled polygon
            road_points = left_boundary_points + right_boundary_points[::-1]
            pygame.draw.polygon(self.screen, (128, 128, 128), road_points)

            # Draw the track boundaries
            pygame.draw.lines(self.screen, (0, 0, 255), False, left_boundary_points, 2)
            pygame.draw.lines(self.screen, (0, 0, 255), False, right_boundary_points, 2)

            # Draw the start/end line
            start_line = [
                (self.left_boundary_x[0] * zoom_factor + offset_x, self.left_boundary_y[0] * zoom_factor + offset_y),
                (self.right_boundary_x[0] * zoom_factor + offset_x, self.right_boundary_y[0] * zoom_factor + offset_y)
            ]
            pygame.draw.line(self.screen, (255, 0, 0), start_line[0], start_line[1], 4)

            # Draw car
            rotated_car = pygame.transform.rotate(self.car, -self.car_angle)
            car_rect = rotated_car.get_rect(center=(self.car_x * zoom_factor + offset_x, self.car_y * zoom_factor + offset_y))
            self.screen.blit(rotated_car, car_rect)

             # Draw waypoints
            waypoints = self.get_waypoints(num_waypoints=10)
            for wp in waypoints:
                wp_x, wp_y = wp
                pygame.draw.circle(self.screen, (0, 255, 0), (int(wp_x * zoom_factor + offset_x), int(wp_y * zoom_factor + offset_y)), 5)

            # Draw LiDAR beams
            lidar_distances, lidar_coords = self.lidar_scan(self.car_x, self.car_y, self.car_angle)
            for end_point in lidar_coords:
                pygame.draw.line(self.screen, (255, 0, 0), (self.car_x * zoom_factor + offset_x, self.car_y * zoom_factor + offset_y),
                                 (end_point[0] * zoom_factor + offset_x, end_point[1] * zoom_factor + offset_y), 1)

            # Display car's speed
            output_text = [
                ("Speed", self.car_velocity),
                ("Heading", self.car_angle),
                ("Laps", self.lap_count),
                ("Lap Time", self.lap_time),
                ("Time", self.game_time),
                ("Current lap time", self.lap_time),
                ("Distance traveled", self.distance_traveled()),
                ("Left-most lidar", lidar_distances[0]),
                ("Right-most lidar", lidar_distances[-1]),
                ("Angular velocity", self.angular_velocity),
                ("Waypoint Curvature", self.calculate_curvature(waypoints)[0] if self.calculate_curvature(waypoints) else 0)
            ]

            self.display_info(font, self.screen, output_text)
         

            pygame.display.flip()
            self.clock.tick(90)
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    quit()
        

    def lidar_scan(self, car_x, car_y, car_angle):
        beam_length = lidar_max
        lidar_distances = np.full(num_lidar_readings, np.inf)
        lidar_coords = []

        # Define the angular spread for the LiDAR in front of the car (e.g., 120 degrees spread)
        angular_spread = 120
        start_angle = -angular_spread / 2
        end_angle = angular_spread / 2

        for i in range(num_lidar_readings):
            angle = start_angle + i * (end_angle - start_angle) / (num_lidar_readings - 1)
            beam_angle = np.radians((car_angle + angle) % 360)
            dx = np.cos(beam_angle)
            dy = np.sin(beam_angle)
            beam_end = np.array([car_x + beam_length * dx, car_y + beam_length * dy])

            min_distance = beam_length

            # Get the spatial grid cells to check for intersections
            start_cell = (int(car_x // self.grid_size), int(car_y // self.grid_size))
            end_cell = (int(beam_end[0] // self.grid_size), int(beam_end[1] // self.grid_size))
            cells_to_check = self.get_cells_to_check(start_cell, end_cell)

            # Check for intersections with track boundaries
            for cell in cells_to_check:
                if cell in self.spatial_grid:
                    for segment in self.spatial_grid[cell]:
                        intersection = self.ray_intersects_segment([car_x, car_y], beam_end, segment)
                        if intersection is not None:
                            distance = np.linalg.norm(intersection - np.array([car_x, car_y]))
                            if distance < min_distance:
                                min_distance = distance
                                beam_end = intersection

            lidar_distances[i] = min_distance
            lidar_coords.append(beam_end)

        # Check if lidar breams not within the track, and if not, set them to 0
        for i, distance in enumerate(lidar_distances):
            if distance == beam_length:
                lidar_distances[i] = 0
        
        return lidar_distances, lidar_coords

    def get_cells_to_check(self, start_cell, end_cell):
        """Bresenham's line algorithm to get cells through which the beam passes."""
        x0, y0 = start_cell
        x1, y1 = end_cell

        cells = []
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        while True:
            cells.append((x0, y0))
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

        return cells

    def ray_intersects_segment(self, ray_origin, ray_end, segment):
        p, r = np.array(ray_origin), np.array(ray_end) - np.array(ray_origin)
        q, s = np.array(segment[0]), np.array(segment[1]) - np.array(segment[0])

        r_cross_s = np.cross(r, s)
        if r_cross_s == 0:
            return None  # Parallel lines

        t = np.cross(q - p, s) / r_cross_s
        u = np.cross(q - p, r) / r_cross_s

        if 0 <= t <= 1 and 0 <= u <= 1:
            return p + t * r  # Intersection point

        return None
    
    def get_observation(self):
        waypoints = self.get_waypoints()
        self.distance_to_left_boundary, self.distance_to_right_boundary = self.calculate_distances_to_boundaries()
        distance_from_center = self.track_width / 2 - min(self.distance_to_left_boundary, self.distance_to_right_boundary)
        distance_traveled = self.total_distance
        self.lap_time = self.get_game_time() - self.lap_start_time
        lidar_readings, _ = self.lidar_scan(self.car_x, self.car_y, self.car_angle)  # Get LiDAR readings

        # Calculate curvature for the next few waypoints
        curvatures = self.calculate_curvature(waypoints)  # Adjust the number of waypoints considered for curvature
        curvature = curvatures[0] if curvatures else 0  # Use the first curvature value or 0 if not available

        return np.array([
            self.car_velocity, 
            self.angular_velocity,
            distance_traveled,
            distance_from_center, 
            self.lap_time,
            curvature,
            *lidar_readings
        ], dtype=np.float32)


    def check_on_track(self):
            track_center = np.vstack((self.x_fine, self.y_fine)).T
            car_position = np.array([self.car_x, self.car_y])
            distances = np.linalg.norm(track_center - car_position, axis=1)
            min_distance = np.min(distances)
            return min_distance <= self.track_width / 2

    def update_absolute_distance(self):
        """Update the absolute distance traveled based on waypoints."""
        current_position = np.array([self.car_x, self.car_y])
        distances = np.hypot(self.x_fine - current_position[0], self.y_fine - current_position[1])
        nearest_waypoint_index = np.argmin(distances)
        
        # Ensure the car is moving forward by checking waypoint index progression
        if nearest_waypoint_index > self.previous_waypoint_index:
            self.total_distance += np.linalg.norm(
                np.array([self.x_fine[nearest_waypoint_index], self.y_fine[nearest_waypoint_index]]) - 
                np.array([self.x_fine[self.previous_waypoint_index], self.y_fine[self.previous_waypoint_index]])
            )
            self.previous_waypoint_index = nearest_waypoint_index

    def calculate_reward(self):
        # Penalize being off-track
        if not self.check_on_track():
            return -100  # Large negative reward for going off track

        # Progress reward
        progress_reward = self.total_distance - self.previous_waypoint_index
        # Check if the car is moving forward, and reward it 1 point at each waypoint
        # progress_reward = 1 if self.total_distance > self.previous_waypoint_index else 0

        # make sure progress reward is positive
        if progress_reward < 0:
            progress_reward = 0

        # Centerline reward
        distance_from_center = abs(self.track_width / 2 - min(self.distance_to_left_boundary, self.distance_to_right_boundary))
        centerline_penalty = distance_from_center / (self.track_width / 2)  # Normalize to 0-1

        # Speed reward
        speed_reward = self.car_velocity / MAX_VELOCITY  # Normalize to 0-1

        # Smoothness penalty (for excessive steering and velocity changes)
        steering_penalty = abs(self.current_action[0] - self.last_action[0])
        acceleration_penalty = abs(self.current_action[1] - self.last_action[1])
        smoothness_penalty = (steering_penalty + acceleration_penalty) / 2

        # Lap completion reward
        lap_completion_reward = 0
        if self.check_crossed_start_line() and self.award_lap_time():
            lap_completion_reward = 1000 / max(self.lap_time, 1e-4)  # Large reward for quick lap completion

        no_movement_penalty = -10 if abs(self.car_velocity) < 0.1 else 0  # Apply penalty if the car's velocity is very low


        if (self.render_mode == 'human'):
            # Print rewards and penalties
            print(f"Progress reward: {progress_reward:.2f}")
            print(f"Centerline penalty: {centerline_penalty:.2f}")
            print(f"Speed reward: {speed_reward:.2f}")
            print(f"Smoothness penalty: {smoothness_penalty:.2f}")
            print(f"Lap completion reward: {lap_completion_reward:.2f}")
            print(f"No movement penalty: {no_movement_penalty:.2f}")

        # Aggregate reward
        reward = (progress_reward * 0.025 +
                speed_reward * 0.3 -
                centerline_penalty * 0.2 -
                smoothness_penalty * 0.1 +
                lap_completion_reward +
                no_movement_penalty)

        return reward

    def check_crossed_start_line(self):
        """Check if the car has crossed the start line."""
        current_position = np.array([self.car_x, self.car_y])
        start_position = np.array([self.x_fine[0], self.y_fine[0]])
        start_distance = np.linalg.norm(current_position - start_position)
        
        if start_distance < 10:
            return True
        
        return False

    def award_lap_time(self):
        self.game_time = self.get_game_time()
        current_lap_time = self.game_time - self.lap_start_time
        if (self.lap_count == 0 and current_lap_time > 10) or (self.lap_count > 0 and (current_lap_time > 20)):
            self.lap_count += 1
            self.lap_time = self.game_time - self.lap_start_time
            self.lap_start_time = self.game_time
            return True
        return False
    
    def get_game_time(self):
        """Get current game time in seconds."""
        return pygame.time.get_ticks() / 1000  # Convert milliseconds to seconds

    def get_waypoints(self, num_waypoints=10, closeness=3):
        waypoints = []
        car_index = np.argmin((np.array(self.x_fine) - self.car_x) ** 2 + (np.array(self.y_fine) - self.car_y) ** 2)
        for i in range(1, num_waypoints + 1):
            wp_index = (car_index + i * closeness) % len(self.x_fine)
            waypoints.append((self.x_fine[wp_index], self.y_fine[wp_index]))
        return waypoints

    def calculate_curvature(self, waypoints):
        curvatures = []
        for i in range(1, len(waypoints) - 1):
            p1, p2, p3 = waypoints[i - 1], waypoints[i], waypoints[i + 1]
            v1 = np.array(p2) - np.array(p1)
            v2 = np.array(p3) - np.array(p2)
            angle = np.degrees(np.arccos(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))))

            # Calculate the cross product to determine the sign of the angle
            cross_product = np.cross(v1, v2)
            if cross_product < 0:
                angle = -angle
            
            curvature = angle / np.linalg.norm(v2)
            curvatures.append(curvature)
        return curvatures


    def calculate_distances_to_boundaries(self):
        # Calculate the distances from the car to the left and right boundaries
        car_position = np.array([self.car_x, self.car_y])
        left_boundary_distances = np.linalg.norm(np.vstack((self.left_boundary_x, self.left_boundary_y)).T - car_position, axis=1)
        right_boundary_distances = np.linalg.norm(np.vstack((self.right_boundary_x, self.right_boundary_y)).T - car_position, axis=1)
        distance_to_left_boundary = np.min(left_boundary_distances)
        distance_to_right_boundary = np.min(right_boundary_distances)
        return distance_to_left_boundary, distance_to_right_boundary

    def distance_traveled(self):
        return self.total_distance
