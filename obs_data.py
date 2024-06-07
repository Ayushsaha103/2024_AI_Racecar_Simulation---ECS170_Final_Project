import numpy as np
from math_helpers import *

class Obs_data():
    def __init__(self, rd, wp, car, obs_size):
        self.rd = rd
        self.wp = wp
        self.car = car

        self.obs_size = obs_size
        self.reset()

    def get_wpa_wpd(self, target_coor, car_pos):
        target_coor_yaw = np.arctan2(target_coor[1] - car_pos[1], target_coor[0]-car_pos[0])
        wpd = distance(target_coor, car_pos)
        wpa = find_ephi(target_coor_yaw, self.car.yaw)
        return wpd, wpa
    
    def get_state(self):
        # get the 3 nearest track points to the car
        n = len(self.rd.track_points)
        # import pdb; pdb.set_trace()
        wp_coors = [ self.rd.track_points[(self.wp.closest_pt-1) % n],
                    self.rd.track_points[(self.wp.closest_pt) % n],
                    self.rd.track_points[(self.wp.closest_pt + 1) % n] ]
        car_pos = (self.car.x, self.car.y)

        # get ey, ephi to the NEAREST COORDINATE within track
        self.ey, nearest_wps, closest_track_coor = find_ey(car_pos, wp_coors)    # TODO: checkme
        (wp1_x, wp1_y), (wp2_x, wp2_y) = nearest_wps
        track_yaw = np.arctan2(wp2_y - wp1_y, wp2_x - wp1_x)
        # import pdb; pdb.set_trace()
        self.ephi = find_ephi(track_yaw, self.car.yaw)              # TODO: checkme - logically

        # calculate s
        car_motion = [self.prev_closest_track_coor, closest_track_coor]
        track_direction = nearest_wps

        self.s_update = distance(closest_track_coor, self.prev_closest_track_coor)
        if abs_angle_btwn_vects(car_motion, track_direction) > np.pi/2:
            self.s_update *= (-1)
        self.s += self.s_update

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # # accumulate self.data

        # for i in range(self.wp.npts):
        #     m_coor = self.rd.track_points[(self.wp.closest_pt+i)%n]
        #     l_coor = self.rd.left_boundary_points[(self.wp.closest_pt+i)%n]
        #     r_coor = self.rd.right_boundary_points[(self.wp.closest_pt+i)%n]
            
        #     wpd0, wpa0 = self.get_wpa_wpd(m_coor, car_pos)
        #     # wpd1, wpa1 = self.get_wpa_wpd(l_coor, car_pos)
        #     # wpd2, wpa2 = self.get_wpa_wpd(r_coor, car_pos)
        #     # self.wpds[2*i] = wpd1
        #     # self.wpds[2*i+1] = wpd2
        #     # self.wpas[2*i] = wpa1
        #     # self.wpas[2*i+1] = wpa2
        #     self.wpas[i] = wpa0
        #     self.wpds[i] = wpd0
        
        # #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # # # accumulate self.data
        edelta = 0
        for i in range(self.wp.npts):
            target_coor = self.rd.track_points[(self.wp.first_target_pt+i)%n]
            target_coor_yaw = np.arctan2(target_coor[1] - car_pos[1], target_coor[0]-car_pos[0])
            wpd = distance(target_coor, car_pos)
            wpa = find_ephi(target_coor_yaw, self.car.yaw)
            self.wpas[i] = wpa
            self.wpds[i] = wpd
        
            if i == 0:
                edelta = find_ephi(target_coor_yaw, self.car.yaw+self.car.delta)

        self.data = np.array(
            # [self.car.delta, self.car.v, self.car.wz, self.s, self.ey, self.ephi]
            # [wpa, wpd, edelta, self.ey, self.ephi]
            # self.wpas + self.wpds + [edelta, self.ey, self.ephi]
            self.wpas + self.wpds + [edelta, self.car.v]
            ).astype(np.float16)
        # print(self.data)

        # #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # # # accumulate self.data
        
        # for i in range(self.wp.npts):

        #     target_coor = self.rd.track_points[(self.wp.closest_pt+i)%n]
        #     target_coor_yaw = np.arctan2(target_coor[1] - car_pos[1], target_coor[0]-car_pos[0])
        #     wpd = distance(target_coor, car_pos)
        #     wpa = find_ephi(target_coor_yaw, self.car.yaw)
        #     self.wpds[i] = wpd
        #     self.wpas[i] = wpa

        # edelta = find_ephi(track_yaw, self.car.yaw+self.car.delta)
        # self.data = np.array(
        #     # [self.car.delta, self.car.v, self.car.wz, self.s, self.ey, self.ephi]
        #     # [wpa, wpd, edelta, self.ey, self.ephi]
        #     self.wpas + self.wpds + [edelta, self.ey, self.ephi]
        #     ).astype(np.float16)
        
        # #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # # # accumulate self.data
        # target_coor = self.rd.track_points[(self.wp.closest_pt+2)%n]
        # target_coor_yaw = np.arctan2(target_coor[1] - car_pos[1], target_coor[0]-car_pos[0])
        # wpd = distance(target_coor, car_pos)
        # wpa = find_ephi(target_coor_yaw, self.car.yaw)

        # delta_ang_diff = find_ephi(track_yaw, self.car.yaw+self.car.delta)
        # self.data = np.array(
        #     # [self.car.delta, self.car.v, self.car.wz, self.s, self.ey, self.ephi]
        #     # [wpa, wpd, delta_ang_diff, self.ey, self.ephi]
        #     ).astype(np.float16)

        self.prev_closest_track_coor = closest_track_coor
        return self.data

    def reset(self):
        self.data = np.array([0]*self.obs_size)
        self.prev_closest_track_coor = self.rd.track_points[0]

        self.s = 0
        self.s_update = 0
        self.ey, self.ephi = 0,0
        self.wpds = [0]*self.wp.npts; self.wpas = [0]*self.wp.npts
        


