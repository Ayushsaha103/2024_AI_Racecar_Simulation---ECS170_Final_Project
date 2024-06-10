# Import necessary libraries
import numpy as np  # For numerical operations
import matplotlib.pyplot as plt  # For plotting
from scipy.interpolate import splprep, splev  # For spline interpolation

# Function to calculate the curvature of a curve given x and y coordinates
def calculate_curvature(x, y):
    # Compute first derivatives
    dx, dy = np.gradient(x), np.gradient(y)
    # Compute second derivatives
    ddx, ddy = np.gradient(dx), np.gradient(dy)
    # Calculate curvature using the formula |x''y' - x'y''| / (x'^2 + y'^2)^(3/2)
    curvature = np.abs(ddx * dy - dx * ddy) / np.power(dx**2 + dy**2, 1.5)
    return curvature

# Function to generate a racetrack
def generate_racetrack(length, width, num_curves, max_curvature, track_number=42):
    # Set random seed for reproducibility (commented out for random tracks each run)
    np.random.seed(track_number)

    # Generate random control points within a specified range
    angles = np.sort(np.random.uniform(0, 2 * np.pi, num_curves))
    radii = np.random.uniform(0.5 * length, length, num_curves)

    # Calculate x and y coordinates of control points
    x = radii * np.cos(angles)
    y = radii * np.sin(angles)

    # Combine x and y into a single array of control points
    control_points = np.column_stack((x, y))
    # Add the first point again to close the loop
    control_points = np.vstack([control_points, control_points[0]])

    # Create a B-spline representation of the control points
    tck, _ = splprep(control_points.T, s=0, per=True)

    max_curvature_reached = False  # Flag to check if curvature is within the limit
    while not max_curvature_reached:
        # Create a fine set of points along the spline
        u_fine = np.linspace(0, 1, 1000)
        x_fine, y_fine = splev(u_fine, tck)

        # Calculate the curvature of the fine points
        curvature = calculate_curvature(x_fine, y_fine)
        if np.max(curvature) > max_curvature:
            # If curvature exceeds the max limit, regenerate the control points
            radii = np.random.uniform(0.5 * length, length, num_curves)
            x = radii * np.cos(angles)
            y = radii * np.sin(angles)
            control_points = np.column_stack((x, y))
            control_points = np.vstack([control_points, control_points[0]])
            tck, u = splprep(control_points.T, s=0, per=True)
        else:
            max_curvature_reached = True  # Exit the loop if curvature is acceptable

    # Compute the normalized direction vectors for the center line
    dx, dy = np.gradient(x_fine), np.gradient(y_fine)
    norms = np.hypot(dx, dy)
    dx, dy = dx / norms, dy / norms

    # Calculate the left and right boundaries of the track
    left_boundary_x = x_fine + width / 2 * dy
    left_boundary_y = y_fine - width / 2 * dx
    right_boundary_x = x_fine - width / 2 * dy
    right_boundary_y = y_fine + width / 2 * dx

    return x_fine, y_fine, left_boundary_x, left_boundary_y, right_boundary_x, right_boundary_y

def plot_racetrack(x_center, y_center, x_left, y_left, x_right, y_right):
    # Plot the center line
    plt.plot(x_center, y_center, 'k-', label='Center Line')
    # Plot the left and right boundaries
    plt.plot(x_left, y_left, 'b--', label='Left Boundary')
    plt.plot(x_right, y_right, 'r--', label='Right Boundary')
    # Set axis limits
    plt.axis('equal')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('Generated Racetrack')
    plt.legend()
    plt.show()

# Parameters for generating the racetrack
track_length = 1000
track_width = 10
number_of_curves = 25
max_curvature = 0.2

# Call the function to generate and display the racetrack
track = generate_racetrack(track_length, track_width, number_of_curves, max_curvature)
# plot_racetrack(*track)