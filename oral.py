#/usr/bin/env python

import math

import cv2

WINDOW_TITLE = "ASS BALLS"

# TARGET SETTINGS
TARGET_RADIUS = 60
TARGET_RADIUS_SQUARED = TARGET_RADIUS ** 2
TARGET_CIRCLE_COLOR = (0, 0, 255)
TARGET_CIRCLE_THICKNESS = 2

ANGLE_ERROR_RADS = math.pi / 4 # error margin for one angle

# MOVEMENT TIMES
MOVE_TIME_DELTA = .5
TURN_TIME_DELTA = .25
TURN_TIMES = (.3, .4, .5, .6)

# MEAN SHIFT TERMINATION CRITERIA
TERM_CRIT = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1)

class Point(object):
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

class State(object):
    def __init__(self):
        self.state = 0
        self.selected_robot = None
        self.target = Point()
        self.view = 0

class HueSettings(object):
    def __init__(self):
        self.min_hue = 0
        self.max_hue = 180

p1 = Point()
p2 = Point()
state = State()
hue_settings = HueSettings()

