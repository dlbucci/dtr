#/usr/bin/env python

import atexit
import math
import multiprocessing as mp
import os
import Queue
import random
import serial
import time

import numpy as np
import cv2

from state import *

BLUETOOTH_BAUDRATE = 115200
BLUETOOTH_TIMEOUT = 0
FORWARD = "f"
BACKWARD = "b"
LEFT = "l"
RIGHT = "r"
STOP = "s\n"

LAST_POS_LIMIT = 5

ERROR = "error"
ERROR_DONE = "error done"

SOUND_CMD_FMT = "omxplayer %s"

def median(L):
    return (sorted(L))[(len(L)/2)]

class Robot(object):
    """ represents a robot. can be told to move with various methods """

    def __init__(self, name, device, sound_folder, front_hue, back_hue, 
                 left_motor = 180, right_motor = 190):
        """ device should be the path to the bluetooth device on the PI """
        self.name = name

        self.device = device
        self.resync()

        self.sound_folder = sound_folder

        self.angle = 0
        self.x = 0
        self.y = 0
        self.last_xs = []
        self.last_ys = []
        self.next_move_time = 0

        self.front_box = None
        self.front_hist = None
        self.front_hue = front_hue

        self.back_box = None
        self.back_hist = None
        self.back_hue = back_hue

        self.running = False
        self.tracking = False

        self.target = Point()

        self.set_motors(left_motor, right_motor)

        self.messaging_queue = mp.Queue()
        self.listener = mp.Process(target=self.listen_for_errors, args=(self.messaging_queue,))
        atexit.register(self.listener.terminate)
        self.listener.start()
        self.error_state = 0
    
    def update(self, hsv, time):
        if (self.front_box is None or self.front_hist is None or
            self.back_box is None or self.back_hist is None or
            not self.tracking):
            return

        mask = cv2.inRange(hsv, np.array((self.front_hue.min_hue, 0, 0)),
                                np.array((self.front_hue.max_hue, 255, 255)))
        hsv1 = cv2.bitwise_and(hsv, hsv, mask=mask)
        self.front_box = self.track(hsv1, self.front_box, self.front_hist)

        mask = cv2.inRange(hsv, np.array((self.back_hue.min_hue, 0, 0)),
                                np.array((self.back_hue.max_hue, 255, 255)))
        hsv1 = cv2.bitwise_and(hsv, hsv, mask=mask)
        self.back_box = self.track(hsv1, self.back_box, self.back_hist)
        
        if not self.running:
            return

        self.check_for_error()
        if self.error_state > 0:
            self.next_move_time = time + self.on_error(time)
            return

        if (time >= self.next_move_time):
            self.next_move_time = time + self.make_move(self.target)

    def track(self, hsv, box, hist):
        back_proj = cv2.calcBackProject([hsv], [0], hist, [0, 180], 1)

        # apply meanshift to get the new location
        ret, box = cv2.meanShift(back_proj, box, TERM_CRIT)

        # do this
        self.update_pos(self.front_box[0] + self.front_box[2]/2, 
                        self.front_box[1] + self.front_box[3]/2)

        return box

    def draw(self, frame):
        if self.front_box is not None:
            cv2.rectangle(frame, (self.front_box[0], self.front_box[1]),
                                 (self.front_box[2] + self.front_box[0], self.front_box[3] + self.front_box[1]), (0, 255, 255), 2)
        if self.back_box is not None:
            cv2.rectangle(frame, (self.back_box[0], self.back_box[1]),
                                 (self.back_box[0] + self.back_box[2], self.back_box[1] + self.back_box[3]), (0, 255, 0), 2) 
        cv2.circle(frame, (self.target.x, self.target.y), state.target_radius,
                   TARGET_CIRCLE_COLOR, TARGET_CIRCLE_THICKNESS)

    def resync(self):
        try:
            self.serial = serial.Serial(self.device, baudrate=BLUETOOTH_BAUDRATE)
        except:
            self.serial = None

    def set_hists(self, frame):
        self.front_hist = self._hist_for((0, 0, 640, 480), frame,
                                         self.front_hue.min_hue,
                                         self.front_hue.max_hue)
        self.back_hist = self._hist_for((0, 0, 640, 480), frame,
                                        self.back_hue.min_hue,
                                        self.back_hue.max_hue)

    def set_hue(self, hob, hue):
        hob.min_hue = hue - HUE_HALF_RANGE
        hob.max_hue = hue + HUE_HALF_RANGE

    def set_front_box(self, p1, p2, hsv):
        self.front_box = self._box_from(p1, p2)
        self.front_hist = self._hist_for(self.front_box, hsv,
                                     self.front_hue.min_hue,
                                     self.front_hue.max_hue)

    def set_front_box_2(self, p1, hsv):
        self.set_front_box(Point(p1.x - ROBOT_BOX_HALF_WIDTH,
                                 p1.y - ROBOT_BOX_HALF_WIDTH),
                           Point(p1.x + ROBOT_BOX_HALF_WIDTH,
                                 p1.y + ROBOT_BOX_HALF_WIDTH), hsv)

    def set_back_box(self, p1, p2, hsv):
        self.back_box = self._box_from(p1, p2)
        self.back_hist = self._hist_for(self.back_box, hsv,
                                    self.back_hue.min_hue,
                                    self.back_hue.max_hue)

    def set_back_box_2(self, p1, hsv):
        self.set_back_box(Point(p1.x - ROBOT_BOX_HALF_WIDTH,
                                p1.y - ROBOT_BOX_HALF_WIDTH),
                          Point(p1.x + ROBOT_BOX_HALF_WIDTH,
                                p1.y + ROBOT_BOX_HALF_WIDTH), hsv)

    def _box_from(self, p1, p2):
        minx = min(p1.x, p2.x)
        miny = min(p1.y, p2.y)
        return (minx, miny, max(p1.x, p2.x) - minx, max(p1.y, p2.y) - miny)
    
    def _hist_for(self, box, hsv, hue_min, hue_max):
        x, y, w, h = box
        # set up the ROI for tracking
        #roi = frame[y:y+h, x:x+w]
        hsv_roi = hsv[y:y+h, x:x+w] #cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv_roi,
                           np.array((hue_min, 0, 0)), 
                           np.array((hue_max, 255, 255)))
        roi_hist = cv2.calcHist([hsv_roi], [0], mask, [16], [0, 180])
        cv2.normalize(roi_hist, roi_hist, 0, 255, cv2.NORM_MINMAX)
        return roi_hist

    def set_motors(self, left=None, right=None):
        if left is not None:
            self.left_motor = left
        if right is not None:
            self.right_motor = right
        self.cmd_format_string = "%%c %d %d\n" % (self.left_motor, self.right_motor)

    def update_pos(self, x, y):
        self.last_xs.append(x)
        self.last_ys.append(y)
        if len(self.last_xs) > LAST_POS_LIMIT:
            self.last_xs.pop(0)
            self.last_ys.pop(0)
        self.x = median(self.last_xs)
        self.y = median(self.last_ys)
        
    def make_move(self, target):
        dx = target.x - self.x
        dy = target.y - self.y
        if (dx ** 2 + dy ** 2 < state.target_radius_squared):
            self.stop()
            return MOVE_TIME_DELTA

        odx = (self.front_box[0] + self.front_box[2]/2) - (self.back_box[0] + self.back_box[2]/2)
        ody = (self.front_box[1] + self.front_box[3]/2) - (self.back_box[1] + self.back_box[3]/2)

        target_angle_rad = math.atan2(dy, dx)
        current_angle_rad = math.atan2(ody, odx)
        angle_delta = target_angle_rad - current_angle_rad
        if angle_delta > math.pi:
            angle_delta -= 2*math.pi
        elif angle_delta <= -math.pi:
            angle_delta += 2*math.pi

        if abs(angle_delta) < ANGLE_ERROR_RADS:
            self.forward()
        elif angle_delta <= -ANGLE_ERROR_RADS:
            self.left()
        elif angle_delta > ANGLE_ERROR_RADS:
            self.right()

        return TURN_TIME_DELTA
    
    def make_move_2(self, target):
        pass

    # this is run in a subprocess and listens for errors
    def listen_for_errors(self, q):
        while True:
            res = self.read()
            if res[0:2] == "E:" or res[0:2] == "ED":
                q.put(res)

    def check_for_error(self):
        try:
            while True:
                msg = self.messaging_queue.get(block=False)
                if msg[0] == "E":
                    print msg,
                    if msg[1] == ":":
                        self.note_obstacle(msg[2:])
                        self.error_state = 1
                    elif msg[1] == "D":
                        self.error_state = 3
        except Queue.Empty:
            pass

    def on_error(self, time):
        if self.error_state == 3:
            self.error_state = 4
            if random.randint(0, 1) == 1:
                self.right()
            else:
                self.left()
            return random.choice(TURN_TIMES)
        elif self.error_state == 4:
            self.error_state = 0
            self.forward()
            return random.choice(FORWARD_TIMES)
        elif self.error_state == 1:
            self.error = 2
            return 1
        else:
            return 1

    def note_obstacle(self, msg):
        if msg == "FIR\n":
            state.obstacles.append(Obstacle(self.front_box[0], self.front_box[1], OBSTACLE_WALL, self))
        elif msg == "CL\n":
            state.obstacles.append(Obstacle(self.front_box[0], self.front_box[1], OBSTACLE_CLIFF, self))
        elif msg == "CR\n":
            state.obstacles.append(Obstacle(self.front_box[0], self.front_box[1], OBSTACLE_CLIFF, self))
        elif msg == "B\n":
            state.obstacles.append(Obstacle(self.front_box[0], self.front_box[1], OBSTACLE_WALL, self))

    #
    # private - meant for testing below here
    #

    def test(self):
	self.forward(2)
	time.sleep(0.5)
	self.backward(2)
	time.sleep(0.5)
	self.left(2)
	time.sleep(0.5)
	self.right(2)
	time.sleep(0.5)
	self.stop()
    
    def read(self):
        try:
            return self.serial.readline()
        except:
            return ""

    def write(self, arg):
        try:
            return self.serial.write(arg)
        except:
            return 0

    def forward(self):
        return self.write(self.cmd_format_string % FORWARD)

    def backward(self):
        return self.write(self.cmd_format_string % BACKWARD)

    def left(self):
        return self.write(self.cmd_format_string % LEFT)

    def right(self):
        return self.write(self.cmd_format_string % RIGHT)

    def stop(self):
        return self.write(STOP)

    def auto(self):
        return self.write("a\n")

    def manual(self):
        return self.write("m\n")

    def deactivate_sensors(self):
        return self.write("d\n")

    def activate_sensors(self):
        return self.write("h\n")

    def say_hi(self):
        os.system(SOUND_CMD_FMT % (self.sound_folder + "Hi.wav"))

