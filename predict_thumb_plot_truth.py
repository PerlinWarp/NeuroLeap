import time
import multiprocessing

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
from mpl_toolkits.mplot3d import Axes3D
import mpl_toolkits.mplot3d as plt3d
from keras.models import load_model

import Leap
from myo_raw import MyoRaw
import NeuroLeap as nl

def predict_thumb(emg, model):
	pred =  np.array([ 51.149292 ,  -7.4921813, 127.01072  ], dtype='float32')
	pred = np.random.rand(1,3) * 200

	emg = emg.reshape(1,8)
	pred = model.predict(emg)

	return pred[0]

# ------------ Leap Setup ---------------
controller = Leap.Controller()
controller.set_policy_flags(Leap.Controller.POLICY_BACKGROUND_FRAMES)

# -------- Main Program Loop -----------
if __name__ == '__main__':
	try:
		# Load the keras model
		model = load_model('BenchmarkNN.h5')

		m = MyoRaw(raw=False, filtered=True) # 50Hz Filtered Myo data
		m.connect()

		# Start a Myo worker to put data into a shared array
		myo_arr = multiprocessing.Array('d', range(8))
		p = multiprocessing.Process(target=nl.get_myodata_arr, args=(m, myo_arr,))
		p.start()

		# Matplotlib Setup
		print("Matplot Setup")
		fig = plt.figure(figsize=(20, 10))
		# The Prediction Leap Plot
		ax = fig.add_subplot(121, projection='3d', xlim=(-300, 300), ylim=(-200, 400), zlim=(-300, 300))
		ax.view_init(elev=45., azim=122)
		# The ground truth leap plot
		ax2 = fig.add_subplot(122, projection='3d', xlim=(-300, 300), ylim=(-200, 400), zlim=(-300, 300))
		ax2.view_init(elev=45., azim=122)

		def predict_points(model):
			# Get the Myo data for model input
			myo_data = np.frombuffer(myo_arr.get_obj())

			# Use input to generate predictions
			thumb_pred = predict_thumb(myo_data, model)
			# As we are only predicting the thumb, I am using a real data to help see if the thumb prediction is bad
			pred = np.array([
			    [-13.35151005, thumb_pred[0],17.06526566, -9.59082985, -31.23623848, -53.12862396],
			    [ 22.12649918, thumb_pred[1],  -70.41703796, -85.38266754, -76.4957428, -67.41526794],
			    [141.71203613, thumb_pred[2], 134.22111511, 124.98007965, 120.3417511, 110.66632843]]
			)
			return pred
			
		def animate(i):
			# Prediction Plotting
			if (p.is_alive()):
				cpoints = predict_points(model)
			else:
				print("Data gatherer has exited")
				quit()

			# Needed for plot_simple, for line plots
			nl.reset_plot(ax)
			
			if (cpoints is not None):
				patches = ax.scatter(cpoints[0], cpoints[1], cpoints[2], s=10, alpha=1)
				nl.plot_simple(cpoints, ax)
				nl.plot_points(cpoints, patches)

			# Leap Motion Plotting
			points = nl.get_points(controller)
			nl.reset_plot(ax2)
			if (points is not None):
				truth = ax2.scatter(points[0], points[1], points[2], s=10, alpha=1)
				nl.plot_simple(points, ax2)

			ax.title.set_text('Prediction Plot')
			ax2.title.set_text('Ground Truth Plot')

		anim = animation.FuncAnimation(fig, animate, blit=False, interval=2)
		plt.show()
	except KeyboardInterrupt:
		print("Quitting...")
		quit()		