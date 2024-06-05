import numpy as np
from math_helpers import *

class Obs_data():
    def __init__(self, rd, wp, car, obs_size):
        self.rd = rd
        self.wp = wp
        self.car = car

        self.obs_size = obs_size
        self.data = np.array([0]*obs_size)
        self.prev_closest_track_coor = self.rd.track_points[0]
        self.s = 0
    
    def get_state(self):
        # get the 3 nearest track points to the car
        n = len(self.rd.track_points)
        wp_coors = [ self.rd.track_points[(self.wp.closest_pt-1) % n],
                    self.rd.track_points[(self.wp.closest_pt) % n],
                    self.rd.track_points[(self.wp.closest_pt + 1) % n] ]
        car_pos = (self.car.x, self.car.y)

        # get ey, ephi to the NEAREST COORDINATE within track
        ey, nearest_wps, closest_track_coor = find_ey(car_pos, wp_coors)    # TODO: checkme
        (wp1_x, wp1_y), (wp2_x, wp2_y) = nearest_wps
        wp_yaw = np.arctan2(wp2_y - wp1_y, wp2_x - wp1_x)
        ephi = find_ephi(wp_yaw, self.car.yaw)              # TODO: checkme - logically
    
        # calculate s
        car_motion = [self.prev_closest_track_coor, closest_track_coor]
        track_direction = nearest_wps

        s_update = distance(closest_track_coor, self.prev_closest_track_coor)
        if not is_vect_facing_along(car_motion, track_direction):
            s_update *= (-1)
        self.s += s_update

        # # accumulate self.data
        self.data = np.array([self.car.delta, self.car.v, self.car.wz, self.s, ey, ephi]).astype(np.float16)
        # self.data[1] = self.car.v
        # self.data[3] = self.car.wz

        self.prev_closest_track_coor = closest_track_coor
        return self.data



    def reset(self):
        self.data = np.array([0]*self.obs_size)
        self.prev_closest_track_coor = self.rd.track_points[0]
        self.s = 0
        


