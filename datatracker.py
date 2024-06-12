from stable_baselines3.common.callbacks import BaseCallback
import pandas as pd
import numpy as np

class DataTracker(BaseCallback):
    def __init__(self, verbose=0, log_frequency=100):
        super(DataTracker, self).__init__(verbose)
        self.log_frequency=log_frequency
        self.data = pd.DataFrame(
            columns=[
                "episode",
                "avg_reward",
                "avg_v",
                "episode_time",
                "distance_traveled",
                "avg_distance_to_left_boundary",
                "avg_distance_to_right_boundary",
                "lidar_readings",
                "shakiness"
            ]
        )
        self.episode_rewards = []
        self.current_rewards = []
        self.current_vs = []
        self.current_angles = []
        self.current_dist_traveled = 0
        self.current_distance_to_left_boundary = []
        self.current_distance_to_right_boundary = []
        self.current_lidar_readings = []
        self.current_angular_velocity = []
        self.previous_angle = None
    def _on_step(self) -> bool:
        self.current_rewards.append(self.training_env.get_attr("reward")[0])

        obs = self.training_env.get_attr("observation")[0]

        car_velocity = obs[0]
        distance_traveled = obs[1]
        distance_from_center = obs[2]
        current_lap_time = obs[3]
        curvature = obs[4]
        lidar_readings = obs[5:]

        # Assuming you have methods to get these values from your environment
        car_angle = self.training_env.get_attr("car_angle")[0]
        distance_to_left_boundary = self.training_env.get_attr("distance_to_left_boundary")[0]
        distance_to_right_boundary = self.training_env.get_attr("distance_to_right_boundary")[0]

        # Calculate angular velocity
        if self.previous_angle is not None:
            angular_velocity = car_angle - self.previous_angle
            self.current_angular_velocity.append(angular_velocity)
        self.previous_angle = car_angle

        if distance_traveled != 0:
            self.current_dist_traveled = distance_traveled

        self.current_vs.append(car_velocity)
        self.current_distance_to_left_boundary.append(distance_to_left_boundary)
        self.current_distance_to_right_boundary.append(distance_to_right_boundary)
        self.current_lidar_readings.append(lidar_readings)

        if self.locals.get("done"):
            self.episode_rewards.append(np.mean(self.current_rewards))
            self.current_rewards = []

            avg_v = np.mean(self.current_vs)
            self.current_vs = []

            avg_distance_to_left_boundary = np.mean(self.current_distance_to_left_boundary)
            self.current_distance_to_left_boundary = []

            avg_distance_to_right_boundary = np.mean(self.current_distance_to_right_boundary)
            self.current_distance_to_right_boundary = []

            avg_lidar_readings = np.mean(self.current_lidar_readings, axis=0)
            self.current_lidar_readings = []

            game_time = self.training_env.get_attr("game_time")[0]

            dist_traveled = self.current_dist_traveled
            self.current_dist_traveled = 0

            shakiness = np.std(self.current_angular_velocity)
            self.current_angular_velocity = []

            new_row = pd.DataFrame(
                [
                    {
                        "episode": len(self.episode_rewards),
                        "avg_reward": self.episode_rewards[-1],
                        "avg_v": avg_v,
                        "episode_time": game_time,
                        "distance_traveled": dist_traveled,
                        "avg_distance_to_left_boundary": avg_distance_to_left_boundary,
                        "avg_distance_to_right_boundary": avg_distance_to_right_boundary,
                        "lidar_readings": avg_lidar_readings,
                        "shakiness": shakiness
                    }
                ]
            )
            self.data = pd.concat([self.data, new_row], ignore_index=True)

        return True

    def get_data(self):
        return self.data

    def save(self, filename, index=False):
        self.data.to_csv(filename, index=index)
