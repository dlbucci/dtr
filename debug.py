#!/usr/bin/env python

import cv2
import numpy as np
from Tkinter import *

from state import *

SETTINGS_WINDOW = "Settings"

TARGET_RADIUS = "Target Radius:"
VIEW_SETTING = "View:"
LAST_VIEW = 4

def GeneralSettingsFrame(Frame):
    def __init__(self, master, state):
        Frame.__init__(self, master=master, bd=2)
        self.pack(side="top")
        self.master = master
        self.state = state

        self.title = Label(self, text=SETTINGS_WINDOW)
        self.title.pack(side="top")

        self.view = Scale(self, variable=state.view,
                                from_=0, to=LAST_VIEW, orient=HORIZONTAL,
                                label=VIEW_SETTING)
        self.view.pack(side="top")

        self.view = Scale(self, variable=state.target_radius,
                                from_=30, to=100, orient=HORIZONTAL,
                                label=TARGET_RADIUS)
        self.view.pack(side="top")

def setup_settings_window():
    cv2.namedWindow(SETTINGS_WINDOW)

    cv2.createTrackbar(VIEW_SETTING, SETTINGS_WINDOW, 0, LAST_VIEW,
                       lambda x: set_setting("view", x))
    cv2.createTrackbar(TARGET_RADIUS, SETTINGS_WINDOW, 30, 100,
                       lambda x: state.set_target_radius(x))
    cv2.setTrackbarPos(TARGET_RADIUS, SETTINGS_WINDOW, state.target_radius)
 
    dummy = np.zeros((1, 400, 3), np.uint8)
    cv2.imshow(SETTINGS_WINDOW, dummy)

def set_setting(name, x):
    setattr(state, name, x)
