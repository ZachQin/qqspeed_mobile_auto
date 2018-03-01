import mobile_action
import time
import cv2

def turn_left(duration=500, time_tolerance=100):
    mobile_action.tap_screen((197, 846), duration=duration, loc_tolerance=50, time_tolerance=time_tolerance)

def turn_right(duration=500, time_tolerance=100):
    mobile_action.tap_screen((477, 846), duration=duration, loc_tolerance = 50, time_tolerance = time_tolerance)

def drift(duration=1000, time_tolerance=400):
    mobile_action.tap_screen((1682, 816), duration=duration, loc_tolerance=80, time_tolerance=time_tolerance)

def small_accelerate():
    mobile_action.tap_screen((1453, 702), duration=200, loc_tolerance=30, time_tolerance=100)

def reset():
    mobile_action.tap_screen((97, 528), duration=200, loc_tolerance=20, time_tolerance=100)

def skew_ratio(img):
    MAP_RECT = (1589, 233, 295, 271)
    HEAD_LOC = (1738, 347)
    THRESHOLD = 150

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    binary = cv2.threshold(gray, THRESHOLD, 255, cv2.THRESH_BINARY)[1]
    
    # cv2.imshow('bin', binary)

    left_count = 0
    right_count = 0
    
    x = HEAD_LOC[0]
    while x > MAP_RECT[0] and binary[HEAD_LOC[1], x] == 255:
        left_count += 1
        x -= 1
    
    x = HEAD_LOC[0]
    while x < MAP_RECT[0] + MAP_RECT[2] and binary[HEAD_LOC[1], x] == 255:
        right_count += 1
        x += 1

    if left_count == 0 or right_count == 0:
        return None
    return left_count / (left_count + right_count)

reset_counter = 0

def action(img):
    """在这里填写需要执行的代码"""
    global reset_counter
    ratio = skew_ratio(img)
    if ratio is None:
        reset_counter += 1
        if reset_counter >= 2:
            reset()
            reset_counter = 0
        return
    print('~~~~~###ratio:', str(ratio))
    turn_duration = int(abs(0.5 - ratio) * 1000)
    if 0.4 < ratio < 0.6:
        pass
    elif ratio < 0.5:
        turn_right(duration=turn_duration)
    else:
        turn_left(duration=turn_duration)
    