try:
    robot0 = Robot("Firecracker", "/dev/rfcomm0", "Sounds/FireCracker/",
                   HueSettings(R0_FRONT_MIN_HUE, R0_FRONT_MAX_HUE),
                   HueSettings(R0_BACK_MIN_HUE, R0_BACK_MAX_HUE),
                   R0_LEFT_MOTOR, R0_RIGHT_MOTOR)
    robot0.say_hi()
    bts0 = serial.Serial("/dev/rfcomm0", baudrate=BLUETOOTH_BAUDRATE)
    print "Connected to Robot 0...",
    try:
        bts0.write("0")
        print "She's ready to go!"
    except:
        print "She ain't listenin'"
except Exception as e:
    print "Could Not Connect to Robot 0"
    print e

try:
    robot1 = Robot("Little Idiot", "/dev/rfcomm1", "Sounds/LittleIdiot/",
                   HueSettings(R1_FRONT_MIN_HUE, R1_FRONT_MAX_HUE),
                   HueSettings(R1_BACK_MIN_HUE, R1_BACK_MAX_HUE),
                   R1_LEFT_MOTOR, R1_RIGHT_MOTOR)
    bts1 = serial.Serial("/dev/rfcomm1", baudrate=BLUETOOTH_BAUDRATE)
    print "Connected to Robot 1...",
    try:
        bts1.write("0")
        print "She's ready to go!"
    except:
        print "She ain't listenin'"
except Exception as e:
    print "Could Not Connect to Robot 1"
    print e

if __name__ == "__main__":
    print "Reading From Robot 1"
    while True:
        print repr(bts1.readline())
