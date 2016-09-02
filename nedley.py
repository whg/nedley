import socket
import threading
import SocketServer
from OSC import OSCServer, OSCClient, OSCMessage
from array import array
import time
from neopixel import *
import netifaces as ni

LED_COUNT      = 300      # Number of LED pixels.
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
machine_ip = ni.ifaddresses('eth0')[2][0]['addr']
server = None


def set_led_data(path, tags, args, source):
        global led_data
        global last_update
	
        last_update = time.clock()
	data = args
        
        with lock:
                to_index = min( len( data ), len( led_data ) )
                led_data[:to_index] = data

	
def send_beacon():
	global machine_ip

	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

	msg = OSCMessage( '/beacon', [ socket.gethostname(), machine_ip ] )
	sock.sendto(msg.getBinary(), ('255.255.255.255', 45454))

	print 'sent beacon'

def run_server():
        global server
        while server:
                server.handle_request()
        
if __name__ == '__main__':

	HOST, PORT = '0.0.0.0', 44448

	server = OSCServer( (HOST, PORT) )
	server.addMsgHandler( '/data', set_led_data )

        server_thread = threading.Thread( target=run_server )
#        server_thread.daemon = True
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
	
			# if time.clock() - last_update > 1 and frame_count % 60 == 0:
			# 	send_beacon()

			time.sleep(1.0 / FRAME_RATE)
			
	except KeyboardInterrupt:
		print 'exiting'
		pass


	for i in range(LED_COUNT):
		strip.setPixelColor(i, 0)
	strip.show()

	server.close()
        server = None
        time.sleep(0.5)
        print 'done'
	
