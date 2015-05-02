#!/usr/bin/env python

import cv2
import numpy as np

from oral import *

SETTINGS_WINDOW = "Settings"

VIEW_SETTING = "View:"
LAST_VIEW = 4

def setup_settings_window():
    cv2.namedWindow(SETTINGS_WINDOW)

    cv2.createTrackbar(VIEW_SETTING, SETTINGS_WINDOW, 0, LAST_VIEW,
                       lambda x: set_setting("view", x))
 
    dummy = np.zeros((1, 400, 3), np.uint8)
    cv2.imshow(SETTINGS_WINDOW, dummy)

def set_setting(name, x):
    setattr(state, name, x)