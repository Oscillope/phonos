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
    coord.partymode()
    if value == 10:
        print("Pause!")
        coord.pause()
    else:
        coord.play_uri(cfg.uris[value])

# These are BeagleBoard-formatted pins.
phone = rotary.Rotary("P8_9", "P8_10", cb)

phone.start()

phone.join()
