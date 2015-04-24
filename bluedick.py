#/usr/bin/env python

import math
import serial
import time

BLUETOOTH_BAUDRATE = 115200
FORWARD = "w"
BACKWARD = "s"
LEFT = "a"
RIGHT = "d"

LAST_POS_LIMIT = 5

TARGET_RADIUS = 60
TARGET_RADIUS_SQUARED = TARGET_RADIUS ** 2
ANGLE_ERROR_RADS = math.pi / 4 # error margin for one angle
MOVE_ERROR_PIXELS = 40
MOVE_ERROR_SQUARED = MOVE_ERROR_PIXELS ** 2

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
        self.serial = serial.Serial(device, baudrate=BLUETOOTH_BAUDRATE)
        self.speed = 0
        self.state = Robot.STOP
        self.old_x = 0
        self.old_y = 0
        self.angle = 0
        self.x = 0
        self.y = 0
        self.last_xs = []
        self.last_ys = []
        self.did_forward_last = False

    def forward(self, speed=1):
        self.speed = speed
        self.state = Robot.FORWARD
        return self.serial.write(FORWARD)

    def backward(self, speed=1):
        self.speed = speed
        self.state = Robot.BACKWARD
        return self.serial.write(BACKWARD)

    def left(self, speed=1):
        self.speed = speed
        self.state = Robot.LEFT
        return self.serial.write(LEFT)

    def right(self, speed=1):
        self.speed = speed
        self.state = Robot.RIGHT
        return self.serial.write(RIGHT)

    def stop(self):
        self.speed = 0
        self.state = Robot.STOP
        return self.serial.write("s\n")

    def auto(self):
        return self.serial.write("a\n")

    def manual(self):
        return self.serial.write("m\n")

    def deactivate_sensors(self):
        return self.serial.write("d\n")

    def activate_sensors(self):
        return self.serial.write("h\n")

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
            print "at target"
            self.old_x = self.x
            self.old_y = self.y
            return

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

        target_angle_rad = math.atan2(dy, dx)
        print "target angle:", target_angle_rad
        current_angle_rad = math.atan2(ody, odx)
        print "current angle:", current_angle_rad
        angle_delta = target_angle_rad - current_angle_rad
        if angle_delta > math.pi:
            angle_delta -= 2*math.pi
        elif angle_delta <= -math.pi:
            angle_delta += 2*math.pi
        print "final angle delta:", angle_delta

        if abs(angle_delta) < ANGLE_ERROR_RADS:
            if self.did_forward_last:
                print "moving forward"
                self.forward()
            else:
                print "moving backward"
                self.backward()
        elif angle_delta <= -ANGLE_ERROR_RADS:
            if self.did_forward_last:
                print "rotating left"
                self.left()
            else:
                print "rotating right"
                self.right()
        elif angle_delta > ANGLE_ERROR_RADS:
            if self.did_forward_last:
                print "rotating right"
                self.right()
            else:
                print "rotating left"
                self.left()

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
