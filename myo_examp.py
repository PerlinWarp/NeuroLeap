import pygame
import multiprocessing

from myo_raw import MyoRaw
import common as c

pygame.init()

carryOn = True

# The clock will be used to control how fast the screen updates
clock = pygame.time.Clock()

# ------------ Myo Setup ---------------
q = multiprocessing.Queue()

m = MyoRaw(raw=False, filtered=True)
m.connect()

def worker(q):
	def add_to_queue(emg, movement):
		q.put(emg)

	m.add_emg_handler(add_to_queue)

	"""worker function"""
	while carryOn:
		m.run(1)
	print("Worker Stopped")

def print_battery(bat):
	print("Battery level:", bat)

m.add_battery_handler(print_battery)

 # Orange logo and bar LEDs
m.set_leds([128, 0, 0], [128, 0, 0])
# Vibrate to know we connected okay
m.vibrate(1)

# -------- Main Program Loop -----------
p = multiprocessing.Process(target=worker, args=(q,))
p.start()

# Setup Myo plotting
# Open a new window
size = (c.WIN_X, c.WIN_Y)
pygame.display.set_caption("Myo Data")
scr = pygame.display.set_mode((c.WIN_X, c.WIN_Y))

last_vals = None
def plot(scr, vals):
    DRAW_LINES = True

    global last_vals
    if last_vals is None:
        last_vals = vals
        return

    D = 5
    scr.scroll(-D)
    scr.fill((0, 0, 0), (c.WIN_X - D, 0, c.WIN_X, c.WIN_Y))
    for i, (u, v) in enumerate(zip(last_vals, vals)):
        if DRAW_LINES:
            pygame.draw.line(scr, (0, 255, 0),
                             (c.WIN_X - D, int(c.WIN_Y/9 * (i+1 - u))),
                             (c.WIN_X, int(c.WIN_Y/9 * (i+1 - v))))
            pygame.draw.line(scr, (255, 255, 255),
                             (c.WIN_X - D, int(c.WIN_Y/9 * (i+1))),
                             (c.WIN_X, int(c.WIN_Y/9 * (i+1))))
        else:
            ca = int(255 * max(0, min(1, v)))
            scr.fill((ca, ca, ca), (c.WIN_X - D, i * c.WIN_Y / 8, D, (i + 1) * c.WIN_Y / 8 - i * c.WIN_Y / 8))

    pygame.display.flip()
    last_vals = vals

try:
    while carryOn:

    	while not(q.empty()):
    		# Get the new data from the Myo queue
    		emg = list(q.get())
    		plot(scr, [e / 500. for e in emg])
    		print(emg)




    	# --- Go ahead and update the screen with what we've drawn.
    	pygame.display.flip()

    	# --- Limit to 60 frames per second
    	clock.tick(60)

    # Once we have exited the main program loop we can stop the game engine:
    pygame.quit()
except KeyboardInterrupt:
    pygame.quit()
    quit()