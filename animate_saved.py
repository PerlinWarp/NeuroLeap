import numpy as np
import matplotlib.pyplot as plt
# Fix for unresponsive 3d plot
plt.switch_backend('Qt4Agg')
from matplotlib import animation
from mpl_toolkits.mplot3d import Axes3D
import mpl_toolkits.mplot3d as plt3d

import NeuroLeap as nl

# Configuraion options
MYO_DATA = True
FULL_HAND = False
FILE_PATH = "thumb_dataset_30.csv"
#FILE_PATH = "data/thumb_dataset-240-raw-False.csv"

if (FULL_HAND):
	# Five finger, 4 joints + palm, wrist. x,y,z
	NUM_POINTS = (5 * 4 + 2) * 3
else:
	NUM_POINTS = 18

# Skip first row as we dont care about columns
all_points = np.loadtxt(FILE_PATH, delimiter=',', skiprows=1)
if (MYO_DATA):
	# Don't try and plot Myo channel data
	all_points = all_points[:,8:]
	if (all_points.shape[1] == 26):
		print("Assuming dual Myo")
		# Remove the second load of Myo data too.
		all_points = all_points[:,8:]
if (all_points.shape[1] == 18):
	# We are only using the finger tips, use plot_simple
	FULL_HAND = False

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d', xlim=(-300, 400), ylim=(-200, 400), zlim=(-300, 300))
ax.view_init(elev=45., azim=122)

points_ = np.zeros((3, NUM_POINTS))
sizes = [10]*(NUM_POINTS//3)
sizes[0] = 30
patches = ax.scatter(points_[0], points_[1], points_[2], s=10, alpha=1)

def animate(i):
	# Reset the plot
	nl.reset_plot(ax)

	frame_points = all_points[i % len(all_points)]
	frame_points = frame_points.reshape((3, NUM_POINTS//3))

	patches = ax.scatter(frame_points[0], frame_points[1], frame_points[2], s=10, alpha=1)
	nl.plot_points(frame_points, patches)
	if (FULL_HAND):
		nl.plot_bone_lines(frame_points, ax)
	else:
		# Only plot fingertips
		nl.plot_simple(frame_points, ax)
	return patches,

def main():
	anim = animation.FuncAnimation(fig, animate, blit=False, interval=2)
	try:
		plt.show()
	except KeyboardInterrupt:
		sys.exit(0)

main()