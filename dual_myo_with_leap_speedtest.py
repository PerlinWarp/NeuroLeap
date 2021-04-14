# Dual Myo Speedtest
import time
import multiprocessing

import blue_myo
from myo_raw import MyoRaw

import Leap
import NeuroLeap as nl

PLOT = True
RAW = True


# ------------ Leap Setup ---------------
leap_data = []

controller = Leap.Controller()
controller.set_policy_flags(Leap.Controller.POLICY_BACKGROUND_FRAMES)

# ------------ Myo Setup ---------------
# For BlueMyo
mac1 = "de:36:7a:87:63:be" # First Bought, Right 117 237 250 237 175 59 235 118 222
mac2 = "c2:19:f0:35:28:5d" # Second Bought, Left 115 109 125 127 77 249 219 206 93

# For MyoRaw
addr1 = [190, 99, 135, 122, 54, 222] # First Bought, Right
addr2 = [93, 40, 53, 240, 25, 194] # Second Bought, Left

# Start First Myo (Blue_Myo)
b_q = multiprocessing.Queue()
b_p = multiprocessing.Process(target=blue_myo.myo_worker, args=(b_q,mac1,RAW, ))
b_p.start()

# Wait until it connects
time.sleep(5)

# Start Second Myo
q = multiprocessing.Queue()

m = MyoRaw(raw=RAW, filtered=False)
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

n_points = 50

myo1_data = []
myo2_data = []

myo1_freq = []
myo2_freq = []

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

	# Now both are connected we can start the speedtest.
	start_time = time.time()
	last_n_1 = start_time
	last_n_2 = start_time

	while True:
		points = None

		# Get data from the first Myo
		while not(b_q.empty()):
			# Get the new data from the Myo queue
			emg = list(b_q.get())
			#print('Myo 1', emg)
			myo1_data.append(emg)

			# Time it
			data_points = len(myo1_data)
			if (data_points % n_points == 0):
				time_s = time.time()
				print(f"BM {data_points} points, {n_points} in {time_s-last_n_1}")
				freq = n_points/(time_s-last_n_1)
				print(f"Giving BlueMyo a frequency of {freq} Hz")
				last_n_1 = time.time()
				myo1_freq.append(freq)

		# Get data from the second Myo
		while not(q.empty()):
			# Get the new data from the Myo queue
			emg = list(q.get())
			#print('Myo 2', emg)
			myo2_data.append(emg)

			points = nl.get_points(controller)

			data_points = len(myo2_data)
			if (data_points % n_points == 0):
				time_s = time.time()
				print(f"MR {data_points} points, {n_points} in {time_s-last_n_2}")
				freq = n_points/(time_s-last_n_2)
				print(f"Giving MyoRaw a frequency of {freq} Hz")
				last_n_2 = time.time()
				myo2_freq.append(freq)

		# Check if data was gathered this frame
		if (points is not None):
			ld = points.flatten()
			leap_data.append(ld)

except KeyboardInterrupt:
	print("Quitting")
	m.set_leds([50, 255, 128], [50, 255, 128])
	m.disconnect()

	end_time = time.time()
	print(f"{len(myo1_data)} measurements in {end_time-start_time} seconds.")
	freq = len(myo1_data)/(end_time-start_time)
	print(f"Giving BlueMyo a frequency of {freq} Hz")

	print(f"{len(myo2_data)} measurements in {end_time-start_time} seconds.")
	freq = len(myo2_data)/(end_time-start_time)
	print(f"Giving MyoRaw a frequency of {freq} Hz")

	print(f"{len(leap_data)} measurements in {end_time-start_time} seconds.")
	freq = len(leap_data)/(end_time-start_time)
	print(f"Giving LeapM a frequency of {freq} Hz")


	if (PLOT):
		import numpy as np
		import matplotlib.pyplot as plt
		x_ticks = np.array(range(1, len(myo1_freq)+1)) * n_points

		# Due to syncing, we know the first freq will be incorrect
		myo1_freq.pop(0)
		myo1_freq.pop(1)

		plt.plot(myo1_freq, label="Blue Myo Freq")
		plt.plot(myo2_freq, label = 'Myo Raw Freq')
		plt.legend()
		plt.title("Myo Frequency Plot")
		plt.xlabel(f"Number of values sent, measured every {n_points}")
		plt.ylabel('Frequency')
		plt.show()