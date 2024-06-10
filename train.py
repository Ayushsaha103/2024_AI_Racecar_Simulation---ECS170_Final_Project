import gym
import numpy as np
from stable_baselines3 import PPO, DQN, A2C, SAC
from stable_baselines3.common.env_util import make_vec_env
from racetractEnv import RacetrackEnv  # Ensure your environment file is named racetrack_env.py
from stable_baselines3.common.env_checker import check_env
from datatracker import DataTracker

def main(agent_policy, num):
    env = make_vec_env(lambda: RacetrackEnv(render_mode='ai'), n_envs=1)
    datatracker = DataTracker()
    # check_env(env)

    if agent_policy == 'A2C':
        model = A2C('MlpPolicy', env, verbose=0, ent_coef=0.01)
    elif agent_policy == 'PPO':
        model = PPO('MlpPolicy', env, verbose=0, tensorboard_log=f"logs/{agent_policy.lower()}_racetrack_{num}", batch_size=128)
    elif agent_policy == 'SAC':
        model = SAC('MlpPolicy', env, verbose=0)
    else:
        raise ValueError("Invalid agent policy. Choose from 'DQN', 'A2C', or 'PPO'.")

    try:
        # Train the model
        if agent_policy == 'PPO':
            model.learn(total_timesteps=300000, progress_bar=True, callback=datatracker)
        elif agent_policy == 'A2C':
            model.learn(total_timesteps=100000, progress_bar=True, callback=datatracker)
        elif agent_policy == 'SAC':
            model
    finally:
        # Save model in models folder
        model.save(f"models/{agent_policy.lower()}_racetrack_{num}")  # Save with appropriate name based on the agent policy
        datatracker.save(f"metrics/{agent_policy.lower()}_racetrack_{num}.csv")  # Save the data tracker (optional

if __name__ == "__main__":
    agent_policy = 'A2C'  # Change this to 'A2C' or 'PPO' as needed
    num = 2
    main(agent_policy, num)
