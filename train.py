import os
import gym
import numpy as np
from stable_baselines3 import PPO, DQN, A2C, SAC
from stable_baselines3.common.env_util import make_vec_env
from racetractEnv import RacetrackEnv  # Ensure your environment file is named racetrack_env.py
from stable_baselines3.common.env_checker import check_env
from datatracker import DataTracker
import torch.nn as nn

def get_latest_num(folder, prefix):
    """Get the latest number used for saved models or logs."""
    files = [f for f in os.listdir(folder) if f.startswith(prefix) and f.endswith('.zip')]
    if not files:
        return 0
    numbers = [int(f.split('_')[-1].replace('.zip', '')) for f in files]
    return max(numbers) + 1

def train(agent_policy, time_steps=100000, load_model=False, model_num=-1):
    models_folder = 'models'
    logs_folder = 'logs'
    metrics_folder = 'metrics'
    os.makedirs(models_folder, exist_ok=True)
    os.makedirs(logs_folder, exist_ok=True)
    os.makedirs(metrics_folder, exist_ok=True)

    num = get_latest_num(models_folder, f"{agent_policy.lower()}_racetrack_")

    env = make_vec_env(lambda: RacetrackEnv(render_mode='ai'), n_envs=1)
    datatracker = DataTracker()
    # check_env(env)

    if load_model:
        print("Loading model...")
        if agent_policy == 'PPO':
            model = PPO.load(f"models/{agent_policy.lower()}_racetrack_{model_num}.zip", env=env)
        elif agent_policy == 'A2C':
            model = A2C.load(f"models/{agent_policy.lower()}_racetrack_{model_num}.zip", env=env)
        elif agent_policy == 'SAC':
            model = SAC.load(f"models/{agent_policy.lower()}_racetrack_{model_num}.zip", env=env)
        else:
            raise ValueError("Invalid agent policy. Choose from 'A2C', 'PPO', or 'SAC'.")
    else:
        print("Training model...")
        if agent_policy == 'A2C':
            model = A2C('MlpPolicy', env, verbose=0, tensorboard_log=f"{logs_folder}/{agent_policy.lower()}_racetrack_{num}", learning_rate=0.0007, n_steps=10)
        elif agent_policy == 'PPO':
            #  n_steps = 10240
            model = PPO('MlpPolicy', env, verbose=0, tensorboard_log=f"{logs_folder}/{agent_policy.lower()}_racetrack_{num}", learning_rate=0.0001, batch_size=128)
        else:
            raise ValueError("Invalid agent policy. Choose from 'A2C', 'PPO', or 'SAC'.")

    try:
        # Train the model
        if agent_policy == 'PPO':
            model.learn(total_timesteps=time_steps, progress_bar=True, callback=datatracker)
        elif agent_policy == 'A2C':
            model.learn(total_timesteps=time_steps, progress_bar=True, callback=datatracker)
        elif agent_policy == 'SAC':
            model.learn(total_timesteps=time_steps, progress_bar=True, callback=datatracker)
    finally:
        # Save model in models folder
        model.save(f"{models_folder}/{agent_policy.lower()}_racetrack_{num}.zip")  # Save with appropriate name based on the agent policy
        datatracker.save(f"{metrics_folder}/{agent_policy.lower()}_racetrack_{num}.csv")  # Save the data tracker (optional)
        print("Model saved to:", f"{models_folder}/{agent_policy.lower()}_racetrack_{num}.zip")

if __name__ == "__main__":
    agent_policy = 'A2C'  # Change this to 'A2C', 'PPO', or 'SAC' as needed
    train(agent_policy, time_steps=100000, load_model=False, model_num=-1)
