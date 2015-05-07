#!/usr/bin/env python

import atexit
import multiprocessing as mp
import Queue

from camera import macRun, raspberryRun
import cv2
import numpy as np

from settings import GeneralSettingsFrame
from state import *
from robot import *
from robot_settings import RobotSettingsWindow

# hack
from PIL import Image, ImageTk

def track_some_shit(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    current_time = time.time()
    
    robot0.update(hsv, current_time)
    robot0.draw(frame)

    robot1.update(hsv, current_time)
    robot1.draw(frame)

def on_click(event, x, y, flags, param):
    print x, y
    if event == cv2.EVENT_LBUTTONDOWN:
        current_state = state.state.get()
        if current_state == State.AWAITING_CLICK and state.callback:
            state.callback(x, y, state.last_hsv)
            state.state.set(State.IDLE)
        elif current_state == 0 or current_state == 3:
            p1.x = x
            p1.y = y
            state.state.set(current_state + 1)
            print p1.x, p1.y
        elif current_state == 1 or current_state == 4:
            p2.x = x
            p2.y = y
            state.state.set(current_state + 1)
            print p2.x, p2.y
        elif current_state == State.IDLE:
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

def step(queue, image_label):
    frame = queue.get()
    queue.put("next")

    state.last_frame = frame
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    state.last_hsv = hsv
    keyboard_cmds(frame)

    view = state.view.get()

    if view == 1:
        mask = cv2.inRange(hsv, np.array((robot0.front_hue.min_hue.get(), 0., 0.)),
                                np.array((robot0.front_hue.max_hue.get(), 255., 255,)))
        hsv = cv2.bitwise_and(hsv, hsv, mask=mask)
        cv2.imshow(WINDOW_TITLE, cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR))
    elif view == 2:
        mask = cv2.inRange(hsv, np.array((robot0.back_hue.min_hue.get(), 0., 0.)),
                                np.array((robot0.back_hue.max_hue.get(), 255., 255,)))
        hsv = cv2.bitwise_and(hsv, hsv, mask=mask)
        cv2.imshow(WINDOW_TITLE, cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR))
    elif view == 3:
        mask = cv2.inRange(hsv, np.array((robot1.front_hue.min_hue.get(), 0., 0.)),
                                np.array((robot1.front_hue.max_hue.get(), 255., 255,)))
        hsv = cv2.bitwise_and(hsv, hsv, mask=mask)
        cv2.imshow(WINDOW_TITLE, cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR))
    elif view == 4:
        mask = cv2.inRange(hsv, np.array((robot1.back_hue.min_hue.get(), 0., 0.)),
                                np.array((robot1.back_hue.max_hue.get(), 255., 255,)))
        hsv = cv2.bitwise_and(hsv, hsv, mask=mask)
        cv2.imshow(WINDOW_TITLE, cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR))
    else:
        current_state = state.state.get()
        if current_state == 1:
            state.selected_robot.set_front_box_2(p1, hsv)
            state.state.set(3)
        if current_state == 4:
            state.selected_robot.set_back_box_2(p1, hsv) 
            state.state.set(6)

        if current_state < 6:
            robot0.draw(frame)
            robot1.draw(frame)
        else:
            track_some_shit(frame)
        
        cv2.circle(frame, (state.target.x, state.target.y), state.target_radius.get(),
                   TARGET_CIRCLE_COLOR, TARGET_CIRCLE_THICKNESS)
        
        cv2.imshow(WINDOW_TITLE, frame)

    root.update()
    root.after(0, func=lambda: step(queue, image_label))

def setup_window():
    GeneralSettingsFrame(root)
    RobotSettingsWindow(root, robot0)
    RobotSettingsWindow(root, robot1)
    cv2.namedWindow(WINDOW_TITLE)
    cv2.setMouseCallback(WINDOW_TITLE, on_click)

def main():
    """
    runs the program by setting up the window and calling
    the appropriate run function for the platform it's on
    """
    root.title("Dicks on Parade")
    setup_window()

    image_label = Label(root)
    image_label.pack(side="right")

    queue = mp.Queue()
    camera_process = mp.Process(target=raspberryRun, args=(queue,))
    camera_process.start()
    atexit.register(camera_process.terminate)

    root.after(0, func=lambda: step(queue, image_label))
    root.mainloop()
    root.destroy()

mask = np.zeros((480, 640), np.uint8)

if __name__ == "__main__":
    main()
