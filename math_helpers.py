
import math
import numpy as np



############################################################################################################
# waypoints


def is_point_to_left_or_right(point1, point2, given_point):
    # Calculate vectors from point1 to point2 and from point1 to the given_point
    vector_p1p2 = (point2[0] - point1[0], point2[1] - point1[1])
    vector_p1_given = (given_point[0] - point1[0], given_point[1] - point1[1])

    # Calculate the cross product of the two vectors
    cross_product = vector_p1p2[0] * vector_p1_given[1] - vector_p1p2[1] * vector_p1_given[0]

    # Determine the orientation of the given point relative to the vector formed by point1 and point2
    if cross_product > 0:
        return 'left'
    elif cross_product < 0:
        return 'right'
    else:
        return 'on_line'

############################################################################################################
# road lanes

# add 2 vectors
def add(p1, p2):
    p1[0] += p2[0]
    p1[1] += p2[1]
    return p1

# rotate a vector by 2deg (hard-coded 2)
def turn_vector(vector, turn_right):
    # Calculate the angle of the vector
    angle = math.atan2(vector[1], vector[0])  # in radians

    # Add or subtract 5 degrees to the angle based on turn direction
    if turn_right: angle -= math.radians(2)  # Convert degrees to radians
    else: angle += math.radians(2)  # Convert degrees to radians

    # Calculate the new x and y components of the slanted vector
    magnitude = math.sqrt(vector[0] ** 2 + vector[1] ** 2)
    slanted_x = magnitude * math.cos(angle)
    slanted_y = magnitude * math.sin(angle)

    return [slanted_x, slanted_y]

# calculate the location of a new line segment,
# parallel to the given line segment
def calculate_parallel_points(start, dest, dist=1, right_dir = True):

    # Convert the input points to arrays and ensure they have the same data type
    start = np.array(start, dtype=float)
    dest = np.array(dest, dtype=float)
    
    # Calculate the direction vector from start to dest
    direction_vector = dest - start
    
    # Calculate the perpendicular vector by rotating the direction vector by 90 degrees clockwise
    perpendicular_vector = []
    if right_dir:
        perpendicular_vector = np.array([direction_vector[1], -direction_vector[0]], dtype=direction_vector.dtype)
    else:
        perpendicular_vector = np.array([-direction_vector[1], direction_vector[0]], dtype=direction_vector.dtype)


    # Normalize the perpendicular vector
    perpendicular_vector /= np.linalg.norm(perpendicular_vector)
    
    # Scale the perpendicular vector by the distance 'dist'
    scaled_perpendicular_vector = perpendicular_vector * dist
    
    # Calculate the new points by adding the scaled perpendicular vector to the start and dest points
    new_start = start + scaled_perpendicular_vector
    new_dest = dest + scaled_perpendicular_vector
    
    return tuple(new_start), tuple(new_dest)

# distance between 2 points
def distance(point1, point2):
    return math.sqrt((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)

