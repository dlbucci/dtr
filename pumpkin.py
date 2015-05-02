#!/usr/bin/env python

import numpy as np
import cv2

from anal import macRun, raspberryRun
from debug import setup_settings_window
from oral import *
from robot import *
from robot_settings import RobotSettingsWindow

def track_some_shit(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    current_time = time.time()
    
    robot0.update(hsv, current_time)
    robot0.draw(frame)

    robot1.update(hsv, current_time)
    robot1.draw(frame)

def on_click(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print state.state
        if state.state == State.AWAITING_CLICK and state.callback:
            state.callback(x, y, state.last_hsv)
            state.state = State.IDLE
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
        elif state.state == State.IDLE:
            state.target.x = x
            state.target.y = y

def keyboard_cmds(frame):
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
    elif key == 'h':
        robot0.set_hists(frame)
        robot1.set_hists(frame)

def step(frame):
    #cv2.imshow(WINDOW_TITLE, frame)
    #return

    state.last_frame = frame
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    state.last_hsv = hsv
    keyboard_cmds(frame)

    if state.view == 1:
        mask = cv2.inRange(hsv, np.array((robot0.front_hue.min_hue, 0., 0.)),
                                np.array((robot0.front_hue.max_hue, 255., 255,)))
        hsv = cv2.bitwise_and(hsv, hsv, mask=mask)
        cv2.imshow(WINDOW_TITLE, cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR))
        return
    elif state.view == 2:
        mask = cv2.inRange(hsv, np.array((robot0.back_hue.min_hue, 0., 0.)),
                                np.array((robot0.back_hue.max_hue, 255., 255,)))
        hsv = cv2.bitwise_and(hsv, hsv, mask=mask)
        cv2.imshow(WINDOW_TITLE, cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR))
        return 
    elif state.view == 3:
        mask = cv2.inRange(hsv, np.array((robot1.front_hue.min_hue, 0., 0.)),
                                np.array((robot1.front_hue.max_hue, 255., 255,)))
        hsv = cv2.bitwise_and(hsv, hsv, mask=mask)
        cv2.imshow(WINDOW_TITLE, cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR))
        return
    elif state.view == 4:
        mask = cv2.inRange(hsv, np.array((robot1.back_hue.min_hue, 0., 0.)),
                                np.array((robot1.back_hue.max_hue, 255., 255,)))
        hsv = cv2.bitwise_and(hsv, hsv, mask=mask)
        cv2.imshow(WINDOW_TITLE, cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR))
        return 
        
    if state.state == 1:
        state.selected_robot.set_front_box_2(p1, hsv)
        state.state = 3
    if state.state == 4:
        state.selected_robot.set_back_box_2(p1, hsv) 
        state.state = 6

    if state.state < 6:
        robot0.draw(frame)
        robot1.draw(frame)
    else:
    	track_some_shit(frame)
    
    cv2.circle(frame, (state.target.x, state.target.y), state.target_radius,
               TARGET_CIRCLE_COLOR, TARGET_CIRCLE_THICKNESS)
    cv2.imshow(WINDOW_TITLE, frame)

def setup_window(): 
    setup_settings_window()
    RobotSettingsWindow(robot0)
    RobotSettingsWindow(robot1)
    cv2.namedWindow(WINDOW_TITLE)
    cv2.setMouseCallback(WINDOW_TITLE, on_click)

def main():
    """
    runs the program by setting up the window and calling
    the appropriate run function for the platform it's on
    """
    setup_window()
    state.selected_robot = robot1
    #macRun(step)
    raspberryRun(step)

mask = np.zeros((480, 640), np.uint8)

if __name__ == "__main__":
    main()
