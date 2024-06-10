import os
import pandas as pd
import matplotlib.pyplot as plt

def generate_graphs(data_file):
    # Read the CSV file into a DataFrame
    data = pd.read_csv(data_file)
    algorithim = data_file.split('_')[0].split('/')[-1]
    print(algorithim)
    
    # Ensure the figures directory exists
    os.makedirs('figures', exist_ok=True)

    # Define the plot
    fig, axs = plt.subplots(2, 2, figsize=(15, 10))

    # Plot average reward per episode
    axs[0, 0].plot(data['episode'], data['avg_reward'], marker='o')
    axs[0, 0].set_title('Average Reward per Episode')
    axs[0, 0].set_xlabel('Episode')
    axs[0, 0].set_ylabel('Avg Reward')

    # Plot average velocity per episode
    axs[0, 1].plot(data['episode'], data['avg_v'], marker='o', color='orange')
    axs[0, 1].set_title('Average Velocity per Episode')
    axs[0, 1].set_xlabel('Episode')
    axs[0, 1].set_ylabel('Avg Velocity')

    # Plot episode time per episode
    axs[1, 0].plot(data['episode'], data['episode_time'], marker='o', color='green')
    axs[1, 0].set_title('Episode Time per Episode')
    axs[1, 0].set_xlabel('Episode')
    axs[1, 0].set_ylabel('Episode Time')

    # Plot distance traveled per episode
    axs[1, 1].plot(data['episode'], data['distance_traveled'], marker='o', color='red')
    axs[1, 1].set_title('Distance Traveled per Episode')
    axs[1, 1].set_xlabel('Episode')
    axs[1, 1].set_ylabel('Distance Traveled')

    # Adjust layout
    plt.tight_layout()

    # Save the figure
    figure_number = len(os.listdir('figures')) + 1
    plt.savefig(f'figures/figure_{algorithim}__{figure_number}.png')
    plt.close()

# Usage example:
# generate_graphs('training_data.csv')
generate_graphs('metrics/ppo_racetrack_3.csv')