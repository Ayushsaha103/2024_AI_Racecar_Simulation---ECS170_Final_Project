

# import matplotlib.pyplot as plt
# from IPython import display
# plt.ion()


# def plot(speeds, dists_from_center, rewards):
#     display.clear_output(wait=True)
#     display.display(plt.gcf())
#     plt.clf()
#     plt.title('Training...')
#     plt.xlabel('Frames')
#     plt.ylabel('')
#     plt.plot(speeds)
#     plt.plot(dists_from_center)
#     plt.plot(rewards)
#     plt.ylim(ymin=0)
#     plt.text(len(speeds)-1, speeds[-1], str(speeds[-1]) + "[m/s]")
#     plt.text(len(dists_from_center)-1, dists_from_center[-1], str(dists_from_center[-1]) + "[m]")
#     plt.text(len(rewards)-1, rewards[-1], str(rewards[-1]) + "[units]")
#     plt.show(block=False)
#     plt.pause(.1)