# Predict from the live data
#from keras.models import load_model

import time
import multiprocessing

import numpy as np
from myo_raw import MyoRaw

m = MyoRaw(raw=False, filtered=True) # 50Hz Filtered Myo data
m.connect()

def get_data(shared_arr):

	# ------------ Myo Setup ---------------
	myo_data = []

	def add_to_queue(emg, movement):
		myo_data.append(emg)
		for i in range(8):
			shared_arr[i] = emg[i]

	m.add_emg_handler(add_to_queue)

	def print_battery(bat):
		print("Battery level:", bat)

	m.add_battery_handler(print_battery)

	 # Its go time
	m.set_leds([128, 128, 0], [128, 128, 0])
	# Vibrate to know we connected okay
	m.vibrate(1)

	# Wait to start
	# m.connect will wait until we get a connection, but the leap doesnt block
	while (True):
			m.run(1)

# -------- Main Program Loop -----------
if __name__ == '__main__':
	myo_arr = multiprocessing.Array('d', range(8))
	p = multiprocessing.Process(target=get_data, args=(myo_arr,))
	p.start()

	myo_data = np.frombuffer(myo_arr.get_obj())

	# Load the keras model
	#model = load_model('BenchmarkNN.h5')

	while (True):
		myo_data = np.frombuffer(myo_arr.get_obj())
		print(myo_data)