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
import NeuroLeap as nl

def data_worker(shared_leap_arr=None, seconds=15, file_name="data_gather.csv", raw=False, full_hand=False):
	collect = False

	# ------------ Leap Setup ---------------
	leap_data = []

	controller = Leap.Controller()
	controller.set_policy_flags(Leap.Controller.POLICY_BACKGROUND_FRAMES)

	# ------------ Myo Setup ---------------
	if (raw):
		m = MyoRaw(raw=True, filtered=False) # 200Hz Non-Filtered Myo data
	else:
		m = MyoRaw(raw=False, filtered=True) # 50Hz Filtered Myo data
	m.connect()

	myo_data = []

	def add_to_queue(emg, movement):
		'''
		Add myo data to myo_data, 
		add leap data to leap_data and shared_leap_arr for plots in other thread
		'''
		myo_data.append(emg)
		if (full_hand):
			points = nl.get_bone_points(controller)
		else:
			points = nl.get_points(controller)
		if (points is not None):
			ld = points.flatten()
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
			if (full_hand == False):
				df = nl.data_to_simple_df(myo_data, leap_data)
			else:
				df = nl.data_to_bones_df(myo_data, leap_data)
			df.to_csv(file_name, index=False)
			print("CSV Saved", file_name)

# -------- Main Program Loop -----------
if __name__ == '__main__':
	p = multiprocessing.Process(target=data_worker)
	p.start()