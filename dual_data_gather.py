# Gather data from 2 seperate Myos
import time
import multiprocessing

import pandas as pd

import blue_myo
from myo_raw import MyoRaw

file_name = "dual_emg.csv"
PLOT = True

# For BlueMyo
mac1 = "de:36:7a:87:63:be" # First Bought, Right 117 237 250 237 175 59 235 118 222
mac2 = "c2:19:f0:35:28:5d" # Second Bought, Left 115 109 125 127 77 249 219 206 93

# For MyoRaw
addr1 = [190, 99, 135, 122, 54, 222] # First Bought, Right
addr2 = [93, 40, 53, 240, 25, 194] # Second Bought, Left

# Start First Myo (Blue_Myo)
b_q = multiprocessing.Queue()
b_p = multiprocessing.Process(target=blue_myo.myo_worker, args=(b_q,mac1,))
b_p.start()

# Wait until it connects
time.sleep(5)

# Start Second Myo
q = multiprocessing.Queue()

m = MyoRaw(raw=False, filtered=True)
m.connect(addr2)

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
p = multiprocessing.Process(target=worker, args=(q,))
p.start()

# Now both are connected we can start the speedtest.
start_time = time.time()

myo_blue_data = []
myo_raw_data = []

myo_blue_started = False
myo_raw_started = False

# -------- Main Program Loop -----------
# Get data from Myos
try:
	print("Waiting for both to connect.")
	# Wait to get data from both Myos to know they are connected
	q.get() # Block until q has an item
 	# Myo raw usually takes longer, wait for that first.
	b_q.get()
	print("Both should be connected")

	# Empty both queues once
	while ( (not b_q.empty()) or (not q.empty()) ):
		if ((not q.empty())): q.get()
		if (not b_q.empty()): b_q.get()

	# Both devices should now be reporting data, and be empty 

	while True:
		# Get data from the first Myo
		while not(b_q.empty()):
			# Get the new data from the Myo queue
			emg = list(b_q.get())
			#print('Myo 1', emg)
			myo_blue_data.append(emg)

		# Get data from the second Myo
		while not(q.empty()):
			# Get the new data from the Myo queue
			emg = list(q.get())
			#print('Myo 2', emg)
			myo_raw_data.append(emg)

except KeyboardInterrupt:
	end_time = time.time()
	print(f"Quitting, after {end_time} seconds.")
	m.set_leds([255, 0, 64], [255, 0, 64])
	m.disconnect()

	print('Saving')
	print(f"Blue Myo {len(myo_blue_data)}")
	print(f"Raw Myo {len(myo_raw_data)}")

	myo1_cols = ["Channel_1", "Channel_2", "Channel_3", "Channel_4", "Channel_5", "Channel_6", "Channel_7", "Channel_8"]
	myo2_cols = ["Channel_9", "Channel_10", "Channel_11", "Channel_12", "Channel_13", "Channel_14", "Channel_15", "Channel_16"]

	myo1_df = pd.DataFrame(myo_blue_data, columns=myo1_cols)
	myo2_df = pd.DataFrame(myo_raw_data, columns=myo2_cols)

	df = myo1_df.join(myo2_df)
	df.to_csv(file_name, index=False)
	print("CSV Saved", file_name)
