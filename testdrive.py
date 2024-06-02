from env import *
import pygame

if __name__ == "__main__":
    env = CarEnv()
    env.reset()
    done = False

    while not done:
        action = env.action_space.sample()
        state, reward, done, info = env.step(action)
        env.render()
        pygame.time.wait(10)

    env.close()