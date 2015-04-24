#!/usr/bin/env python

import os
RASPBERRY_PI = os.uname()[1] == "raspberrypi"
if RASPBERRY_PI:
    from picamera.array import PiRGBArray
    from picamera import PiCamera
import cv2
import numpy as np
import time

from oral import *
from pumpkin import step

def pos_upper_left(pos):
    return (pos.x - 60, pos.y - 60 )
def pos_lower_right(pos):
    return (pos.x + 60, pos.y + 60 )

def raspberryRun(coverage): 
    camera = PiCamera()
    camera.resolution = CAP_DIM
    camera.framerate = CAP_FPS

    rawCapture = PiRGBArray(camera, size=CAP_DIM)

    time.sleep(1) # allow the camera to warm up

    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        image = frame.array

        step(image, coverage)
        cv2.rectangle(image, pos_upper_left(target), pos_lower_right(target), (0, 0, 255), 4)
        cv2.imshow(WINDOW_TITLE, image)

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

        step(image, coverage)

    # clean up
    cap.release()
    cv2.destroyAllWindows()

def on_click(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        target.x = x
        target.y = y
        print x, y
    elif event == cv2.EVENT_LBUTTONUP:
        pass

def run():
    # keep track of the which pixels have been covered
    coverage = np.zeros(CAP_DIM, np.uint8)
    cv2.namedWindow(WINDOW_TITLE)
    cv2.setMouseCallback(WINDOW_TITLE, on_click)
    if RASPBERRY_PI:
        raspberryRun(coverage)
    else:
        macRun(coverage)

CAP_DIM = (640, 480)
CAP_FPS = 16
if __name__ == "__main__":
    run()
