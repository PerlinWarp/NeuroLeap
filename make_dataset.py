import multiprocessing

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
from mpl_toolkits.mplot3d import Axes3D
import mpl_toolkits.mplot3d as plt3d

import data_gather as d

NUM_POINTS = 18

# -------- Main Program Loop -----------
if __name__ == '__main__':
	leap_arr = multiprocessing.Array('d', range(NUM_POINTS))

	p = multiprocessing.Process(target=d.data_worker, args=(leap_arr, 5, "data_gather5.csv"))
	p.start()

	# Matplotlib Setup
	fig = plt.figure()
	ax = fig.add_subplot(111, projection='3d', xlim=(-300, 300), ylim=(-200, 400), zlim=(-300, 300))
	ax.view_init(elev=45., azim=122)

	points = np.zeros((3, NUM_POINTS//3))
	patches = ax.scatter(points[0], points[1], points[2], s=[20]*NUM_POINTS, alpha=1)

	def get_points():
		if(leap_arr[0] != 0):
			leap_data = np.frombuffer(leap_arr.get_obj())
			leap_data = leap_data.reshape(3,NUM_POINTS//3)
			return leap_data
		return None
		
	def animate(i):
		if (p.is_alive()):
			points = get_points()
			if (points is not None):
				patches.set_offsets(points[:2].T)
				patches.set_3d_properties(points[2], zdir='z')
		else:
			print("Data gatherer has exited")
			quit()

	anim = animation.FuncAnimation(fig, animate, blit=False, interval=2)
	plt.show()
	