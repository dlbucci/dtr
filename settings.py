#!/usr/bin/env python

import cv2
import numpy as np

from state import *

SETTINGS_WINDOW = "Settings"

TARGET_RADIUS = "Target Radius:"
VIEW_SETTING = "View:"

SET_FLOOR_HUE = "Set Floor Hue:"
FLOOR_MIN_HUE = "Floor Min Hue:"
FLOOR_MAX_HUE = "Floor Max Hue:"
LAST_VIEW = 5

def set_floor_hue(x):
    if x == 1:
        state.set_state(State.AWAITING_CLICK, sfh_callback)
def sfh_callback(x, y, hsv):
    hue = hsv[y, x, 0]
    state.floor_hue.min_hue, state.floor_hue.max_hue = hue - HUE_HALF_RANGE, hue + HUE_HALF_RANGE
    cv2.setTrackbarPos(SET_FLOOR_HUE, SETTINGS_WINDOW, 0)
    cv2.setTrackbarPos(FLOOR_MIN_HUE, SETTINGS_WINDOW, state.floor_hue.min_hue)
    cv2.setTrackbarPos(FLOOR_MAX_HUE, SETTINGS_WINDOW, state.floor_hue.max_hue)

def set_min_hue(trackbar, hue, x):
    hue.min_hue = x
    cv2.setTrackbarPos(trackbar, SETTINGS_WINDOW, x)

def set_max_hue(trackbar, hue, x):
    hue.max_hue = x
    cv2.setTrackbarPos(trackbar, SETTINGS_WINDOW, x)

def setup_settings_window():
    cv2.namedWindow(SETTINGS_WINDOW)

    cv2.createTrackbar(VIEW_SETTING, SETTINGS_WINDOW, 0, LAST_VIEW,
                       lambda x: set_setting("view", x))
    cv2.createTrackbar(TARGET_RADIUS, SETTINGS_WINDOW, 30, 100,
                       lambda x: state.set_target_radius(x))
    cv2.setTrackbarPos(TARGET_RADIUS, SETTINGS_WINDOW, state.target_radius)

    cv2.createTrackbar(SET_FLOOR_HUE, SETTINGS_WINDOW, 0, 1, set_floor_hue)
    cv2.createTrackbar(FLOOR_MIN_HUE, SETTINGS_WINDOW, 0, 180, 
        lambda x: set_min_hue(FLOOR_MIN_HUE, state.floor_hue, x))
    cv2.createTrackbar(FLOOR_MAX_HUE, SETTINGS_WINDOW, 0, 180,
        lambda x: set_max_hue(FLOOR_MAX_HUE, state.floor_hue, x))

    dummy = np.zeros((1, 400, 3), np.uint8)
    cv2.imshow(SETTINGS_WINDOW, dummy)

def set_setting(name, x):
    setattr(state, name, x)
