import time


class Timer:
    def __init__(self):
        self.tot_start_time = time.time()
        self.game_start_time = -1
        self.lap_start_time = -1

    def get_time_elapsed(self, time_type):
        if time_type == "total":
            return time.time() - self.tot_start_time
        elif time_type == "game":
            return time.time() - self.game_start_time
        elif time_type == "lap":
            return time.time() - self.lap_start_time

    def reset(self):
        self.reset_game()

    def reset_game(self):
        self.game_start_time = time.time()
        self.lap_start_time = time.time()

    def reset_lap(self):
        self.lap_start_time = time.time()
