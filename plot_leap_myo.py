import sys
import multiprocessing
import mpl_toolkits.mplot3d as plt3d
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import animation
import numpy as np

import Leap
from myo_raw import MyoRaw

# ------------ Myo Setup ---------------
q = multiprocessing.Queue()

m = MyoRaw(raw=True, filtered=False)
m.connect()

def worker(q):
	def add_to_queue(emg, movement):
		q.put(emg)

	m.add_emg_handler(add_to_queue)

	"""worker function"""
	while True:
		m.run(1)
	print("Worker Stopped")

def print_battery(bat):
	print("Battery level:", bat)

m.add_battery_handler(print_battery)

 # Orange logo and bar LEDs
m.set_leds([128, 0, 0], [128, 0, 0])
# Vibrate to know we connected okay
m.vibrate(1)

# ------------ Leap Setup ---------------
controller = Leap.Controller()
controller.set_policy_flags(Leap.Controller.POLICY_BACKGROUND_FRAMES)


# ------------ Plot Setup ---------------
fig = plt.figure()
ax = fig.add_subplot(121, projection='3d', xlim=(-300, 400), ylim=(-200, 400), zlim=(-300, 300))
ax.view_init(elev=10., azim=250)
colors = np.array([100, 100, 100, 100, 100, 500])

# Add Myo Plotting
axm = fig.add_subplot(122)
global myox
myox = [128,128,128,128,128,128,128,128]
rects  = axm.bar(list(range(1,9)), myox)

points = np.zeros((3, 6))

lines = []

palm_x, palm_y, palm_z = points.T[5]
for (x, y, z) in points[:, :5].T:
	line = plt3d.art3d.Line3D([x, palm_x], [y, palm_y], [z, palm_z])
	lines.append(line)
	ax.add_line(line)

patches = ax.scatter(points[0], points[1], points[2], s=[30, 30, 30, 30, 30, 100], alpha=1)
patches.set_array(colors)

def get_points():
	frame = controller.frame()
	hand = frame.hands.rightmost
	if not hand.is_valid: return np.array(patches._offsets3d)
	fingers = hand.fingers
	X = [finger.stabilized_tip_position.x for finger in fingers]
	X.append(hand.palm_position.x)
	Y = [finger.stabilized_tip_position.y for finger in fingers]
	Y.append(hand.palm_position.y)
	Z = [finger.stabilized_tip_position.z for finger in fingers]
	Z.append(hand.palm_position.z)
	return np.array([X, Z, Y])

def plot_lines(points):
	palm_x, palm_y, palm_z = points.T[5]
	for (i, line) in enumerate(lines):
		line.set_data([points[0, i], palm_x], [points[1, i], palm_y])
		line.set_3d_properties([points[2, i], palm_z])

def plot_points(points):
	patches.set_offsets(points[:2].T)
	patches.set_3d_properties(points[2], zdir='z')

def init():
	points = get_points()
	plot_points(points)
	plot_lines(points)

	return patches, rects

def animate(i):
	myox = [128,128,128,128,128,128,128,128]
	points = get_points()
	plot_points(points)
	plot_lines(points)

	# Myo Plot
	while not(q.empty()):
		myox = list(q.get())
	
	for rect, yi in zip(rects, myox):
		rect.set_height(yi)

	return patches, rects

def main():
	anim = animation.FuncAnimation(fig, animate, init_func=init, blit=False, interval=2)
	try:
		plt.show()
	except KeyboardInterrupt:
		sys.exit(0)

if __name__ == '__main__':
	# Start Myo Process
	p = multiprocessing.Process(target=worker, args=(q,))
	p.start()

	main()
