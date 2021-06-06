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

def predict_hand(semg_input, model, input_scaler, output_scaler):
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

	return scaled_pred

# ------------ Leap Setup ---------------
controller = Leap.Controller()
controller.set_policy_flags(Leap.Controller.POLICY_BACKGROUND_FRAMES)

# -------- Main Program Loop -----------
if __name__ == '__main__':
	try:
		# Load the keras model
		model_name = "NNNonRel-60secs-FULL-StanScaled"
		model = load_model(f"models/{model_name}.h5")

		input_scaler = joblib.load(f'models/{model_name}-EMG.gz')
		output_scaler = joblib.load(f'models/{model_name}-Hand.gz')

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

		def predict_hand_points(model):
			# Get the Myo data for model input
			myo_data = np.frombuffer(myo_arr.get_obj())

			# Use input to generate predictions
			pred = predict_hand(myo_data, model, input_scaler, output_scaler)

			# Convert them to points
			# Five finger, 4 joints + palm, wrist. x,y,z
			NUM_POINTS = (5 * 4 + 2) * 3
			pred_points = pred.reshape((3, NUM_POINTS//3))

			return pred_points

		def animate(i):
			# Prediction Plotting
			if (p.is_alive()):
				cpoints = predict_hand_points(model)
			else:
				print("Data gatherer has exited")
				quit()

			# Needed for plot_simple, for line plots
			nl.reset_plot(ax)

			if (cpoints is not None):
				patches = ax.scatter(cpoints[0], cpoints[1], cpoints[2], s=10, alpha=1)
				nl.plot_points(cpoints, patches)
				nl.plot_bone_lines(cpoints, ax)

			# Leap Motion Plotting
			## Note this should be done in another thread or weird things happen.
			points = nl.get_bone_points(controller)
			nl.reset_plot(ax2)
			if (points is not None):
				truth = ax2.scatter(points[0], points[1], points[2], s=10, alpha=1)
				nl.plot_points(points, truth)
				nl.plot_bone_lines(points, ax2)

			ax.set_title('Prediction Plot', fontsize=22)
			ax2.set_title('Ground Truth Plot', fontsize=22)

		anim = animation.FuncAnimation(fig, animate, blit=False, interval=2)
		plt.show()
	except KeyboardInterrupt:
		print("Quitting...")
		quit()