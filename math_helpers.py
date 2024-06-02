import math
import numpy as np

############################################################################################################
# waypoints
############################################################################################################

# tell if given_point is to left or right of line segment formed by connecting pt1 -> pt2
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

# calculate distance of given_point from the line formed by connecting p1 and p2
def distance_from_line(p1, p2, given_point):
    # Convert points to numpy arrays for easier calculations
    p1 = np.array(p1)
    p2 = np.array(p2)
    given_point = np.array(given_point)
    
    # Calculate the vector from p1 to p2
    line_vector = p2 - p1
    
    # Calculate the vector from p1 to the given point
    given_point_vector = given_point - p1
    
    # Calculate the perpendicular distance from the given point to the line
    distance = np.linalg.norm(np.cross(line_vector, given_point_vector)) / np.linalg.norm(line_vector)
    if is_point_to_left_or_right(p1, p2, given_point) == 'left':
        return distance
    else: return -distance


############################################################################################################
# road lanes
############################################################################################################

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


############################################################################################################
# env
############################################################################################################

# calculate angle between vect1 and vect2
def angle_between_vectors(vector1, vector2):
    dot_product = sum(v1 * v2 for v1, v2 in zip(vector1, vector2))
    magnitude1 = math.sqrt(sum(v ** 2 for v in vector1))
    magnitude2 = math.sqrt(sum(v ** 2 for v in vector2))
    angle_radians = math.acos(dot_product / (magnitude1 * magnitude2))

    # determine whether vect2 is pointing to left/right/neither of vect1
    cross_product = np.cross(vector1, vector2)
    dir = -1
    if cross_product > 0: dir = 0   # left
    elif cross_product < 0: dir = 1     # right
    else: dir = 2     # "Parallel or Collinear"

    return 1 - (angle_radians / np.pi), dir

# convert (angle, magnitude) into vector
def angle2vect(angle, magnitude=1):
    return [magnitude*math.cos(angle), magnitude*math.sin(angle)]

# subtract vectors: p2 - p1
def vectsub(pt1, pt2):    # pt2 - pt1
    return [pt2[i] - pt1[i] for i in range(len(pt2))]

# normalize vector
def normalize(vect):
    magnitude = math.sqrt(sum(v ** 2 for v in vect))
    return [ vect[i] / magnitude for i in range(len(vect)) ]

############################################################################################################
# env - get_state()
############################################################################################################

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

# # Example usage
# xy_pairs = [(1, 0), (2, 3), (3, 5)]
# car_pos = (1.25, 1)
# min_distance, segment, closest_point = find_nearest_segment(car_pos, xy_pairs)
