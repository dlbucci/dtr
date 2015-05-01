#/usr/bin/env python

import math
import random
import serial
import time

import numpy as np
import cv2

from oral import state

BLUETOOTH_BAUDRATE = 115200
FORWARD = "f"
BACKWARD = "b"
LEFT = "l"
RIGHT = "r"
STOP = "s\n"

CMD_FORMAT_STRING = "%c 180 190\n"

LAST_POS_LIMIT = 5

TARGET_RADIUS = 60
TARGET_RADIUS_SQUARED = TARGET_RADIUS ** 2
ANGLE_ERROR_RADS = math.pi / 4 # error margin for one angle
MOVE_ERROR_PIXELS = 40
MOVE_ERROR_SQUARED = MOVE_ERROR_PIXELS ** 2

MOVE_TIME_DELTA = .5
TURN_TIME_DELTA = .25
TURN_TIMES = (.3, .4, .5, .6)

TERM_CRIT = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 2)

def median(L):
    return (sorted(L))[(len(L)/2)]

class Robot(object):
    """ represents a robot. can be told to move with various methods """
    STOP = 0
    FORWARD = 1
    BACKWARD = 2
    LEFT = 3
    RIGHT = 4

    def __init__(self, device):
        """ device should be the path to the bluetooth device on the PI """
        self.device = device
        self.serial = serial.Serial(device, baudrate=BLUETOOTH_BAUDRATE)

        self.old_x = 0
        self.old_y = 0
        self.angle = 0
        self.x = 0
        self.y = 0
        self.last_xs = []
        self.last_ys = []
        self.did_forward_last = True
        self.next_move_time = 0

        self.front_box = None
        self.front_hist = None
        self.back_box = None
        self.back_hist = None
    
    def update(self, hsv, time):
        self.front_box = self.track(hsv, self.front_box, self.front_hist)
        self.back_box = self.track(hsv, self.back_box, self.back_hist)
        if (time >= self.next_move_time):
            self.next_move_time = time + self.make_move(state.target)
            res = self.serial.readline()
            if res[0:2] == "E:":
                if random.randint(0, 1) == 1:
                    self.right()
                else:
                    self.left()
                self.next_move_time = time + random.choice(TURN_TIMES)
                # clear error messages
                res = self.serial.readline()
                while res[0:2] == "E:":
                    res = self.serial.readline()


    def track(self, hsv, box, hist):
        back_proj = cv2.calcBackProject([hsv], [0], hist, [0, 180], 1)

        # apply meanshift to get the new location
        ret, box = cv2.meanShift(back_proj, box, TERM_CRIT)

        # do this
        self.update_pos(self.back_box[0] + self.back_box[2]/2, self.back_box[1] + self.back_box[3]/2)

        return box
        
    def draw(self, frame):
        if self.front_box:
            cv2.rectangle(frame, (self.front_box[0], self.front_box[1]),
                                 (self.front_box[2] + self.front_box[0], self.front_box[3] + self.front_box[1]), (0, 255, 255), 2)
        if self.back_box:
            cv2.rectangle(frame, (self.back_box[0], self.back_box[1]),
                                 (self.back_box[0] + self.back_box[2], self.back_box[1] + self.back_box[3]), (0, 255, 0), 2) 

    def resync(self):
        self.serial = serial.Serial(self.device, baudrate=BLUETOOTH_BAUDRATE) 

    def set_hists(self, frame):
        self.front_hist = self._hist_for((0, 0, 640, 480), frame)        
        self.back_hist = self._hist_for((0, 0, 640, 480), frame)        

    def set_front_box(self, p1, p2, frame):
        self.front_box = self._box_from(p1, p2)
        if self.front_hist is None:
            self.front_hist = self._hist_for(self.front_box, frame)

    def set_back_box(self, p1, p2, frame):
        self.back_box = self._box_from(p1, p2)
        if self.back_hist is None:
            self.back_hist = self._hist_for(self.back_box, frame)

    def _box_from(self, p1, p2):
        minx = min(p1.x, p2.x)
        miny = min(p1.y, p2.y)
        return (minx, miny, max(p1.x, p2.x) - minx, max(p1.y, p2.y) - miny)
    
    def _hist_for(self, box, frame):
        x, y, w, h = box
        # set up the ROI for tracking
        roi = frame[y:y+h, x:x+w]
        hsv_roi =  cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv_roi, np.array((20., 60.,32.)), np.array((50.,255.,255.)))
        roi_hist = cv2.calcHist([hsv_roi], [0], None, [16], [0, 180])
        cv2.normalize(roi_hist, roi_hist, 0, 255, cv2.NORM_MINMAX)
        cv2.imshow(self.device, roi)
        return roi_hist

    def forward(self, speed=1):
        try:
            return self.serial.write(CMD_FORMAT_STRING % FORWARD)
        except:
            return None

    def backward(self, speed=1):
        try:
            return self.serial.write(CMD_FORMAT_STRING % BACKWARD)
        except:
            return None

    def left(self, speed=1):
        try:
            return self.serial.write(CMD_FORMAT_STRING % LEFT)
        except:
            return None

    def right(self, speed=1):
        try:
            return self.serial.write(CMD_FORMAT_STRING % RIGHT)
        except:
            return None

    def stop(self):
        try:
            return self.serial.write(STOP)
        except:
            return None

    def auto(self):
        try:
            return self.serial.write("a\n")
        except:
            return None

    def manual(self):
        try:
            return self.serial.write("m\n")
        except:
            return None

    def deactivate_sensors(self):
        try:
            return self.serial.write("d\n")
        except:
            return None

    def activate_sensors(self):
        try:
            return self.serial.write("h\n")
        except:
            return None

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
        if (dx ** 2 + dy ** 2 < TARGET_RADIUS_SQUARED):
            self.old_x = self.x
            self.old_y = self.y
            self.stop()
            return MOVE_TIME_DELTA
        """
        odx = self.x - self.old_x
        ody = self.y - self.old_y
        if (odx ** 2 + ody ** 2 < MOVE_ERROR_SQUARED):
            if self.did_forward_last:
                print "moving backward, b/c just rotated"
                self.backward()
            else:
                print "moving forward, b/c just rotated"
                self.forward()
            self.did_forward_last = not self.did_forward_last
            self.old_x = self.x
            self.old_y = self.y
            return
        """
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
            if self.did_forward_last:
                self.forward()
            else:
                self.backward()
            return MOVE_TIME_DELTA
        elif angle_delta <= -ANGLE_ERROR_RADS:
            if self.did_forward_last:
                self.left()
            else:
                self.right()
        elif angle_delta > ANGLE_ERROR_RADS:
            if self.did_forward_last:
                self.right()
            else:
                self.left()

        return TURN_TIME_DELTA
        self.old_x = self.x
        self.old_y = self.y
        return

    
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
        return self.serial.readline()

    def write(self, arg):
        return self.serial.write(arg)

try:
    robot0 = Robot("/dev/rfcomm0")
    bts0 = serial.Serial("/dev/rfcomm0", baudrate=BLUETOOTH_BAUDRATE)
    print "Connected to Robot 0...",
    try:
        bts0.write("0")
        print "She's ready to go!"
    except:
        print "She ain't listenin'"
except:
    print "Could Not Connect to Robot 0"

try:
    robot1 = Robot("/dev/rfcomm1")
    bts1 = serial.Serial("/dev/rfcomm1", baudrate=BLUETOOTH_BAUDRATE)
    print "Connected to Robot 1...",
    try:
        bts1.write("0")
        print "She's ready to go!"
    except:
        print "She ain't listenin'"
except:
    print "Could Not Connect to Robot 1"

if __name__ == "__main__":
    print "Reading From Robot 1"
    while True:
        print repr(bts1.readline())
