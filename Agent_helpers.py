


import math
import numpy as np


################################################################################################
# agent
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

# check if yaw angle is pointing opposite to vector formed by pt1 & pt2
def is_yaw_opposite_to_vector(yaw_angle, point1, point2):
    # Calculate the vector formed by point1 and point2
    vector_p1p2 = np.array([point2[0] - point1[0], point2[1] - point1[1]])
    
    # Calculate the yaw vector
    yaw_vector = np.array([np.cos(yaw_angle), np.sin(yaw_angle)])
    
    # Calculate the dot product of the yaw vector and the vector formed by point1 and point2
    dot_product = np.dot(yaw_vector, vector_p1p2)
    
    # Check if the dot product is negative (angles pointing in opposite directions)
    if dot_product < 0:
        return True
    else:
        return False

