#!/usr/bin/env python

import numpy as np
import cv2

from anal import macRun, raspberryRun
from bluedick import *
from oral import *

def track_some_shit(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    current_time = time.time()

    robot1.update(hsv, current_time)
    robot1.draw(frame)

    return

    global mask, next_move_time
    if track_window is None:
        return

    back_proj = cv2.calcBackProject([hsv], [0], roi_hist, [0, 180], 1)

    # apply meanshift to get the new location
    ret, track_window = cv2.meanShift(back_proj, track_window, TERM_CRIT)

    # Draw it on image
    x, y, w, h = track_window
    # cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
    mask[y:y+h, x:x+w] = 255
    # pts = np.int0(cv2.cv.BoxPoints(ret))
    # cv2.polylines(frame, [pts], True, (0, 255, 0), 2)
    # cv2.imshow(WINDOW_TITLE, cv2.bitwise_and(frame, frame, mask=mask))\

    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 255), 2)
    return track_window
    
    robot0.draw(frame)
    robot1.draw(frame)

    robot0.update_pos(x + w/2, y + h/2)
    if (current_time > next_move_time):
        print "Making Move..."
        robot0.make_move(target)
        next_move_time = current_time + MOVE_TIME_DELTA
    cv2.rectangle(frame, (robot0.old_x-w/2, robot0.old_y-h/2),
                         (robot0.old_x+w/2, robot0.old_y+h/2), (0, 255, 255), 2)
    cv2.rectangle(frame, (robot0.x-w/2, robot0.y-h/2), (robot0.x+w/2, robot0.y+h/2), (0, 255, 0), 2)
    
    return track_window

next_move_time = 0
MOVE_TIME_DELTA = 1

mask = np.zeros((480, 640), np.uint8)
# Setup the termination criteria, either 10 iterations or move by at least 1 pt
TERM_CRIT = ( cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1 )    

def on_click(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        if state.state == 0 or state.state == 3:
            p1.x = x
            p1.y = y
            state.state += 1
            print p1.x, p1.y
        elif state.state == 1 or state.state == 4:
            p2.x = x
            p2.y = y
            state.state += 1
            print p2.x, p2.y
        elif state.state > 4:
            state.target.x = x
            state.target.y = y
    elif event == cv2.EVENT_LBUTTONUP:
        pass

def keyboard_cmds():
    key = chr(cv2.waitKey(1) & 0xff)
    if key == '0':
        robot0.stop()
        state.selected_robot = robot0
        state.state = 0
    elif key == '1':
        robot1.stop()
        state.selected_robot = robot1
        state.state = 0
    elif key == 's':
        which = cv2.waitKey(0)
        if which == '0':
            robot0.stop()
        elif which == '1':
            robot1.stop()

def step(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    keyboard_cmds()
        
    if state.state == 2:
        state.selected_robot.set_front_box(p1, p2, frame)
        state.state = 3
    if state.state == 5:
        state.selected_robot.set_back_box(p1, p2, frame) 
        state.state = 6

    if state.state < 6:
        robot1.draw(frame)
    else:
    	track_some_shit(frame)
    
    cv2.rectangle(frame, (state.target.x-5, state.target.y-5),
                         (state.target.x+5, state.target.y+5), (0, 0, 255), 2)
    cv2.imshow(WINDOW_TITLE, frame)

def run():
    cv2.namedWindow(WINDOW_TITLE)
    cv2.setMouseCallback(WINDOW_TITLE, on_click)
    state.selected_robot = robot1
    raspberryRun(step)

if __name__ == "__main__":
    run()
