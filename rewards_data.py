

# from Constants import *

# # Rewards Data
# # keeps track of different rewards and their weighted values

# class Rewards_data():
#     def __init__(self, obs, car, tim, num_rewards):
#         self.obs = obs
#         self.car = car
#         self.tim = tim
#         self.num_rewards = num_rewards
#         self.rewards = [0] * num_rewards
#         self.reward_val = 0
#     def get_reward(self):
#         self.rewards = [0.3*self.obs.s,
#                         10*self.car.v,
#                         -1*abs(self.obs.ey),
#                         -9*abs(self.obs.ephi)]
#         # 0.005*self.tim.get_time_elapsed("game")
        
#         self.reward_val = sum(self.rewards)
#         return self.reward_val

#     def collision_reward(self):
#         penalty = 90
#         self.reward_val = -penalty
#         return self.reward_val
#     def reset(self):
#         self.rewards = [0] * self.num_rewards
#         self.reward_val = 0
    