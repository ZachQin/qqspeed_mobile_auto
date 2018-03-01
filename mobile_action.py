import os
import random
import subprocess

def screencap():
    cmd = 'adb shell screencap -p'
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    png_bin = proc.stdout.read()
    return png_bin

def tap_screen(point, duration = 200, loc_tolerance = 20, time_tolerance = 50):
    cmd = 'adb shell input swipe {x1} {y1} {x2} {y2} {duration}'.format(
        x1 = max(point[0] + int(random.uniform(-loc_tolerance, loc_tolerance)), 0),
        y1 = max(point[1] + int(random.uniform(-loc_tolerance, loc_tolerance)), 0),
        x2 = max(point[0] + int(random.uniform(-loc_tolerance, loc_tolerance)), 0),
        y2 = max(point[1] + int(random.uniform(-loc_tolerance, loc_tolerance)), 0),
        duration = max(duration + int(random.uniform(-time_tolerance, time_tolerance)), 1)
    )
    os.system(cmd)
