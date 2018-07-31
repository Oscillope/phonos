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
        else:
            try:
                zp = zones[value - 1]
                zp.unjoin()
                print("GC: " + zp.player_name)
            except IndexError:
                print("Invalid zone selection")
    elif (state == "music"):
        try:
            zp.play_uri(cfg.uris[value - 1].uri)
            print("Playing " + cfg.uris[value - 1].name)
            state = "volume"
        except IndexError:
            print("Invalid music selection " + str(value))
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
        state = "music"
        print("Group selected, pick some music")
    elif (state == "zone"):
        pass
    else:
        try:
            zp.pause()
        except soco.exceptions.SoCoUPnPException:
            pass
        state = "zone"
        print("Pause, reset state")

phone = rotary.Rotary(18, 16, 22, cb, hook_cb)

phone.start()

print("Phonos ready. Zones:")
for i, zone in enumerate(zones):
    print(str(i+1) + ": " + zone.player_name)
print("\nPresets:")
for i, preset in enumerate(cfg.uris):
    print(str(i+1) + ": " + preset.name)

phone.join()
