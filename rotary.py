import threading
from time import sleep
try:
    import RPi.GPIO as GPIO
    emulator = False
except ImportError:
    emulator = True

class Rotary (threading.Thread):
    def __init__(self, latch, count, hook, cb = None, hook_cb = None):
        threading.Thread.__init__(self)
        self.latch = latch
        self.count = count
        self.hook = hook
        if not emulator:
            GPIO.setmode(GPIO.BOARD)
            GPIO.setup(self.latch, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(self.count, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(self.hook, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(self.count, GPIO.RISING, bouncetime=80)
            if hook_cb:
                GPIO.add_event_detect(self.hook, GPIO.BOTH, callback=self._hook_cb, bouncetime=500)
                self.hook_cb = hook_cb
        else:
            print("Rotary module in emulator mode")
            self.hook_cb = hook_cb
        self._counter = 0
        self.value = 0
        self.callback = cb
        self.stop_thread = False

    def run(self):
        while (not self.stop_thread):
            if emulator:
                num = input("Enter a number, or q: ")
                if (num == 'q'):
                    self.stop_thread = True
                elif (num == 'h'):
                    if self.hook_cb:
                        self.hook_cb()
                else:
                    self._counter = int(num)
            else:
                while (GPIO.input(self.latch) == 0):
                    if (GPIO.event_detected(self.count)):
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
        if not emulator:
            GPIO.cleanup()

    def _hook_cb(self, pin):
        if (GPIO.input(pin)):
            self.hook_cb(True)
        else:
            self.hook_cb(False)

