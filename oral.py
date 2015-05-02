#/usr/bin/env python

import math

import cv2

CAP_DIM = (480, 360)
CAP_FPS = 32

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

ROBOT_BOX_HALF_WIDTH = 15

# Firecracker (Robot 0)
R0_FRONT_MIN_HUE = 0
R0_FRONT_MAX_HUE = 180
R0_BACK_MIN_HUE = 0
R0_BACK_MAX_HUE = 180
R0_LEFT_MOTOR = 140
R0_RIGHT_MOTOR = 150

# Little Idiot (Robot 1)
R1_FRONT_MIN_HUE = 0
R1_FRONT_MAX_HUE = 180
R1_BACK_MIN_HUE = 0
R1_BACK_MAX_HUE = 180
R1_LEFT_MOTOR = 200
R1_RIGHT_MOTOR = 210

HUE_HALF_RANGE = 10

class Point(object):
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

class State(object):
    IDLE = 6

    AWAITING_FRONT_HUE = 10
    AWAITING_CLICK = 11

    def __init__(self):
        self.state = 0
        self.selected_robot = None
        self.target = Point()
        self.view = 0
        self.callback = None
        self.last_frame = None
        self.last_hsv = None

    def set_state(self, state, callback):
        self.state = state
        self.callback = callback

class HueSettings(object):
    def __init__(self, min_hue=0, max_hue=180):
        self.min_hue = min_hue
        self.max_hue = max_hue

p1 = Point()
p2 = Point()
state = State()
hue_settings = HueSettings()

