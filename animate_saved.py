import numpy as np
import matplotlib.pyplot as plt
# Fix for unresponsive 3d plot
plt.switch_backend('Qt4Agg')
from matplotlib import animation
from mpl_toolkits.mplot3d import Axes3D
import mpl_toolkits.mplot3d as plt3d

import NeuroLeap as nl

#from plot_hand import plot_lines
NUM_POINTS = 18 
MYO_DATA = True
FINGER_PLOT = False
# Skip first row as we dont care about columns
all_points = np.loadtxt('thumb_dataset_60.csv', delimiter=',', skiprows=1)
if (MYO_DATA):
	# Don't try and plot Myo channel data
	all_points = all_points[:,8:]
if (all_points.shape[1] == 18):
	# We are only using the finger tips, use finger_plot
	FINGER_PLOT = True
## To Remove all rows that only contain zero, when the hand was not in range
#data = data[~np.all(data == 0, axis=1)]

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
	if (FINGER_PLOT):
		nl.plot_simple(frame_points, ax)
	else:
		nl.plot_bone_lines(frame_points, ax)
	return patches,

def main():
	anim = animation.FuncAnimation(fig, animate, blit=False, interval=2)
	try:
		plt.show()
	except KeyboardInterrupt:
		sys.exit(0)
		
main()