#!/usr/bin/env python

import cv2
import numpy as np
from Tkinter import *

from state import *

SETTINGS_WINDOW = "Settings"

TARGET_RADIUS = "Target Radius:"
VIEW_SETTING = "View:"
LAST_VIEW = 4

class GeneralSettingsFrame(Frame):
    def __init__(self, master):
        Frame.__init__(self, master=master, bd=2)
        self.pack(side="right")
        self.master = master

        self.title = Label(self, text=SETTINGS_WINDOW)
        self.title.pack(side="top")

        self.view = Scale(self, variable=state.view,
                                from_=0, to=LAST_VIEW, orient=HORIZONTAL,
                                label=VIEW_SETTING)
        self.view.pack(side="top")

        self.target_radius = Scale(self, command=state.set_target_radius,
                                   variable=state.target_radius,
                                   from_=30, to=100, orient=HORIZONTAL,
                                   label=TARGET_RADIUS)
        self.target_radius.pack(side="top")
