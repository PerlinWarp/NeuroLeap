import Leap
import sys
import math
import time
import numpy as np
from numpy import linalg as LA
import matplotlib.pyplot as plt
from matplotlib import animation
from mpl_toolkits.mplot3d import Axes3D
import mpl_toolkits.mplot3d as plt3d

import NeuroLeap as nl

def get_rotation_matrix(bone):
	basis = bone.basis
	x_basis = basis.x_basis
	y_basis = basis.y_basis
	z_basis = basis.z_basis
	matrix = Leap.Matrix(x_basis, y_basis, z_basis).to_array_3x3()
	matrix = np.reshape(matrix, newshape=(3, 3))
	return matrix

def get_angles_from_rot(rot_mat):
	"""
	Function from LearnOpenCV, Satya Mallick:
	https://www.learnopencv.com/rotation-matrix-to-euler-angles/
	https://github.com/spmallick/learnopencv/blob/master/RotationMatrixToEulerAngles/rotm2euler.py
	"""
	sy = math.sqrt(rot_mat[0, 0] * rot_mat[0, 0] + rot_mat[1, 0] * rot_mat[1, 0])
	singular = sy < 1e-6

	if not singular:
		x = math.atan2(rot_mat[2, 1], rot_mat[2, 2])
		y = math.atan2(-rot_mat[2, 0], sy)
		z = math.atan2(rot_mat[1, 0], rot_mat[0, 0])
	else:
		x = math.atan2(-rot_mat[1, 2], rot_mat[1, 1])
		y = math.atan2(-rot_mat[2, 0], sy)
		z = 0

	return [math.degrees(angle) for angle in [x, y, z]]

finger_bones = ['metacarpals', 'proximal', 'intermediate', 'distal']

def get_angles(hand):
	'''
	Gets angles in degrees for all joints in the hand.
	'''
	angles = []
	for finger in hand.fingers:
		for b in range(1,4):
			last_bone = finger.bone(b-1)
			bone = finger.bone(b)
			# Generate rotation matrices from basis vectors
			last_bone_mat = get_rotation_matrix(last_bone)
			bone_mat = get_rotation_matrix(bone)
			# Get rotation matrix between bones, change of basis
			rot_mat = np.matmul(bone_mat, last_bone_mat.transpose())
			# Generate euler angles in degrees from rotation matrix
			angles.append(get_angles_from_rot(rot_mat))
	return angles


controller = Leap.Controller()
controller.set_policy_flags(Leap.Controller.POLICY_BACKGROUND_FRAMES)
NUM_POINTS = 22

# Matplotlib Setup
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d', xlim=(-300, 300), ylim=(-200, 400), zlim=(-300, 300))
ax.view_init(elev=45., azim=122)

points = np.zeros((3, NUM_POINTS))
patches = ax.scatter(points[0], points[1], points[2], s=[20]*NUM_POINTS, alpha=1)

def animate(i):
	# Reset the plot
	nl.reset_plot(ax)

	points = nl.get_bone_points(controller)
	if (points is not None):
		patches = ax.scatter(points[0], points[1], points[2], s=[10]*NUM_POINTS, alpha=1)
		nl.plot_points(points, patches)
		nl.plot_bone_lines(points, ax)

	frame = controller.frame()
	hand = frame.hands.frontmost

	if hand.is_valid:
		#print('\r', leap_hand.get_angles(), end='')
		angles = np.array(get_angles(hand))

		pitch = angles[3,0]
		yaw = angles[3,1]
		roll = angles[3,2]

		print("pitch", pitch)
		print("yaw", yaw)
		print("roll", roll)

def main():
	anim = animation.FuncAnimation(fig, animate, blit=False, interval=2)
	try:
		plt.show()
	except KeyboardInterrupt:
		sys.exit(0)

if __name__ == "__main__":
	main()
