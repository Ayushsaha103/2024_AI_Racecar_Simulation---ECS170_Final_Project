import os
import pygame


# Window CONFIGURE
WIDTH, HEIGHT = 600, 600
TIME_LIMIT    = 60  #How many seconds will it take for one episode?


# ADDED
AGENTX = WIDTH/2
AGENTY = HEIGHT/2

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
INDIGO = (75, 0, 130)
VIOLET = (238, 130, 238)

# Model.learn - Hyperparameter Configure
total_timesteps = 300000 #300k
learning_rate  = 0.0005 #0.004 (4*10^-3) recommended
ent_coef       = 0.01 
gamma          = 0.99 
gae_lambda     = 0.95
max_grad_norm  = 0.5

# Physical CONSTANTS
FPS         = 10

# Model Configure 
Model_Save_Path = "./models/" + str(int(total_timesteps/1000)) + "k.zip"  
# Indicates the model path which will save after the training, 

tensorboard_log = "./DroneLog/"
tensorboard_sub_folder = 'new_training' + str(total_timesteps/1000) + "k"

# Display and asset Settings & Function
BACKGROUND = "assets/sky.png"

# Takes multiple image and provide animation in the game
def spriter(Type):
    if Type == "Car":
        image_width = 80 / 10
        image_height = (8/30) * 621 / 10
        image_path = "./assets/Drone/"

    elif Type == "Baloon":
        image_width = 30
        image_height = int(image_width * 1.7)
        image_path = "./assets/Baloon/"

    player = []

    for image_file in os.listdir(image_path):
        file_path = os.path.join(image_path, image_file)  # Full path to the file
        if os.path.isfile(file_path) and image_file.lower().endswith('.png'):
            image = pygame.image.load(file_path)
            image.convert()
            player.append(pygame.transform.scale(image, (image_width, image_height)))

    return player


def report(environment):
    print("Environment loading..\n")
    print("Observation space:")
    print(environment.observation_space)
    print("")
    print("Action space:")
    print(environment.action_space)
    print("")
    print("Action space sample:")
    print(environment.action_space.sample())
