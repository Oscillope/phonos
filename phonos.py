import rotary
import soco
import time

try:
    import config as cfg
except ImportError:
    import sys
    print("You need a config.py!")
    sys.exit(-1)

state = "zone"
zp = soco.discovery.any_soco()

def cb(value):
    global state
    global zp
    if (state == "zone"):
        if (value >= 10):
            zp.partymode()
            state = "music"
            return
        for i, zone in enumerate(soco.discovery.discover()):
            if (i == value - 1):
                zp = zone
                zp.unjoin()
                print("Room: " + zp.player_name)
                state = "music"
                return
        print("Invalid zone selection")
    elif (state == "music"):
        try:
            zp.play_uri(cfg.uris[value - 1].uri)
            print("Playing " + cfg.uris[value - 1].name)
            state = "volume"
        except IndexError:
            print("Invalid music selection")
    elif (state == "volume"):
        if (value >= 10):
            state = "music"
            return
        for member in zp.group:
            member.volume = value * 10
        print("Volume: " + str(value * 10))
    else:
        print("Invalid state")
        state = "zone"

def hook_cb(value):
    global state
    global zp
    if (value):
        try:
            zp.play()
        except soco.exceptions.SoCoUPnPException:
            pass
        state = "volume"
        print("Play, go to volume state")
    else:
        try:
            zp.pause()
        except soco.exceptions.SoCoUPnPException:
            pass
        state = "zone"
        print("Pause, reset state")

phone = rotary.Rotary(18, 16, 22, cb, hook_cb)

phone.start()

print("Phonos ready. Rooms:")
for i, zone in enumerate(soco.discovery.discover()):
    print(str(i) + ": " + zone.player_name)
print("\nPresets:")
for i, preset in enumerate(cfg.uris):
    print(str(i) + ": " + preset.name)

phone.join()
