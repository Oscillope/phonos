import threading
# Is nesting try statements bad? My brain says yes, but my heart says no.
# This will figure out if we're on a Raspberry Pi, a Beaglebone, or neither.
try:
    import RPi.GPIO as GPIO
    rpi = True
    emulator = False
except ImportError:
    try:
        import Adafruit_BBIO.GPIO as GPIO
        rpi = False
        emulator = False
    except ImportError:
        rpi = False
        emulator = True
from time import sleep
import signal

class Rotary (threading.Thread):
    def __init__(self, latch, count, cb = None):
        threading.Thread.__init__(self)
        self.latch = latch
        self.count = count
        if rpi:
            GPIO.setmode(GPIO.board)
        if not emulator:
            GPIO.setup(self.latch, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(self.count, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        else:
            print("Rotary module in emulator mode")
        self._counter = 0
        self.value = 0
        self.callback = cb
        self.stop_thread = False
        signal.signal(signal.SIGINT, self.sig_handler)

    def run(self):
        while (not self.stop_thread):
            if emulator:
                num = input("Enter a number, or q: ")
                if (num == 'q'):
                    self.stop_thread = True
                else:
                    self._counter = int(num)
            else:
                while (GPIO.input(self.latch) == 0):
                    if (GPIO.input(self.count) == 1):
                        self._counter += 1
                        while (GPIO.input(self.count) == 1):
                            pass # wait for it to go low
            if (self._counter):
                self.value = self._counter
                if (self.callback):
                    self.callback(self.value)
                self._counter = 0
            sleep(0.1)
        print("Exiting rotary phone thread")

    def sig_handler(self, signal, frame):
        print("Caught ctrl-C, exiting...")
        self.stop_thread = True
        if rpi:
            GPIO.cleanup()
