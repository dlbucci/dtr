#/usr/bin/env python

import math

import cv2

CAP_DIM = (480, 360)
CAP_FPS = 30

WINDOW_TITLE = "DTR"

# TARGET SETTINGS
INITIAL_TARGET_RADIUS = 40
TARGET_CIRCLE_COLOR = (255, 255, 255)
TARGET_CIRCLE_THICKNESS = 2

ANGLE_ERROR_RADS = math.pi / 4 # error margin for one angle

# MOVEMENT TIMES
MOVE_TIME_DELTA = .5
TURN_TIME_DELTA = .25
# ERROR RECOVERY TIMES
TURN_TIMES = (.5, 1, 1.5, 2)
FORWARD_TIMES = (.5, 1, 1.5, 2)

# MEAN SHIFT TERMINATION CRITERIA
TERM_CRIT = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1)

ROBOT_BOX_HALF_WIDTH = 10

# Firecracker (Robot 0)
R0_FRONT_MIN_HUE = 0
R0_FRONT_MAX_HUE = 180
R0_BACK_MIN_HUE = 0
R0_BACK_MAX_HUE = 180
R0_LEFT_MOTOR = 160
R0_RIGHT_MOTOR = 170

# Little Idiot (Robot 1)
R1_FRONT_MIN_HUE = 0
R1_FRONT_MAX_HUE = 180
R1_BACK_MIN_HUE = 0
R1_BACK_MAX_HUE = 180
R1_LEFT_MOTOR = 180
R1_RIGHT_MOTOR = 190

HUE_HALF_RANGE = 10

class Point(object):
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

class State(object):
    IDLE = 6
    IDLE2 = 7

    AWAITING_CLICK = 11

    def __init__(self):
        self.state = State.IDLE
        self.selected_robot = None
        self.target = Point()
        self.set_target_radius(INITIAL_TARGET_RADIUS)
        self.view = 0
        self.callback = None
        self.last_frame = None
        self.last_hsv = None

        self.last_fps = 0
        self.frame_count = 0

        self.floor_hue = HueSettings()
        
        self.obstacles = []

    def set_state(self, state, callback):
        self.state = state
        self.callback = callback
    
    def set_target_radius(self, target_radius):
        self.target_radius = target_radius
        self.target_radius_squared = self.target_radius ** 2

class HueSettings(object):
    def __init__(self, min_hue=0, max_hue=180):
        self.min_hue = min_hue
        self.max_hue = max_hue

OBSTACLE_CLIFF = 0
OBSTACLE_WALL = 1
OBSTACLE_RADIUS = 5
OBSTACLE_COLOR = (0, 0, 255)
OBSTACLE_THICKNESS = 5
class Obstacle(object):
    def __init__(self, x, y, kind, robot):
        if kind == OBSTACLE_CLIFF:
            self.arg1 = (x, y)
            self.arg2 = OBSTACLE_RADIUS
        elif kind == OBSTACLE_WALL:
            self.arg1 = (x-OBSTACLE_RADIUS, y-OBSTACLE_RADIUS)
            self.arg2 = (x+OBSTACLE_RADIUS, y+OBSTACLE_RADIUS)
        self.kind = kind
        self.robot = robot

    def draw(self, frame):
        cv2.circles(frame, self.arg1, self.arg2, OBSTACLE_COLOR, OBSTACLE_THICKNESS)

p1 = Point()
p2 = Point()
state = State()
hue_settings = HueSettings()

