from time import sleep, time
from tqdm import tqdm

trials = 10
gestures = ['Thumb curl in', 'Index curl', 'Middle curl', 'Ring curl', 'Pinky curl',
			 'Close fist']
gesture_time = 3
print("Waiting to start")
for s in tqdm(range(10)):
			sleep(1)

for t in range(trials):
	print()
	for gesture in gestures:
		print(gesture)
		# Sleep for gesture time seconds, and display progress
		for s in tqdm(range(gesture_time*10)):
			# Slowly make that gesture
			sleep(0.1)
		print("Return to resting")
		for s in tqdm(range(gesture_time*10)):
			# Slowly return to resting
			sleep(0.1)
	print(f"Trial {t} done")
	print("Resting")
	for s in tqdm(range(gesture_time*10)):
		sleep(0.1)
print("Done")