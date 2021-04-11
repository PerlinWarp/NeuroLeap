# Alternate BluePy Myo
import struct
import multiprocessing

from bluepy import btle

class Handle:
	BATTERY = 0x11
	FIRMWARE = 0x17
	IMU = 0x1c
	CLASSIFIER = 0x23
	EMG_FILT = 0x27
	EMG0 = 0x2b
	EMG1 = 0x2e
	EMG2 = 0x31
	EMG3 = 0x34

class Connection(btle.Peripheral):
	def __init__(self, mac):
		btle.Peripheral.__init__(self, mac)	

		# Subscribe to EMG Channels
		self.writeCharacteristic(0x28, struct.pack('<bb', 0x01, 0x00),True)
		self.writeCharacteristic(0x19, struct.pack('<bbbbb', 1,1,1,3,1) ,True )

		# Tell the Myo not to sleep, otherwise it disconnects after 30
		self.writeCharacteristic(0x19, struct.pack('<3B', 9, 1, 1), True)

	def vibrate(self, length):
		self.writeCharacteristic(0x19, struct.pack('<bbb', 0x03, 0x01, length),True)

	def set_leds(self, logo, line):
		self.writeCharacteristic(0x19, struct.pack('<8B', 6, 6, *(logo + line)))

class MyoDelegate(btle.DefaultDelegate):
	def __init__(self, q):
		btle.DefaultDelegate.__init__(self)
		self.q = q

	def handleNotification(self, cHandle, data):
		if (cHandle == Handle.EMG_FILT):
			data = struct.unpack('<8H', data[:16])
			# Add EMG data to the Queue
			self.q.put(data)

def myo_worker(q, mac_addr = 'c2:19:f0:35:28:5d'):
	p = Connection(mac_addr)
	p.setDelegate(MyoDelegate(q))

	p.vibrate(1)
	p.vibrate(1)
	p.vibrate(1)

	p.set_leds([64, 0, 255], [64, 0, 255])

	while True:
		try:
			'''
			Blocks until a notification is received from the peripheral, or until the given timeout (in seconds) 
			has elapsed. If a notification is received, the delegate object’s handleNotification() method will be called, and waitForNotifications() will then return True.
			If nothing is received before the timeout elapses, this will return False.
			'''

			if p.waitForNotifications(1.0):
				continue
			print("waiting...")
		except btle.BTLEException:
			print("Disconnected")

if __name__ == '__main__':
	q = multiprocessing.Queue()
	p = multiprocessing.Process(target=myo_worker, args=(q,))
	p.start()

	while True:
		try:
			while not(q.empty()):
					# Get the new data from the Myo queue
					emg = list(q.get())
					print(emg)
		except KeyboardInterrupt:
			print("Quitting")
			quit()