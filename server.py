import socket
import threading
import SocketServer
from array import array
import time
from neopixel import *

LED_COUNT      = 60      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
FRAME_RATE = 100

led_data = [255 for _ in range(LED_COUNT)]
lock = threading.Lock()
frame_count = 0
last_update = 0

class RequestHandler(SocketServer.BaseRequestHandler):
	def handle(self):
		global led_data
		global last_update
	
		last_update = time.clock()
	
		data_len = 300
		data = self.request[0].strip()#.recv(300)
		print time.clock(), len(data)
		inarray = array('I')
		inarray.fromstring(data)
		with lock:
			led_data = inarray.tolist()

	
def send_beacon():
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
	sock.sendto(socket.gethostname(), ('255.255.255.255', 45454))
	print 'sent beacon'

if __name__ == '__main__':

	HOST, PORT = '0.0.0.0', 44448
	server = SocketServer.UDPServer((HOST, PORT), RequestHandler)
	server_thread = threading.Thread(target=server.serve_forever)
	server_thread.daemon = True
	server_thread.start()
	print 'started server thread'
	
	strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
	strip.begin()

	try:
		while True:
			for i in range(LED_COUNT):
				strip.setPixelColor(i, led_data[i])
			strip.show()
			frame_count+= 1
	
			if time.clock() - last_update > 1 and frame_count % 60 == 0:
				send_beacon()

			time.sleep(1.0 / FRAME_RATE)
			
	except KeyboardInterrupt:
		print 'exiting'
		pass


	for i in range(LED_COUNT):
		strip.setPixelColor(i, 0)
	strip.show()

	server.shutdown()
	server.server_close()
	
	