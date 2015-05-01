#!/usr/bin/env python

import cv2
import numpy as np
from bluedick import *
from oral import *

WINDOW_FMT = "%s Settings"

FRONT_MIN_HUE = "Front Min Hue:"
FRONT_MAX_HUE = "Front Max Hue:"
BACK_MIN_HUE = "Back Min Hue:"
BACK_MAX_HUE = "Back Max Hue:"
MIN_RANGE = 1

class RobotSettingsWindow(object):
    def __init__(self, robot):
        self.robot = robot
        self.WINDOW = WINDOW_FMT % robot.device
        cv2.namedWindow(self.WINDOW)
    
        cv2.createTrackbar(FRONT_MIN_HUE, self.WINDOW, 0, 180, 
            lambda x: self.set_min_hue(FRONT_MIN_HUE, robot.front_hue, x))
        cv2.createTrackbar(FRONT_MAX_HUE, self.WINDOW, 0, 180,
            lambda x: self.set_max_hue(FRONT_MAX_HUE, robot.front_hue, x))
        cv2.createTrackbar(BACK_MIN_HUE, self.WINDOW, 0, 180,
            lambda x: self.set_min_hue(BACK_MIN_HUE, robot.back_hue, x))
        cv2.createTrackbar(BACK_MAX_HUE, self.WINDOW, 0, 180,
            lambda x: self.set_max_hue(BACK_MAX_HUE, robot.back_hue, x))
        cv2.setTrackbarPos(FRONT_MIN_HUE, self.WINDOW, robot.front_hue.min_hue)
        cv2.setTrackbarPos(FRONT_MAX_HUE, self.WINDOW, robot.front_hue.max_hue)
        cv2.setTrackbarPos(BACK_MAX_HUE, self.WINDOW, robot.back_hue.max_hue)
        cv2.setTrackbarPos(BACK_MAX_HUE, self.WINDOW, robot.back_hue.max_hue)
        
        hue_window = np.zeros((1, 400, 3), np.uint8)
        cv2.imshow(self.WINDOW, hue_window)

    def set_min_hue(self, trackbar, hob, x):
        hob.min_hue = min(x, hob.max_hue-MIN_RANGE)
        cv2.setTrackbarPos(trackbar, self.WINDOW, hob.min_hue)

    def set_max_hue(self, trackbar, hob, x):
        hob.max_hue = max(x, hob.min_hue+MIN_RANGE)
        cv2.setTrackbarPos(trackbar, self.WINDOW, hob.max_hue)

