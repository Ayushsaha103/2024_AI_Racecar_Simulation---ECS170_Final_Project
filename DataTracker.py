from stable_baselines3.common.callbacks import BaseCallback
import pandas as pd
import numpy as np

class DataTracker(BaseCallback):
    def __init__(self, verbose=0):
        super(DataTracker, self).__init__(verbose)
        self.data = pd.DataFrame(columns=['episode', 'avg_reward'])
        self.episode_rewards = []
        self.current_rewards = []

    def _on_step(self) -> bool:
        self.current_rewards.append(self.training_env.get_attr('reward')[0])
        return True

    def _on_rollout_end(self) -> bool:
        self.episode_rewards.append(np.mean(self.current_rewards))
        self.current_rewards = []

        new_row = pd.DataFrame([{'episode': len(self.episode_rewards), 'avg_reward': self.episode_rewards[-1]}])
        self.data = pd.concat([self.data, new_row], ignore_index=True)
        
        return True

    def get_data(self):
        return self.data
    
    def save_data(self, filename, index=False):
        self.data.to_csv(filename, index=index)