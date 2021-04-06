# Simplist data recording
'''
The simplict hand tracking model:
	Only record the finger tips. / finger-palm angle etc etc etc 
	Only records a sample from the leap when there is a new myo sample. 
	Use the 50Hz Myo mode.
'''
import time

import numpy as np
import pandas as pd
import Leap
from myo_raw import MyoRaw

collect = False
SECONDS = 15
file_name = "thumb_move.csv"

# ------------ Leap Setup ---------------
leap_data = []

controller = Leap.Controller()
controller.set_policy_flags(Leap.Controller.POLICY_BACKGROUND_FRAMES)

def get_points():
	frame = controller.frame()
	hand = frame.hands.rightmost
	if not hand.is_valid: return [0]*6
	fingers = hand.fingers
	X = [finger.stabilized_tip_position.x for finger in fingers]
	X.append(hand.palm_position.x)
	Y = [finger.stabilized_tip_position.y for finger in fingers]
	Y.append(hand.palm_position.y)
	Z = [finger.stabilized_tip_position.z for finger in fingers]
	Z.append(hand.palm_position.z)
	return np.array([X, Z, Y])

# ------------ Myo Setup ---------------
m = MyoRaw(raw=False, filtered=True) # 50Hz Filtered Myo data
m.connect()

myo_data = []

def add_to_queue(emg, movement):
	myo_data.append(emg)
	leap_data.append(get_points().flatten())

m.add_emg_handler(add_to_queue)

def print_battery(bat):
	print("Battery level:", bat)

m.add_battery_handler(print_battery)

 # Its go time
m.set_leds([128, 128, 128], [128, 128, 128])
# Vibrate to know we connected okay
m.vibrate(1)

# Wait to start
# m.connect will wait until we get a connection, but the leap doesnt block
while not(collect):
	frame = controller.frame()
	hand = frame.hands.rightmost
	if (hand.palm_position.x != 0):
		collect = True
		print(f"Collection started for {SECONDS} seconds.")

# Start collecing data.
start_time = time.time()

while collect:
	if (time.time() - start_time < SECONDS):
		m.run(1)
	else:
		collect = False
		collection_time = time.time() - start_time
		print("Finished collecting.")
		print(f"Collection time: {collection_time}")
		print(len(myo_data), "myos collected")
		print(len(leap_data), "leaps collected")

		print(myo_data[0])
		print(leap_data[0])

		# Combine the data and record to a df
		myo_cols = ["Channel_1", "Channel_2", "Channel_3", "Channel_4", "Channel_5", "Channel_6", "Channel_7", "Channel_8"]
		leap_cols = []
		finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky', 'Palm']
		# We can of course generate column names on the fly:
		for finger in finger_names:
			for dim in ["x","y","z"]:
					leap_cols.append(f"{finger}_tip_{dim}")
		print(leap_cols)

		myo_df = pd.DataFrame(myo_data, columns=myo_cols)
		leap_df = pd.DataFrame(leap_data, columns=leap_cols)
		print(myo_df.head())
		print(leap_df.head())

		df = myo_df.join(leap_df)
		df.to_csv(file_name, index=False)
