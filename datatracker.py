from stable_baselines3.common.callbacks import BaseCallback
import pandas as pd
import numpy as np


class DataTracker(BaseCallback):
    def __init__(self, verbose=0):
        super(DataTracker, self).__init__(verbose)
        self.data = pd.DataFrame(
            columns=[
                "episode",
                "avg_reward",
                "avg_v",
                "episode_time",
                "distance_traveled",
            ]
        )
        self.episode_rewards = []
        self.current_rewards = []
        self.current_vs = []
        self.current_dist_traveled = 0

    def _on_step(self) -> bool:
        self.current_rewards.append(self.training_env.get_attr("reward")[0])

        obs = self.training_env.get_attr("observation")[0]

        car_velocity = obs[0]
        distance_traveled = obs[1]
        distance_from_center = obs[2]
        current_lap_time = obs[3]
        curvature = obs[4]
        lidar_readings = obs[5:]

        if distance_traveled != 0:
            self.current_dist_traveled = distance_traveled

        self.current_vs.append(car_velocity)

        if self.locals.get("done"):
            self.episode_rewards.append(np.mean(self.current_rewards))
            self.current_rewards = []

            avg_v = np.mean(self.current_vs)
            self.current_vs = []

            game_time = self.training_env.get_attr("game_time")[0]

            dist_traveled = self.current_dist_traveled
            self.current_dist_traveled = 0

            new_row = pd.DataFrame(
                [
                    {
                        "episode": len(self.episode_rewards),
                        "avg_reward": self.episode_rewards[-1],
                        "avg_v": avg_v,
                        "episode_time": game_time,
                        "distance_traveled": dist_traveled,
                    }
                ]
            )
            self.data = pd.concat([self.data, new_row], ignore_index=True)

        return True

    def get_data(self):
        return self.data

    def save(self, filename, index=False):
        self.data.to_csv(filename, index=index)
