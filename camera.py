#!/usr/bin/env python

import os
RASPBERRY_PI = os.uname()[1] == "raspberrypi"
if RASPBERRY_PI:
    from picamera.array import PiRGBArray
    from picamera import PiCamera
import cv2
import numpy as np
import time

from state import *
#from pumpkin import runBalls, step

def raspberryRun(step):
    camera = PiCamera()
    camera.resolution = CAP_DIM
    camera.framerate = CAP_FPS

    rawCapture = PiRGBArray(camera, size=CAP_DIM)

    time.sleep(1) # allow the camera to warm up

    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        image = frame.array

        step(image)

        rawCapture.truncate(0)

        if (cv2.waitKey(1) & 0xff) == ord('q'):
            break

def macRun(coverage):
    cap = cv2.VideoCapture(0)

    while True:
        if (cv2.waitKey(1) & 0xff) == ord('q'):
            break
        succ, image = cap.read()
        if not succ:
            continue

        step(image)

    # clean up
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    print "run pumpkin.py, you dumb ass"
    raise "Dumbass Error"
