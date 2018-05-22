import rotary
import soco
import time

zp = soco.discovery.any_soco()
coord = zp.group.coordinator

def cb(value):
    if value == 10:
        print("Pause!")
        coord.pause()
    if value == 1:
        print("Play!")
        coord.play()

phone = rotary.Rotary("P8_9", "P8_10", cb)

phone.start()

phone.join()
