import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from math import pi

def get_latest_num(folder, prefix):
    """Get the latest number used for saved models or logs."""
    files = [f for f in os.listdir(folder) if f.startswith(prefix) and f.endswith('.zip')]
    if not files:
        return 0
    numbers = [int(f.split('_')[-1].replace('.zip', '')) for f in files]
    return max(numbers)

def plot_data(algorithm_type, number=-1):
    if number == -1:
        number = get_latest_num('models', algorithm_type)
    
    output_folder = f'figures/{algorithm_type.lower()}_{number}'
    os.makedirs(output_folder, exist_ok=True)

    data = pd.read_csv(f'metrics/{algorithm_type.lower()}_racetrack_{number}.csv')

    # Convert lidar readings from string representation to lists
    data['lidar_readings'] = data['lidar_readings'].apply(lambda x: np.fromstring(x.strip('[]'), sep=' '))
    
    # Aggregate lidar readings to a single value (e.g., mean)
    data['lidar_mean'] = data['lidar_readings'].apply(np.mean)
    
    episodes = data['episode']
    
    # Line Plot: Average Reward Over Episodes with Trend Line
    plt.figure(figsize=(10, 5))
    plt.plot(data['episode'], data['avg_reward'], label=algorithm_type)
    sns.regplot(x='episode', y='avg_reward', data=data, scatter=False, label='Trend Line', color='orange')
    plt.xlabel('Episode')
    plt.ylabel('Average Reward')
    plt.title('Average Reward Over Episodes')
    plt.legend()
    plt.savefig(os.path.join(output_folder, f'{algorithm_type}_{number}_avg_reward_over_episodes.png'))
    plt.close()
    
    # Box Plot: Average Distance to Left Boundary
    plt.figure(figsize=(10, 5))
    sns.boxplot(data=data['avg_distance_to_left_boundary'])
    plt.xlabel('Algorithm Type')
    plt.ylabel('Average Distance to Left Boundary')
    plt.title('Distance to Left Boundary')
    plt.savefig(os.path.join(output_folder, f'{algorithm_type}_{number}_distance_to_left_boundary.png'))
    plt.close()
    
    # Scatter Plot: Lidar Readings (Mean) vs. Distance Traveled with Trend Line
    plt.figure(figsize=(10, 5))
    plt.scatter(data['lidar_mean'], data['distance_traveled'])
    sns.regplot(x='lidar_mean', y='distance_traveled', data=data, scatter=False, label='Trend Line', color='orange')
    plt.xlabel('Lidar Readings (Mean)')
    plt.ylabel('Distance Traveled')
    plt.title('Lidar Readings vs. Distance Traveled')
    plt.legend()
    plt.savefig(os.path.join(output_folder, f'{algorithm_type}_{number}_lidar_vs_distance.png'))
    plt.close()
    
    
    # Heatmap: Correlation Matrix of Metrics
    plt.figure(figsize=(10, 8))
    corr = data.drop(columns=['lidar_readings']).corr()  # Drop the lidar_readings column for correlation matrix
    sns.heatmap(corr, annot=True, cmap='coolwarm')
    plt.title('Correlation Matrix of Metrics')
    plt.savefig(os.path.join(output_folder, f'{algorithm_type}_{number}_correlation_matrix.png'))
    plt.close()


# Example usage:
plot_data('PPO', number=46)
