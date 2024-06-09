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
                "avg_ey",
                "avg_ephi",
                "avg_v",
                "episode_time",
                "progress",
            ]
        )
        self.episode_rewards = []
        self.current_rewards = []
        self.current_eys = []
        self.current_ephis = []
        self.current_vs = []
        self.current_s = 0

    def _on_step(self) -> bool:
        self.current_rewards.append(self.training_env.get_attr("reward")[0])

        obs = self.training_env.get_attr("obs")[0]
        self.current_ephis.append(obs.ephi)
        self.current_eys.append(obs.ey)
        self.current_s += obs.s

        car = self.training_env.get_attr("car")[0]
        self.current_vs.append(car.v)

        if self.locals.get("done"):
            self.episode_rewards.append(np.mean(self.current_rewards))
            self.current_rewards = []

            avg_ephi = np.mean(self.current_ephis)
            self.current_ephis = []

            avg_ey = np.mean(self.current_eys)
            self.current_eys = []

            avg_v = np.mean(self.current_vs)
            self.current_vs = []

            tim = self.training_env.get_attr("tim")[0]
            game_time = tim.get_time_elapsed("game")

            progress = self.current_s
            self.current_s = 0

            new_row = pd.DataFrame(
                [
                    {
                        "episode": len(self.episode_rewards),
                        "avg_reward": self.episode_rewards[-1],
                        "avg_ephi": avg_ephi,
                        "avg_ey": avg_ey,
                        "avg_v": avg_v,
                        "episode_time": game_time,
                        "progress": progress,
                    }
                ]
            )
            self.data = pd.concat([self.data, new_row], ignore_index=True)

        return True

    def get_data(self):
        return self.data

    def save(self, filename, index=False):
        self.data.to_csv(filename, index=index)
