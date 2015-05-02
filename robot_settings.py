#!/usr/bin/env python

import cv2
import numpy as np
from oral import *
from robot import *

WINDOW_FMT = "%s Settings"

RUN_ROBOT = "Run Robot:"
PICK_CIRCLES = "Pick Circles:"
LEFT_MOTOR = "Left Motor Speed:"
RIGHT_MOTOR = "Right Motor Speed:"
SET_FRONT_HUE = "Set Front Hue:"
FRONT_MIN_HUE = "Front Min Hue:"
FRONT_MAX_HUE = "Front Max Hue:"
SET_BACK_HUE = "Set Back Hue:"
BACK_MIN_HUE = "Back Min Hue:"
BACK_MAX_HUE = "Back Max Hue:"
MIN_RANGE = 1

class RobotSettingsWindow(object):
    def __init__(self, robot):
        self.robot = robot
        self.WINDOW = WINDOW_FMT % robot.name
        cv2.namedWindow(self.WINDOW)

        cv2.createTrackbar(RUN_ROBOT, self.WINDOW, 0, 1, self.run_robot)

        cv2.createTrackbar(LEFT_MOTOR, self.WINDOW, 0, 255, self.left_motor)
        cv2.setTrackbarPos(LEFT_MOTOR, self.WINDOW, robot.left_motor)
        cv2.createTrackbar(RIGHT_MOTOR, self.WINDOW, 0, 255, self.right_motor)
        cv2.setTrackbarPos(RIGHT_MOTOR, self.WINDOW, robot.right_motor)

        cv2.createTrackbar(PICK_CIRCLES, self.WINDOW, 0, 1, self.pick_circles)
    
        cv2.createTrackbar(SET_FRONT_HUE, self.WINDOW, 0, 1, self.set_front_hue)
        cv2.createTrackbar(FRONT_MIN_HUE, self.WINDOW, 0, 180, 
            lambda x: self.set_min_hue(FRONT_MIN_HUE, robot.front_hue, x))
        cv2.createTrackbar(FRONT_MAX_HUE, self.WINDOW, 0, 180,
            lambda x: self.set_max_hue(FRONT_MAX_HUE, robot.front_hue, x))

        cv2.createTrackbar(SET_BACK_HUE, self.WINDOW, 0, 1, self.set_back_hue)
        cv2.createTrackbar(BACK_MIN_HUE, self.WINDOW, 0, 180,
            lambda x: self.set_min_hue(BACK_MIN_HUE, robot.back_hue, x))
        cv2.createTrackbar(BACK_MAX_HUE, self.WINDOW, 0, 180,
            lambda x: self.set_max_hue(BACK_MAX_HUE, robot.back_hue, x))

        cv2.setTrackbarPos(FRONT_MIN_HUE, self.WINDOW, robot.front_hue.min_hue)
        cv2.setTrackbarPos(FRONT_MAX_HUE, self.WINDOW, robot.front_hue.max_hue)
        cv2.setTrackbarPos(BACK_MIN_HUE, self.WINDOW, robot.back_hue.min_hue)
        cv2.setTrackbarPos(BACK_MAX_HUE, self.WINDOW, robot.back_hue.max_hue)

        hue_window = np.zeros((1, 400, 3), np.uint8)
        cv2.imshow(self.WINDOW, hue_window)

    def run_robot(self, x):
        self.robot.running = True if x == 1 else False
        if not self.robot.running:
            self.robot.stop()

    def left_motor(self, x):
        self.robot.set_motors(left=x)

    def right_motor(self, x):
        self.robot.set_motors(right=x)

    def pick_circles(self, x):
        state.state = 0
        state.selected_robot = self.robot
        cv2.setTrackbarPos(PICK_CIRCLES, self.WINDOW, 0)

    def set_min_hue(self, trackbar, hob, x):
        hob.min_hue = min(x, hob.max_hue-MIN_RANGE)
        cv2.setTrackbarPos(trackbar, self.WINDOW, hob.min_hue)

    def set_max_hue(self, trackbar, hob, x):
        hob.max_hue = max(x, hob.min_hue+MIN_RANGE)
        cv2.setTrackbarPos(trackbar, self.WINDOW, hob.max_hue)

    def set_front_hue(self, x):
        if x == 1:
            state.set_state(State.AWAITING_CLICK, self.sfh_callback)
    def sfh_callback(self, x, y, hsv):
        self.robot.set_hue(self.robot.front_hue, hsv[y, x, 0])
        cv2.setTrackbarPos(SET_FRONT_HUE, self.WINDOW, 0)
        cv2.setTrackbarPos(FRONT_MIN_HUE, self.WINDOW, self.robot.front_hue.min_hue)
        cv2.setTrackbarPos(FRONT_MAX_HUE, self.WINDOW, self.robot.front_hue.max_hue)
        self.robot.set_front_box_2(Point(x, y), hsv)

    def set_back_hue(self, x):
        if x == 1:
            state.set_state(State.AWAITING_CLICK, self.sbh_callback)
    def sbh_callback(self, x, y, hsv):
        self.robot.set_hue(self.robot.back_hue, hsv[y, x, 0])
        cv2.setTrackbarPos(SET_BACK_HUE, self.WINDOW, 0)
        cv2.setTrackbarPos(BACK_MIN_HUE, self.WINDOW, self.robot.back_hue.min_hue)
        cv2.setTrackbarPos(BACK_MAX_HUE, self.WINDOW, self.robot.back_hue.max_hue)
        self.robot.set_back_box_2(Point(x, y), hsv)
    
