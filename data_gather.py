# Simplist data recording + Plotting
'''
The simplict hand tracking model:
	Only record the finger tips. / finger-palm angle etc etc etc 
	Only records a sample from the leap when there is a new myo sample. 
	Use the 50Hz Myo mode.
'''
import time
import multiprocessing

import numpy as np
import pandas as pd
import Leap
from myo_raw import MyoRaw

def data_worker(shared_leap_arr=None, seconds=15, file_name="data_gather.csv"):
	collect = False

	# ------------ Leap Setup ---------------
	leap_data = []

	controller = Leap.Controller()
	controller.set_policy_flags(Leap.Controller.POLICY_BACKGROUND_FRAMES)

	def get_points():
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

	# ------------ Myo Setup ---------------
	m = MyoRaw(raw=False, filtered=True) # 50Hz Filtered Myo data
	m.connect()

	myo_data = []

	def add_to_queue(emg, movement):
		myo_data.append(emg)
		points = get_points()
		if (points is not None):
			ld = get_points().flatten()
			leap_data.append(ld)
			if (shared_leap_arr != None):
				# Move leap data into shared array for plotting
				for i in range(len(ld)):
					shared_leap_arr[i] = ld[i]

	m.add_emg_handler(add_to_queue)

	def print_battery(bat):
		print("Battery level:", bat)

	m.add_battery_handler(print_battery)

	 # Its go time
	m.set_leds([0, 128, 0], [0, 128, 0])
	# Vibrate to know we connected okay
	m.vibrate(1)

	# Wait to start
	# m.connect will wait until we get a connection, but the leap doesnt block
	while not(collect):
		frame = controller.frame()
		hand = frame.hands.rightmost
		if (hand.palm_position.x != 0):
			collect = True
			print(f"Collection started for {seconds} seconds.")

	# Start collecing data.
	start_time = time.time()

	while collect:
		if (time.time() - start_time < seconds):
			m.run(1)
		else:
			collect = False
			collection_time = time.time() - start_time
			print("Finished collecting.")
			print(f"Collection time: {collection_time}")
			print(len(myo_data), "myos collected")
			print(len(leap_data), "leaps collected")

			# Combine the data and record to a df
			myo_cols = ["Channel_1", "Channel_2", "Channel_3", "Channel_4", "Channel_5", "Channel_6", "Channel_7", "Channel_8"]
			leap_cols = []
			finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky', 'Palm']
			# We can of course generate column names on the fly:
			for finger in finger_names:
				for dim in ["x","y","z"]:
						leap_cols.append(f"{finger}_tip_{dim}")

			myo_df = pd.DataFrame(myo_data, columns=myo_cols)
			leap_df = pd.DataFrame(leap_data, columns=leap_cols)

			df = myo_df.join(leap_df)
			df.to_csv(file_name, index=False)

# -------- Main Program Loop -----------
if __name__ == '__main__':
	p = multiprocessing.Process(target=data_worker)
	p.start()