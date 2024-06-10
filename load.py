import gym
import numpy as np
from stable_baselines3 import PPO, A2C
from stable_baselines3.common.env_util import make_vec_env
from racetractEnv import RacetrackEnv  # Ensure your environment file is named racetrack_env.py
from stable_baselines3.common.env_checker import check_env

def main():
    env = make_vec_env(lambda: RacetrackEnv(render_mode='human'), n_envs=1)
    # Optionally, load and test the trained model
    model = PPO.load("models/PPO_racetrack_3")
    obs = env.reset()
    while True:
        action, _states = model.predict(obs, deterministic=True)
        obs, rewards, dones, info = env.step(action)
        env.render()
        if np.any(dones):
            obs = env.reset()

if __name__ == "__main__":
    main()
