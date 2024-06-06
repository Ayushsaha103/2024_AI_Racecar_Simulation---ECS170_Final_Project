
from shapely.geometry import Point
from shapely.geometry.polygon import LineString
from shapely.geometry import Polygon
from math_helpers import distance
import numpy as np
import random

# Training dojo
# systems to constrain the car's motion and actions

class Training_dojo():
    def __init__(self, rd, wp, car, obs, tim):
        self.rd = rd
        self.wp = wp
        self.car = car
        self.obs = obs
        self.tim = tim
        self.vset = 0.5
        self.carminv = 0.3; self.carmaxv = 1.04
    def vary_speed(self):
        # every 12 sec, vary the speed
        if int(self.tim.get_time_elapsed("game")) % 12 == 0:
            vset_update = 0.16
            vset_update *= (random.randint(0,1) * 2 - 1)
            if self.vset + vset_update < self.carminv or self.vset + vset_update > self.carmaxv:
                vset_update *= (-1)
            self.vset = np.clip(self.vset+vset_update, self.carminv, self.carmaxv)
        return self.vset
    
    def check_car_overlies_wp(self):
        car_box = Polygon(self.car.bounding_box)
        # import pdb; pdb.set_trace()
        target_line = LineString((
            self.rd.left_boundary_points[self.wp.closest_pt],
            self.rd.right_boundary_points[self.wp.closest_pt] ))
    
        return target_line.intersects(car_box)
    def reset(self):
        pass
    def reward(self):
        reward = 0
        car_pos = (self.car.x, self.car.y)
        n = len(self.rd.track_points)
        wpcoor = self.rd.track_points[(self.wp.first_target_pt)%n]
        # reward += (1/600)*self.wp.rd_dist_traversed
        reward += (1/60)
        # reward += -abs(self.obs.ephi) - (1/20)*self.obs.ey
        reward -= (distance(car_pos, wpcoor) * 1/90)
        
        # check if waypoints updated
        # crossed_wp_coor = self.rd.track_points[self.wp.closest_pt-1]
        if self.wp.just_updated:    # and distance(car_pos, crossed_wp_coor) < 6:
            # print("wp update")
            reward += 9.0

        return reward
    def collision_reward(self):
        return -200
    
    def terminate(self):
        # car is heading in wrong dir.
        # self.obs.s_update < 0
        # import pdb; pdb.set_trace()
    
        # car is too far from rd center
        if abs(self.obs.ey) > 7:
            return True

        # car is facing > 15deg from road yaw
        if abs(self.obs.ephi) > (26)*np.pi/180:
            return True

        # # return True if car insuccessfully collides w/ wp
        # # AKA if car is too far from upcoming middle lane waypoint (when crossing it)
        # wpcoor = self.rd.track_points[self.wp.closest_pt-1]
        # if self.wp.just_updated and distance((self.car.x, self.car.y), wpcoor) > 10:
        #     return True

    
        