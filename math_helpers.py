
import math
import numpy as np



############################################################################################################
# waypoints
############################################################################################################

# tell if given_point is to left or right of line segment formed by connecting pt1 -> pt2
def is_point_to_left_or_right(point1, point2, given_point):
    vector_p1p2 = (point2[0] - point1[0], point2[1] - point1[1])
    vector_p1_given = (given_point[0] - point1[0], given_point[1] - point1[1])
    cross_product = vector_p1p2[0] * vector_p1_given[1] - vector_p1p2[1] * vector_p1_given[0]
    if cross_product > 0:
        return 'left'
    elif cross_product < 0:
        return 'right'
    else:
        return 'on_line'

############################################################################################################
# obs_data
############################################################################################################

# return the closest point on the segment ab to the point p
def closest_point_on_segment(p, a, b):
    """Returns the closest point on the segment ab to the point p."""
    ap = p - a
    ab = b - a
    t = np.dot(ap, ab) / np.dot(ab, ab)
    t = np.clip(t, 0, 1)
    return a + t * ab

def find_ey(car_pos, xy_pairs):
    car_pos = np.array(car_pos)
    min_distance = float('inf')
    closest_segment = None
    closest_point = None

    for i in range(len(xy_pairs) - 1):
        a = np.array(xy_pairs[i])
        b = np.array(xy_pairs[i + 1])
        closest_point_on_ab = closest_point_on_segment(car_pos, a, b)
        dist = distance(car_pos, closest_point_on_ab)
        if dist < min_distance:
            min_distance = dist
            closest_segment = (xy_pairs[i], xy_pairs[i + 1])
            closest_point = closest_point_on_ab
    if is_point_to_left_or_right(closest_segment[0], closest_segment[1], car_pos) == 'left':
        min_distance *= (-1)
    return min_distance, closest_segment, closest_point

# min distance between 2 indices in array of length n
def min_distance(p1, p2, n):
    minpt = min(p1, p2)
    maxpt = max(p1, p2)
    return min(minpt + (n-maxpt), maxpt-minpt)

def find_ephi(wp_yaw, car_yaw):
    yaw_diff = min_distance(wp_yaw, car_yaw, 2*np.pi)
    if is_point_to_left_or_right((0,0), (np.cos(wp_yaw),np.sin(wp_yaw)),(np.cos(car_yaw),np.sin(car_yaw))) == "left":
        yaw_diff *= (-1)
    return yaw_diff

# return True if v1 is facing within pi/2 of the same facing direction as v2
def abs_angle_btwn_vects(v1, v2):
    [(v1x, v1y), (v1x_, v1y_)] = v1
    [(v2x, v2y), (v2x_, v2y_)] = v2
    yaw1 = np.arctan2(v1y_-v1y,v1x_-v1x)
    yaw2 = np.arctan2(v2y_-v2y,v2x_-v2x)
    yaw_diff = min_distance(yaw1, yaw2, 2*np.pi)
    return abs(yaw_diff)

# distance between 2 points
def distance(point1, point2):
    return math.sqrt((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)




