import Leap
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
from mpl_toolkits.mplot3d import Axes3D
import mpl_toolkits.mplot3d as plt3d

import NeuroLeap as nl

# Leap Motion Controller Setup
controller = Leap.Controller()
controller.set_policy_flags(Leap.Controller.POLICY_BACKGROUND_FRAMES)
NUM_POINTS = 22

SAVE = True
points_list = []
'''
finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
bone_names = ['MCP', 'PIP', 'DIP', 'TIP']
# We can of course generate column names on the fly:
for finger in finger_names:
	for bone in bone_names:
		for dim in ["x","y","z"]:
			columns.append(f"{finger}_{bone}_{dim}")

print(columns)
'''
columns = [
		"Palm_x", "Palm_y", "Palm_z",
		"Wrist_x", "Wrist_y", "Wrist_z",
		'Thumb_MCP_x', 'Thumb_MCP_y', 'Thumb_MCP_z',
		'Thumb_PIP_x', 'Thumb_PIP_y', 'Thumb_PIP_z',
		'Thumb_DIP_x', 'Thumb_DIP_y', 'Thumb_DIP_z',
		'Thumb_TIP_x', 'Thumb_TIP_y', 'Thumb_TIP_z',
		'Index_MCP_x', 'Index_MCP_y', 'Index_MCP_z',
		'Index_PIP_x', 'Index_PIP_y', 'Index_PIP_z',
		'Index_DIP_x', 'Index_DIP_y', 'Index_DIP_z',
		'Index_TIP_x', 'Index_TIP_y', 'Index_TIP_z',
		'Middle_MCP_x', 'Middle_MCP_y', 'Middle_MCP_z',
		'Middle_PIP_x', 'Middle_PIP_y', 'Middle_PIP_z',
		'Middle_DIP_x', 'Middle_DIP_y', 'Middle_DIP_z',
		'Middle_TIP_x', 'Middle_TIP_y', 'Middle_TIP_z',
		'Ring_MCP_x', 'Ring_MCP_y', 'Ring_MCP_z',
		'Ring_PIP_x', 'Ring_PIP_y', 'Ring_PIP_z',
		'Ring_DIP_x', 'Ring_DIP_y', 'Ring_DIP_z',
		'Ring_TIP_x', 'Ring_TIP_y', 'Ring_TIP_z',
		'Pinky_MCP_x', 'Pinky_MCP_y', 'Pinky_MCP_z',
		'Pinky_PIP_x', 'Pinky_PIP_y', 'Pinky_PIP_z',
		'Pinky_DIP_x', 'Pinky_DIP_y', 'Pinky_DIP_z',
		'Pinky_TIP_x', 'Pinky_TIP_y', 'Pinky_TIP_z'
		]
# Convert this to headers for numpy saving...
headers = ""
for col in columns:
	headers+= col
	headers+= ","
headers = headers[:-2]


