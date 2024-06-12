import gym
import numpy as np
from stable_baselines3 import PPO, A2C, SAC
from stable_baselines3.common.env_util import make_vec_env
from racetractEnv import RacetrackEnv  # Ensure your environment file is named racetrack_env.py
from stable_baselines3.common.env_checker import check_env
import os

def get_latest_num(folder, prefix):
    """Get the latest number used for saved models or logs."""
    files = [f for f in os.listdir(folder) if f.startswith(prefix) and f.endswith('.zip')]
    if not files:
        return 0
    numbers = [int(f.split('_')[-1].replace('.zip', '')) for f in files]
    return max(numbers)

def load_model(algo, num = -1):
    if num == -1:
        # load in the latest model
        num = get_latest_num('models', f"{algo.lower()}_racetrack_")

    env = make_vec_env(lambda: RacetrackEnv(render_mode='human'), n_envs=1)
    # Optionally, load and test the trained model
    if algo == 'PPO':
        model = PPO.load(f"models/{algo.lower()}_racetrack_{num}.zip", env=env)
    elif algo == 'A2C':
        model = A2C.load(f"models/{algo.lower()}_racetrack_{num}.zip", env=env)
    elif algo == 'SAC':
        model = SAC.load(f"models/{algo.lower()}_racetrack_{num}.zip", env=env)
    else:
        raise ValueError("Invalid agent policy. Choose from 'A2C', 'PPO', or 'SAC'.")
    
    obs = env.reset()

    print("Loaded model from:", f"models/{algo.lower()}_racetrack_{num}.zip")
    while True:
        action, _states = model.predict(obs, deterministic=True)
        obs, rewards, dones, info = env.step(action)
        env.render()
        if np.any(dones):
            obs = env.reset()

if __name__ == "__main__":
    load_model(algo='PPO', num=-1)
