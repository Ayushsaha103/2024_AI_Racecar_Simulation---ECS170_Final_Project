if __name__ == "__main__":
    env = RacetrackEnv()
    env.reset()
    done = False

    while not done:
        action = env.action_space.sample()
        state, reward, done, info = env.step(action)
        env.render()
        pygame.time.wait(100)

    env.close()