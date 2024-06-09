
from math_helpers import save_data
import time
import Constants


class Data_Logger():
    def __init__(self, env):
        self.env = env
        self.nsec_btwn_data_records = 3
        self.all_data = []
    # record data every 2 sec
    def log_incremental_data(self):
        t = time.time()
        if t > self.data_timer + self.nsec_btwn_data_records:
            # reset timer
            self.data_timer = t

            # record data
            ey = self.env.obs.ey
            ephi = self.env.obs.ephi
            rw = self.env.reward
            s = self.env.obs.s
            v = self.env.car.v
            wp_updates = self.env.wp.num_updates_in_game
            time_passed = self.env.tim.get_time_elapsed("lap")
            self.game_data.append([ey, ephi, v, rw, s, wp_updates, time_passed])

    # reset at the end of every game
    def reset(self):
        try:
            assert(len(self.game_data) > 0)
            mat = list(zip(*self.game_data))
            colmaxes = [max(column) for column in mat[4:]]
            # sum_in_columns = [sum(column) for column in mat]
            colavs = [sum(column)/len(column) for column in mat[:4]]
            all_data_row = colavs + colmaxes
            self.all_data.append(all_data_row)
        except:
            self.game_data = []
        self.data_timer = time.time()
    def finish(self):
        colnames = ["av_ey", "av_ephi", "av_v", "av_rw", "total_s", "total_wp_updates", "total_time"]
        fname = Constants.get_updated_Model_Save_Path("recorded_train_data.csv")
        # fname = fname.replace("./models/", "./data/")
        save_data(self.all_data, colnames, fname)

        if self.env.dojo.successful_lap_index != -1:
            fname = Constants.get_updated_Model_Save_Path("successful_lap_data.csv")
            # fname = fname.replace("./models/", "./data/")
            save_data(self.game_data, ["ey", "ephi", "v", "reward", "s", "wp_updates", "t"], fname)


