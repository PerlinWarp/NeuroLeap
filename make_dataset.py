import multiprocessing

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
from mpl_toolkits.mplot3d import Axes3D
import mpl_toolkits.mplot3d as plt3d

import data_gather as d
import NeuroLeap as nl

# Configs
FULL_HAND = True
SECONDS = 60
''' RAW is the Myo preprocessing setting.
	If RAW is False, we get undocumented filtered 50Hz. (0x01)
	If RAW is true, we get unrectified 200Hz data between -128 and 127.
'''
RAW = False
CSV_NAME = "post_uni_2"

ops = ""
if (RAW): ops += "raw-"
if (FULL_HAND): ops += "full_hand-"
csv_name = f"{CSV_NAME}-{ops}{SECONDS}s.csv"

if (FULL_HAND):
	# Five finger, 4 joints + palm, wrist. x,y,z
	NUM_POINTS = (5 * 4 + 2) * 3
else:
	NUM_POINTS = 18

# -------- Main Program Loop -----------
if __name__ == '__main__':
	leap_arr = multiprocessing.Array('d', range(NUM_POINTS))

	p = multiprocessing.Process(target=d.data_worker, args=(leap_arr, SECONDS, csv_name, RAW, FULL_HAND))
	p.start()

	# Matplotlib Setup
	fig = plt.figure()
	ax = fig.add_subplot(111, projection='3d', xlim=(-300, 300), ylim=(-200, 400), zlim=(-300, 300))
	ax.view_init(elev=45., azim=122)

	points = np.zeros((3, NUM_POINTS//3))
	patches = ax.scatter(points[0], points[1], points[2], s=20, alpha=1)

	def get_leap_points():
		# TODO Use flags to tell main thread when leap is ready
		if(leap_arr[11] != 0):
			leap_data = np.frombuffer(leap_arr.get_obj())
			leap_data = leap_data.reshape(3,NUM_POINTS//3)
			return leap_data
		return None

	def animate(i):
		if (p.is_alive()):
			cpoints = get_leap_points()
		else:
			print("Data gatherer has exited")
			quit()

		# Reset the plot
		# Really you can just update the lines to avoid this
		nl.reset_plot(ax)

		if (cpoints is not None):
			patches = ax.scatter(cpoints[0], cpoints[1], cpoints[2], s=[10], alpha=1)
			nl.plot_points(cpoints, patches)
			if (FULL_HAND):
				nl.plot_bone_lines(cpoints, ax)
			else:
				nl.plot_simple(cpoints, ax)



	anim = animation.FuncAnimation(fig, animate, blit=False, interval=2)
	plt.show()
