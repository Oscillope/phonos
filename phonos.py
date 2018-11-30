import rotary
import soco
import time
import leds
import signal
from threading import Timer

try:
    import config as cfg
except ImportError:
    import sys
    print("You need a config.py!")
    sys.exit(-1)

state = "zone"
zp = None
zones = list(soco.discovery.discover())

# This is how we transition through the various states:
# Zone -> <zone select> -> <handset up> -> Music -> <music select> -> Volume
# Zone -> <handset up> -> Music
# Any -> <handset down> -> Zone
# Volume -> <dial 0> -> Music

def cb(value):
    global state
    global zp
    if (state == "zone"):
        lights.startWait((255, 133, 0))
        if (value >= 10):
            zp = None
            print("Reset GM")
        elif (value == 9):
            zp.partymode()
        elif zp:
            try:
                zone = zones[value - 1]
                if zone is zp:
                    return
                zone.join(zp)
                print("GM: " + zone.player_name)
            except IndexError:
                print("Invalid zone selection")
        elif (value > len(cfg.rooms)):
            print("Invalid zone selection " + str(value))
            lights.startErr()
            return
        else:
            try:
                zp = zones[value - 1]
                zp.unjoin()
                print("GC: " + zp.player_name)
            except IndexError:
                print("Invalid zone selection")
        state = "music"
        lights.startWait((0, 255, 100))
    elif (state == "music"):
        try:
            zp.play_uri(cfg.uris[value - 1].uri)
            print("Playing " + cfg.uris[value - 1].name)
            state = "volume"
            lights.startPlay((0, 148, 255))
        except IndexError:
            print("Invalid music selection " + str(value))
            lights.startErr()
    elif (state == "volume"):
        if (value >= 10):
            state = "music"
            lights.startWait((0, 255, 100))
            return
        for member in zp.group:
            member.volume = value * 10
        print("Volume: " + str(value * 10))
    else:
        print("Invalid state")
        lights.startErr()
        state = "zone"

def hook_cb(value):
    global state
    global zp
    if (value):
        if (state == "volume"):
            return # Avoid double-play
        try:
            zp.play()
            lights.startPlay((0, 200, 255))
        except soco.exceptions.SoCoUPnPException:
            pass
        state = "music"
        print("Group selected, pick some music")
    elif (state == "zone"):
        pass
    else:
        if (state == "zone"):
            return # Avoid double-pause
        try:
            zp.pause()
            lights.startOff()
        except soco.exceptions.SoCoUPnPException:
            pass
        state = "zone"
        print("Pause, reset state")

def sig_handler(signal, frame):
    print("Caught signal " + str(signal) + ", exiting...")
    phone.stop_thread = True
    phone.join()
    lights.kill()
    lights.join()

phone = rotary.Rotary(18, 16, 22, cb, hook_cb)
lights = leds.Leds(18, 5)

signal.signal(signal.SIGINT, sig_handler)
signal.signal(signal.SIGTERM, sig_handler)
phone.start()
lights.start()
lights.startOff()

print("Phonos ready. Zones:")
for i, zone in enumerate(zones):
    print(str(i+1) + ": " + zone.player_name)
print("\nPresets:")
for i, preset in enumerate(cfg.uris):
    print(str(i+1) + ": " + preset.name)