def get_bone_points(controller):
	'''
	Gets points for a full hand model. (22 points, 66 vars)
	Uses 4 joints for each finger and 3 for the thumb.
	Also uses Palm and Wrist position.
	Note this could be reduced to 21 points as the thumb has 1 less joint.
	'''
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

	# Add wrist position
	X.append(-1 * hand.wrist_position.x)
	Y.append(hand.wrist_position.y)
	Z.append(hand.wrist_position.z)

	print("Palm, normal roll", hand.palm_normal.roll)
	#print(hand.fingers.joint_position())

	# Add Elbow
	#arm = hand.arm
	#X.append(arm.elbow_position.x)
	#Y.append(arm.elbow_position.y)
	#Z.append(arm.elbow_position.z)



	# Add fingers
	print("Finger 1, dir: ", fingers[1].direction)

	for finger in fingers:
		for joint in range(0,4):
			'''
			0 = JOINT_MCP – The metacarpophalangeal joint, or knuckle, of the finger.
			1 = JOINT_PIP – The proximal interphalangeal joint of the finger. This joint is the middle joint of a finger.
			2 = JOINT_DIP – The distal interphalangeal joint of the finger. This joint is closest to the tip.
			3 = JOINT_TIP – The tip of the finger.
			'''
			X.append(-1 * finger.joint_position(joint)[0])
			Y.append(finger.joint_position(joint)[1])
			Z.append(finger.joint_position(joint)[2])

	#fj = fingers[1].joint_position(1)
	#print("pitch:", fj.pitch)
	#print("yaw:  ", fj.yaw)
	#print("roll: ", fj.roll)

	fj = fingers[1].direction
	print("old pitch:", round(fj.pitch * (180/3.14159265),2))
	print("old yaw:  ", round(fj.yaw * (180/3.14159265), 2))
	#print("old roll: ", round(fingers[1].normal.roll * (180/3.14159265), 2))

	# Get palm angles
	pitch = hand.direction.pitch
	yaw = hand.direction.yaw
	roll = hand.palm_normal.roll

	print()
	fj = fingers[1].direction
	print("ol pitch:", round((fj.pitch-pitch) * (180/3.14159265),2))
	print("ol yaw:  ", round((fj.yaw-yaw) * (180/3.14159265), 2))
	print("ol roll: ", round((fj.roll-roll) * (180/3.14159265), 2))
	print()

	frame = controller.frame()
	for hand in frame.hands:
		hand_x_basis = hand.basis.x_basis
		hand_y_basis = hand.basis.y_basis
		hand_z_basis = hand.basis.z_basis
		hand_origin = hand.palm_position
		hand_transform = Leap.Matrix(hand_x_basis, hand_y_basis, hand_z_basis, hand_origin)
		hand_transform = hand_transform.rigid_inverse()

		for i in range(len(hand.fingers)):
			finger = hand.fingers[i]
			transformed_position = hand_transform.transform_point(finger.tip_position)
			transformed_direction = hand_transform.transform_direction(finger.direction)
			# Do something with the transformed fingers

			mcp = finger.joint_position(0)
			pip = finger.joint_position(1)

			transformed_mcp = hand_transform.transform_direction(mcp)

			if (i == 1):
			#fj = fingers[1].direction
				print("pitch:", round(transformed_direction.pitch * (180/3.14159265),2))
				print("yaw:  ", round(transformed_direction.yaw * (180/3.14159265), 2))
				print("roll: ", round(transformed_direction.roll * (180/3.14159265), 2))

				print("metacarpophalangeal")
				print("pitch:", round(transformed_mcp.pitch * (180/3.14159265),2))
				print("yaw:  ", round(transformed_mcp.yaw * (180/3.14159265), 2))
				print("roll: ", round(transformed_mcp.roll * (180/3.14159265), 2))


	return np.array([X, Z, Y])

def on_close(event):
	print("Closed Figure")

	if (SAVE):
		print("Saving all points gathered")
		# Alternatively use pandas to remove need to make headers string.
		np.savetxt("all_points.csv", points_list, delimiter=',', header=headers, comments='')

# Matplotlib Setup
fig = plt.figure()
fig.canvas.mpl_connect('close_event', on_close)
ax = fig.add_subplot(111, projection='3d', xlim=(-300, 300), ylim=(-200, 400), zlim=(-300, 300))
ax.view_init(elev=45., azim=122)

points = np.zeros((3, NUM_POINTS))
patches = ax.scatter(points[0], points[1], points[2], s=[20]*NUM_POINTS, alpha=1)

def animate(i):
	# Reset the plot
	nl.reset_plot(ax)

	points = get_bone_points(controller)
	if (points is not None):
		if (SAVE):
			points_list.append(points.flatten())

		patches = ax.scatter(points[0], points[1], points[2], s=[10]*NUM_POINTS, alpha=1)
		nl.plot_points(points, patches)
		nl.plot_bone_lines(points, ax)

def main():
	anim = animation.FuncAnimation(fig, animate, blit=False, interval=2)
	try:
		plt.show()
	except KeyboardInterrupt:
		sys.exit(0)

if __name__ == '__main__':
	main()


