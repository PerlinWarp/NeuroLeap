import time
import multiprocessing

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
from mpl_toolkits.mplot3d import Axes3D
import mpl_toolkits.mplot3d as plt3d
from keras.models import load_model
import joblib

import Leap
from myo_raw import MyoRaw
import NeuroLeap as nl

def predict_thumb(emg, model):
	'''
	Use when predicting the **absolute position** of the thumb from the Leap.
	Bad idea, keeping for archive reasons.
	'''
	emg = emg.reshape(1,8)
	thumb_pred = model.predict(emg)
	thumb_pred = thumb_pred[0]

	# Turn this into actual points to other functions can treat predict_points the same.
	pred = np.array([
				    [-13.35151005, thumb_pred[0] ,17.06526566, -9.59082985, -31.23623848, -53.12862396],
				    [ 22.12649918, thumb_pred[1],  -70.41703796, -85.38266754, -76.4957428, -67.41526794],
				    [141.71203613, thumb_pred[2], 134.22111511, 124.98007965, 120.3417511, 110.66632843]]
				)
	return pred

def predict_rel_thumb(semg_input, model, input_scaler, output_scaler):
	'''
	Use when repredicting the relative position of the hand.
	This allows to predict without the hand position being the same in prod as it was while training. 
	'''
	# Get some input data
	semg_input = semg_input.reshape(1,8)

	# Scale the input
	scaled_input = input_scaler.transform(semg_input)
	# Get a prediction
	pred = model.predict(scaled_input)
	# Scale it back to a value
	scaled_pred = output_scaler.inverse_transform(pred)
	scaled_pred = scaled_pred[0]
	print('Pred', scaled_pred)
	# Since this is a relative thumb position, we need to add the palm positions on
	xp = scaled_pred[0] - 13.35151005
	yp = scaled_pred[1] + 22.12649918
	zp = scaled_pred[2] + 141.71203613

	# Turn this into actual points to other functions can treat predict_points the same.
	pred = np.array([
				    [-13.35151005, xp ,17.06526566, -9.59082985, -31.23623848, -53.12862396],
				    [ 22.12649918, yp,  -70.41703796, -85.38266754, -76.4957428, -67.41526794],
				    [141.71203613, zp, 134.22111511, 124.98007965, 120.3417511, 110.66632843]]
				)
	return pred

# ------------ Leap Setup ---------------
controller = Leap.Controller()
controller.set_policy_flags(Leap.Controller.POLICY_BACKGROUND_FRAMES)

# -------- Main Program Loop -----------
if __name__ == '__main__':
	try:
		# Load the keras model
		#model = load_model('BenchmarkNN.h5')
		model = load_model('models/BenchmarkNNRel-MinMaxScaled.h5')
		input_scaler = joblib.load('models/MinMaxRelThumb8Apr-EMG.gz')
		output_scaler = joblib.load('models/MinMaxRelThumb8Apr-Hand.gz')

		m = MyoRaw(raw=False, filtered=True) # 50Hz Filtered Myo data
		m.connect()

		# Start a Myo worker to put data into a shared array
		myo_arr = multiprocessing.Array('d', range(8))
		p = multiprocessing.Process(target=nl.get_myodata_arr, args=(m, myo_arr,))
		p.start()

		# Matplotlib Setup
		print("Matplot Setup")
		fig = plt.figure(figsize=(20, 10), dpi=100)
		# The Prediction Leap Plot
		ax = fig.add_subplot(121, projection='3d', xlim=(-200, 300), ylim=(-200, 400), zlim=(-200, 200))
		ax.view_init(elev=45., azim=122)
		# The ground truth leap plot
		ax2 = fig.add_subplot(122, projection='3d', xlim=(-200, 300), ylim=(-200, 400), zlim=(-200, 200))
		ax2.view_init(elev=45., azim=122)

		def predict_points(model):
			# Get the Myo data for model input
			myo_data = np.frombuffer(myo_arr.get_obj())

			# Use input to generate predictions
			pred = predict_rel_thumb(myo_data, model, input_scaler, output_scaler)
			# As we are only predicting the thumb, I am using a real data to help see if the thumb prediction is bad
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
			## Note this should be done in another thread or weird things happen. 
			points = nl.get_points(controller)
			nl.reset_plot(ax2)
			if (points is not None):
				truth = ax2.scatter(points[0], points[1], points[2], s=10, alpha=1)
				nl.plot_simple(points, ax2)

			ax.set_title('Prediction Plot', fontsize=22)
			ax2.set_title('Ground Truth Plot', fontsize=22)

		anim = animation.FuncAnimation(fig, animate, blit=False, interval=2)
		plt.show()
	except KeyboardInterrupt:
		print("Quitting...")
		quit()		