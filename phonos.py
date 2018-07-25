import rotary
import soco
import time

try:
    import config as cfg
except ImportError:
    import sys
    print("You need a config.py!")
    sys.exit(-1)

zp = soco.discovery.any_soco()
coord = zp.group.coordinator

def cb(value):
    print(value)
    if value >= 10:
        print("Pause!")
        coord.pause()
    else:
        coord.partymode()
        coord.play_uri(cfg.uris[value - 1])

# These should be strings on BeagleBoard, but numbers on RPi
phone = rotary.Rotary(18, 16, cb)

phone.start()

phone.join()
