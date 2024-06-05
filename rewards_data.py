

from Constants import *

class Rewards_data():
    def __init__(self, obs, tim, num_rewards):
        self.obs = obs
        self.tim = tim
        self.num_rewards = num_rewards
        self.rewards = [0] * num_rewards
        self.reward_val = 0
    def get_reward(self):
        [delta, v, wz, s, ey, ephi] = self.obs.data
        self.rewards = [0.3*s, 0.05*v, -1*abs(ey), -9*abs(ephi)]
        # 0.005*self.tim.get_time_elapsed("game")
        

        self.reward_val = sum(self.rewards)
        return self.reward_val

    def collision_reward(self):
        penalty = 90
        self.reward_val = -penalty
        return self.reward_val
    def reset(self):
        self.rewards = [0] * self.num_rewards
        self.reward_val = 0
    