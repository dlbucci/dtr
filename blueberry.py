#/usr/bin/env python

import serial
import time

BLUETOOTH_BAUDRATE = 115200

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

    def forward(self, speed=1):
        self.speed = speed
        self.state = Robot.FORWARD
        return self.serial.write("f%d%d\n" % (speed * 10, speed * 10))

    def backward(self, speed=1):
        self.speed = speed
        self.state = Robot.BACKWARD
        return self.serial.write("b%d%d\n" % (speed * 10, speed * 10))

    def left(self, speed=1):
        self.speed = speed
        self.state = Robot.LEFT
        return self.serial.write("l%d%d\n" % (speed * 10, speed * 10))

    def right(self, speed=1):
        self.speed = speed
        self.state = Robot.RIGHT
        return self.serial.write("r%d%d\n" % (speed * 10, speed * 10))

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
    bts0 = serial.Serial("/dev/rfcomm0", baudrate=115200)
    print "Connected to Robot 0...",
    try:
        bts0.write("s")
        print "She's ready to go!"
    except:
        print "She ain't listenin'"
except:
    print "Could Not Connect to Robot 0"

try:
    robot1 = Robot("/dev/rfcomm1")
    bts1 = serial.Serial("/dev/rfcomm1", baudrate=115200)
    print "Connected to Robot 1...",
    try:
        bts1.write("s")
        print "She's ready to go!"
    except:
        print "She ain't listenin'"
except:
    print "Could Not Connect to Robot 1"
