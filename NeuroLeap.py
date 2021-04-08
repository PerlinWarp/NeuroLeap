import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
from mpl_toolkits.mplot3d import Axes3D
import mpl_toolkits.mplot3d as plt3d

# Leap Motion Hand Animation

def get_points(controller):
	frame = controller.frame()
	hand = frame.hands.rightmost
	if not hand.is_valid: return None
	fingers = hand.fingers

	X = []
	Y = []
	Z = []

	# Add the position of the palms
	X.append(-1 *hand.palm_position.x)
	Y.append(hand.palm_position.y)
	Z.append(hand.palm_position.z)

	for finger in fingers:
		# Add finger tip positions
		X.append(-1 * finger.stabilized_tip_position.x)
		Y.append(finger.stabilized_tip_position.y)
		Z.append(finger.stabilized_tip_position.z) 
	return np.array([X, Z, Y])


def plot_points(points, scatter):
	scatter.set_offsets(points[:2].T)
	scatter.set_3d_properties(points[2], zdir='z')

def plot_simple(points, ax):
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

def reset_plot(ax):
	'''
	The Line plots will plot other eachother, as I make new lines instead of changing the data for the old ones
	TODO: Fix plot_simple and plot_lines so I don't need to do this. 
	'''
	# Reset the plot
	ax.cla()
	# Really you can just update the lines to avoid this
	ax.set_xlim3d([-300, 300])
	ax.set_xlabel('X [mm]')
	ax.set_ylim3d([-200, 400])
	ax.set_ylabel('Y [mm]')
	ax.set_zlim3d([-300, 300])
	ax.set_zlabel('Z [mm]')

# Myo Multiprocessing functions
def get_myodata_arr(myo, shared_arr):
	# ------------ Myo Setup ---------------
	def add_to_queue(emg, movement):
		for i in range(8):
			shared_arr[i] = emg[i]

	myo.add_emg_handler(add_to_queue)

	def print_battery(bat):
		print("Battery level:", bat)

	myo.add_battery_handler(print_battery)

	# Its go time
	myo.set_leds([128, 128, 0], [128, 128, 0])
	# Vibrate to know we connected okay
	myo.vibrate(1)

	# Wait to start
	# m.connect will wait until we get a connection, but the leap doesnt block
	try:
		while (True):
				myo.run(1)
	except KeyboardInterrupt:
		print("Quitting Myo worker")
		quit()
