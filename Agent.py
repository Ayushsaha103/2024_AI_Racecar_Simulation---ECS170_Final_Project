import pygame
import Constants
import os


import math
import numpy as np
from collections import deque
from Agent_helpers import *

# Screen
WIDTH, HEIGHT =  Constants.WIDTH, Constants.HEIGHT


# car constants
max_steer = np.radians(30.0)  # [rad] max steering angle
max_throttle = 16.0
max_v = 35.0

L = 7.9  # [m] Wheel base of vehicle
dt = 0.1
Lr = L / 2.0  # [m]
Lf = L - Lr
Cf = 1600.0 * 2.0  # N/rad
Cr = 1700.0 * 2.0  # N/rad
Iz = 2250.0  # kg/m2
m = 1500.0  # kg


################################################################################################
# Drone class
################################################################################################

#class Drone(pygame.sprite.Sprite):
#    def __init__(self):
#        pygame.sprite.Sprite.__init__(self)
#        self.pedals = PID(0.8,0.1,0.05, 6)
#        self.reset()
#    def reset(self, x=WIDTH / 2, y=HEIGHT / 2, yaw=math.pi/2, vx=0.01, vy=0, omega=0.0):
#        self.x = x
#        self.y = y
#        self.yaw = yaw
#        self.vx = vx
#        self.vy = vy
#        self.v = math.sqrt(self.vx**2 + self.vy**2)

#        self.omega = omega
#        # Aerodynamic and friction coefficients
#        self.c_a = 1.36
#        self.c_r1 = 0.01

        
#    def get_v(self):
#        return math.sqrt(self.vx**2 + self.vy **2)

#    def update(self, throttle, delta):
#        delta = np.clip(delta, -max_steer, max_steer)
#        throttle = np.clip(throttle, -max_throttle, max_throttle)
        
#        vmag = math.sqrt(self.vx**2 + self.vy**2)
#        if abs(vmag) > max_v:
#            self.vx = max_v * self.vx / vmag
#            self.vy = max_v * self.vy / vmag
#        if self.v < 2: throttle = 0.2

#        self.x = self.x + self.vx * math.cos(self.yaw) * dt - self.vy * math.sin(self.yaw) * dt
#        self.y = self.y + self.vx * math.sin(self.yaw) * dt + self.vy * math.cos(self.yaw) * dt
#        self.yaw = self.yaw + self.omega * dt
#        self.yaw = normalize_angle(self.yaw)
#        Ffy = -Cf * math.atan2(((self.vy + Lf * self.omega) / self.vx - delta), 1.0)
#        Fry = -Cr * math.atan2((self.vy - Lr * self.omega) / self.vx, 1.0)
#        R_x = self.c_r1 * self.vx
#        F_aero = self.c_a * self.vx ** 2
#        F_load = F_aero + R_x
#        self.vx = self.vx + (throttle - Ffy * math.sin(delta) / m - F_load/m + self.vy * self.omega) * dt
#        self.vy = self.vy + (Fry / m + Ffy * math.cos(delta) / m - self.vx * self.omega) * dt
#        vmag = math.sqrt(self.vx**2 + self.vy**2)
#        if abs(vmag) > max_v:
#            self.vx = max_v * self.vx / vmag
#            self.vy = max_v * self.vy / vmag

#        self.v = math.sqrt(self.vx**2 + self.vy**2)
#        self.omega = self.omega + (Ffy * Lf * math.cos(delta) - Fry * Lr) / Iz * dt

#        print([throttle, delta, self.v, self.yaw])
#        return throttle

#    def pidv(self,vset, delta):
#        throttle = 1*self.pedals.push(math.sqrt(self.vx**2 + self.vy **2),vset)
#        self.update(throttle,delta)




class Drone(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.pedals = PID(0.8,0.1,0.05, 6)
        self.reset()
        
    def reset(self, x=WIDTH / 2, y=HEIGHT / 2, yaw=math.pi/2, v=0.0):
    # Reset initial variables
        #(self.angle, self.angle_speed, self.angular_acceleration) = (0, 0, 0)
        (self.x_position, self.x_speed, self.x_acceleration) = (int(WIDTH/2) , 0, 0)
        (self.y_position, self.y_speed, self.y_acceleration) = (int(HEIGHT/2), 0, 0)

        self.x = x
        self.y = y
        self.x_position, self.y_position = self.x, self.y
        self.yaw = yaw
        self.v = v
        self.x_speed, self.y_speed = convert_to_speed_vector(self.v, self.yaw)

        self.dyaw_dt = 0.0
        self.prev_yaws = deque(); self.prev_yaws.appendleft(self.yaw)
        self.pedals.reset()

    def get_v(self):
        return self.v
    
    def pidv(self, vset, delta):
        throttle = 1*self.pedals.push(self.v,vset)
        self.update(throttle,delta)

    def update(self, throttle, delta):
        """
        Update the state of the vehicle.
        Stanley Control uses bicycle model.
        :param a: (float) Acceleration
        :param delta: (float) Steering
        """
        delta = np.clip(delta, -max_steer, max_steer)
        throttle = np.clip(throttle, -max_throttle, max_throttle)
        self.v = np.clip(self.v, 0, max_v)
        if self.v == 0: throttle = 0.2

        self.x += self.v * np.cos(self.yaw) * dt
        self.y += self.v * np.sin(self.yaw) * dt
        self.yaw += self.v / L * np.tan(delta) * dt
        self.yaw = normalize_angle(self.yaw)
        self.v += throttle * dt

        #print("velocity [m/s]: " + str(self.v))
        x_speed_orig, y_speed_orig = self.x_speed, self.y_speed
        self.x_position, self.y_position = self.x, self.y
        self.x_speed, self.y_speed = convert_to_speed_vector(self.v - ( throttle*dt), self.yaw)
        self.x_acceleration, self.y_acceleration = (self.x_speed - x_speed_orig) / dt, (self.y_speed - y_speed_orig)/dt
        
        self.prev_yaws.appendleft(self.yaw)
        if len(self.prev_yaws) > 2: self.prev_yaws.pop()
        self.dyaw_dt = estimate_average_dxdt(self.prev_yaws)

        print([throttle, delta, self.v])
        return throttle
    