from rpi_ws281x import *
import threading
import math
from time import sleep

# These are the defaults
#LED_COUNT       = 5
#LED_PIN         = 18
#LED_CHANNEL     = 0
#LED_FREQ_HZ     = 800000
#LED_DMA         = 10
#LED_BRIGHTNESS  = 255
#LED_INVERT      = False

# RGB/HSV stuff from http://code.activestate.com/recipes/576919-python-rgb-and-hsv-conversion/
def hsv2rgb(h, s, v):
    h = float(h)
    s = float(s)
    v = float(v)
    h60 = h / 60.0
    h60f = math.floor(h60)
    hi = int(h60f) % 6
    f = h60 - h60f
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    r, g, b = 0, 0, 0
    if hi == 0: r, g, b = v, t, p
    elif hi == 1: r, g, b = q, v, p
    elif hi == 2: r, g, b = p, v, t
    elif hi == 3: r, g, b = p, q, v
    elif hi == 4: r, g, b = t, p, v
    elif hi == 5: r, g, b = v, p, q
    r, g, b = int(r * 255), int(g * 255), int(b * 255)
    return r, g, b

def rgb2hsv(r, g, b):
    r, g, b = r/255.0, g/255.0, b/255.0
    mx = max(r, g, b)
    mn = min(r, g, b)
    df = mx-mn
    if mx == mn:
        h = 0
    elif mx == r:
        h = (60 * ((g-b)/df) + 360) % 360
    elif mx == g:
        h = (60 * ((b-r)/df) + 120) % 360
    elif mx == b:
        h = (60 * ((r-g)/df) + 240) % 360
    if mx == 0:
        s = 0
    else:
        s = df/mx
    v = mx
    return h, s, v

class Leds (threading.Thread):
    def __init__(self, pin, count):
        threading.Thread.__init__(self)
        self.strip = Adafruit_NeoPixel(count, pin)
        self.stop_thread = False
        self.num_steps = 16
        self.state = "off"
        self.color = (0, 183, 255)
        self.cond = threading.Condition()
        self.__states = {
            "off" : self.stateOff,
            "waiting" : self.stateWait,
            "playing" : self.statePlay,
        }
        self.strip.begin()

    def run(self):
        while (not self.stop_thread):
            self.cond.acquire()
            self.cond.wait()
            self.__states[self.state](self.color)
            self.cond.release()

    def kill(self):
        self.running = False
        self.stop_thread = True
        self.cond.acquire()
        self.cond.notifyAll()
        self.cond.release()

    def stop(self):
        self.running = False

    def startWait(self, color):
        self.running = False
        self.cond.acquire()
        self.running = True
        self.color = color
        self.state = "waiting"
        self.cond.notifyAll()
        self.cond.release()


    def startPlay(self, color):
        self.running = False
        self.cond.acquire()
        self.running = True
        self.color = color
        self.state = "playing"
        self.cond.notifyAll()
        self.cond.release()

    def startOff(self):
        self.running = False
        self.cond.acquire()
        self.state = "off"
        self.cond.notifyAll()
        self.cond.release()

    def stateOff(self, color):
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColorRGB(i, 0, 0, 0)
        self.strip.show()

    def stateWait(self, color):
        while self.running:
            for j in range(128):
                for i in range(self.strip.numPixels()):
                    tail = j / 128
                    red = int(color[0] * tail)
                    green = int(color[1] * tail)
                    blue = int(color[2] * tail)
                    self.strip.setPixelColorRGB(i, red, green, blue)
                self.strip.show()
                sleep(0.01)
                if not self.running: return
            for j in range(128, 0, -1):
                for i in range(self.strip.numPixels()):
                    tail = j / 128
                    red = int(color[0] * tail)
                    green = int(color[1] * tail)
                    blue = int(color[2] * tail)
                    self.strip.setPixelColorRGB(i, red, green, blue)
                self.strip.show()
                sleep(0.01)
                if not self.running: return

    def statePlay(self, color):
        step = 0
        while self.running:
            for i in range(self.strip.numPixels()):
                if (i == step):
                    self.strip.setPixelColorRGB(i, color[0], color[1], color[2])
                else:
                    self.strip.setPixelColorRGB(i, 0, 0, 0)
            step = (step + 1) % self.strip.numPixels()
            self.strip.show()
            sleep(0.5)
