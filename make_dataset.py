import multiprocessing

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
from mpl_toolkits.mplot3d import Axes3D
import mpl_toolkits.mplot3d as plt3d

import data_gather as d

NUM_POINTS = 18
SECONDS = 30

# -------- Main Program Loop -----------
if __name__ == '__main__':
	leap_arr = multiprocessing.Array('d', range(NUM_POINTS))

	p = multiprocessing.Process(target=d.data_worker, args=(leap_arr, SECONDS, "thumb_dataset_30.csv"))
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

	def plot_points(points):
		patches.set_offsets(points[:2].T)
		patches.set_3d_properties(points[2], zdir='z')

	def plot_simple(points):
		'''
		Plot lines connecting the palms to the fingers, assuming thats the only data we get.
		'''
		# Get Palm Position
		palm = points[:,0]
		
		# For Each of the 5 fingers
		for n in range(1,6):
			# Draw a line from the palm to the finger tips
			tip = points[:,n]
			top = plt3d.art3d.Line3D([palm[0], tip[0]], [palm[1], tip[1]], [palm[2], tip[2]])
			ax.add_line(top)
		
	def animate(i):
		if (p.is_alive()):
			cpoints = get_points()
		else:
			print("Data gatherer has exited")
			quit()

		# Reset the plot
		ax.cla()
		# Really you can just update the lines to avoid this
		ax.set_xlim3d([-300, 300])
		ax.set_xlabel('X [mm]')
		ax.set_ylim3d([-200, 400])
		ax.set_ylabel('Y [mm]')
		ax.set_zlim3d([-300, 300])
		ax.set_zlabel('Z [mm]')
		
		if (cpoints is not None):
			patches = ax.scatter(cpoints[0], cpoints[1], cpoints[2], s=[10]*NUM_POINTS, alpha=1)
			plot_simple(cpoints)
			plot_points(cpoints)


	anim = animation.FuncAnimation(fig, animate, blit=False, interval=2)
	plt.show()
	