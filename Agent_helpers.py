


import math
import numpy as np


################################################################################################
# Helper funcs
################################################################################################

# normalize an angle to [-pi, pi]
def normalize_angle(angle):
    """
    Normalize an angle to [-pi, pi].
    :param angle: (float)
    :return: (float) Angle in radian in [-pi, pi]
    """
    while angle > np.pi:
        angle -= 2.0 * np.pi

    while angle < -np.pi:
        angle += 2.0 * np.pi

    return angle

def convert_to_speed_vector(v, yaw_rad):
    #yaw_rad = math.radians(yaw)
    x_speed = v * math.cos(yaw_rad)
    y_speed = v * math.sin(yaw_rad)
    
    return x_speed, y_speed

def estimate_average_dxdt(angle_values):
    if len(angle_values) < 2: return 0

    # Calculate the change in angle over time
    d_angle_dt = np.diff(angle_values)
    
    # Check if angle wraps around from 2pi to 0
    for i in range(len(d_angle_dt)):
        if d_angle_dt[i] > np.pi:
            d_angle_dt[i] -= 2*np.pi
        elif d_angle_dt[i] < -np.pi:
            d_angle_dt[i] += 2*np.pi
    
    # Calculate the average value of d_angle/dt
    avg_d_angle_dt = np.mean(d_angle_dt)
    
    return avg_d_angle_dt

# PID controller
class PID:
    # init. PID controller
    def __init__(obj, kp, ki, kd, length=6):    # length = time length of integral
      obj.errors = [0] * length;
      obj.integ = 0; obj.kp = kp; obj.ki = ki; obj.kd = kd;
      obj.dt = 0

    # internal function: update PID error values
    def update_ers(obj, er):
      obj.integ += obj.dt * (er - obj.errors[0]);
      obj.errors = obj.errors[2:len(obj.errors)];
      obj.errors += [er];

    # PID controller pushes v to be closer to v_exp
    def push(obj, val, val_exp):
        er = val_exp - val;
        obj.update_ers(er);
        Fo = obj.kp * er + \
              obj.ki * obj.integ + \
              obj.kd * (er - obj.errors[len(obj.errors)-2]);
        if Fo > 1:
            Fo = 1;
        elif Fo < -1:
            Fo = -1;
        return Fo

    # reset internal state of PID controller
    def reset(obj):
        obj.integ = 0; obj.errors = [0] * len(obj.errors);

    # set k constants of PID controller
    def set_ks(obj, kp, ki, kd):
        obj.kp = kp; obj.ki = ki; obj.kd = kd