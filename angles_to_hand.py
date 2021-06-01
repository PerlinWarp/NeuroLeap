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

def on_close(event):
	print("Closed Figure")

	if (SAVE):
		print("Saving all points gathered")
		# Alternatively use pandas to remove need to make headers string.
		np.savetxt("all_points.csv", points_list, delimiter=',', header=headers, comments='')

# Matplotlib Setup
fig = plt.figure()
fig.canvas.mpl_connect('close_event', on_close)
ax = fig.add_subplot(121, projection='3d', xlim=(-300, 300), ylim=(-200, 400), zlim=(-300, 300))
ax2 = fig.add_subplot(122, projection='3d', xlim=(-300, 300), ylim=(-200, 400), zlim=(-300, 300))
ax.view_init(elev=45., azim=122)
ax2.view_init(elev=45., azim=122)

points = np.zeros((3, NUM_POINTS))
patches = ax.scatter(points[0], points[1], points[2], s=[20]*NUM_POINTS, alpha=1)


def dot_product_angle(v1,v2):
	'''
	Get the angle between 2 vectors using the dot product
	'''
	if np.linalg.norm(v1) == 0 or np.linalg.norm(v2) == 0:
		# Avoiding a zero division error
		print("Zero magnitude vector!")
	else:
		vector_dot_product = np.dot(v1,v2)
		# Get angle in radians
		arccos = np.arccos(vector_dot_product / (np.linalg.norm(v1) * np.linalg.norm(v2)))
		# Convert to degrees
		#angle = np.degrees(arccos)
		angle = arccos
		return angle
	return 0

def animate(i):
	# Reset the plot
	nl.reset_plot(ax)

	points = nl.get_bone_points(controller)
	a_points = []
	if (points is not None):
		if (SAVE):
			points_list.append(points.flatten())

		patches = ax.scatter(points[0], points[1], points[2], s=[10]*NUM_POINTS, alpha=1)
		nl.plot_points(points, patches)
		nl.plot_bone_lines(points, ax)

		# Print the angles
		# Wrist
		wri = points[:,1]

		# For Each of the 5 fingers
		for i in range(0,5):
			n = 4*i + 2

			# Get each of the bones
			mcp = points[:,n+0]
			pip = points[:,n+1]
			dip = points[:,n+2]
			tip = points[:,n+3]

			if (i == 1):
				print()
				# Get vectors for each bone
				metacarpal   = mcp - wri
				proximital   = pip - mcp
				intermediate = dip - pip
				distal       = tip - dip

				m_p = dot_product_angle(metacarpal, proximital)
				# Intermediate Proximital
				p_i = dot_product_angle(proximital, intermediate)
				# Distal Intermediate Angle
				i_d = dot_product_angle(intermediate, distal)

				print("Thumb Angles: ",round(m_p,2), round(p_i,2), round(i_d,2))
				'''
				This is the angle between the vectors on the plane that joins them
				https://math.stackexchange.com/questions/53291/how-is-the-angle-between-2-vectors-in-more-than-3-dimensions-defined
				'''

				# Can we just project them to a lower dimention
				# XY (Above)
				metacarpal_xy   = metacarpal[0:2]
				proximital_xy   = proximital[0:2]
				intermediate_xy = intermediate[0:2]
				distal_xy       = distal[0:2]

				m_p_xy = dot_product_angle(metacarpal_xy, proximital_xy)
				# Intermediate Proximital
				p_i_xy = dot_product_angle(proximital_xy, intermediate_xy)
				# Distal Intermediate Angle
				i_d_xy = dot_product_angle(intermediate_xy, distal_xy)

				print("Thumb Angles Above: ",round(m_p_xy,2), round(p_i_xy,2), round(i_d_xy,2))

				# XZ (Behind)
				metacarpal_xz   = metacarpal[-1]
				proximital_xz   = proximital[-1]
				intermediate_xz = intermediate[-1]
				distal_xz       = distal[-1]

				m_p_xz = dot_product_angle(metacarpal_xz, proximital_xz)
				# Intermediate Proximital
				p_i_xz = dot_product_angle(proximital_xz, intermediate_xz)
				# Distal Intermediate Angle
				i_d_xz = dot_product_angle(intermediate_xz, distal_xz)

				print("Thumb Angles Behind: ",round(m_p_xz,2), round(p_i_xz,2), round(i_d_xz,2))

				# YZ (Side - Important?)
				metacarpal_yz   = metacarpal[1:3]
				proximital_yz   = proximital[1:3]
				intermediate_yz = intermediate[1:3]
				distal_yz       = distal[1:3]

				m_p_yz = dot_product_angle(metacarpal_yz, proximital_yz)
				# Intermediate Proximital
				p_i_yz = dot_product_angle(proximital_yz, intermediate_yz)
				# Distal Intermediate Angle
				i_d_yz = dot_product_angle(intermediate_yz, distal_yz)

				print("Thumb Angles Side: ",round(m_p_yz,2), round(p_i_yz,2), round(i_d_yz,2))

				# Add these angles to a list
				a_points.append([m_p_xy, p_i_xy, i_d_xy])
				a_points.append([m_p_xz, p_i_xz, i_d_xz])
				a_points.append([m_p_yz, p_i_yz, i_d_yz])

		# Creating the 2nd plot
		nl.reset_plot(ax2)

		angle_plot = ax2.scatter(points[0], points[1], points[2], s=[10]*NUM_POINTS, alpha=1)

		# Convert to a numpy array
		a_points = np.array(a_points).T

		# Scale everything
		a_points = a_points*40

		angle_plot.set_offsets(a_points[:2].T)
		angle_plot.set_3d_properties(a_points[2], zdir='z')

		#nl.plot_points(points, angle_plot)
		#nl.plot_bone_lines(points, ax2)




def main():
	anim = animation.FuncAnimation(fig, animate, blit=False, interval=2)
	try:
		plt.show()
	except KeyboardInterrupt:
		sys.exit(0)

if __name__ == '__main__':
	main()


