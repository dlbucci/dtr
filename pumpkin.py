#!/usr/bin/env python

import numpy as np
import cv2

from bluedick import *
from oral import *

def get_roi_hist(frame):
    # setup initial location of window
    c, r, w, h = 320-480/8, 240-480/8, 480/4, 480/4 # simply hardcoded the values
    track_window = (c, r, w, h)

    cv2.rectangle(frame, (c,r), (c+w,r+h), 255, 2)
    #cv2.imshow(WINDOW_TITLE, frame)

    k = cv2.waitKey(1) & 0xff
    if k != ord('s'):
        return None, None

    # set up the ROI for tracking
    roi = frame[r:r+h, c:c+w]
    hsv_roi =  cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv_roi, np.array((20., 60.,32.)), np.array((50.,255.,255.)))
    roi_hist = cv2.calcHist([hsv_roi], [0], None, [16], [0, 180])
    cv2.normalize(roi_hist, roi_hist, 0, 255, cv2.NORM_MINMAX)
    
    return track_window, roi_hist

def track_some_shit(frame, track_window, roi_hist):
    global mask, next_move_time
    if track_window is None:
        return

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    back_proj = cv2.calcBackProject([hsv], [0], roi_hist, [0, 180], 1)

    # apply meanshift to get the new location
    ret, track_window = cv2.meanShift(back_proj, track_window, TERM_CRIT)

    # Draw it on image
    x, y, w, h = track_window
    # cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
    mask[y:y+h, x:x+w] = 255
    # pts = np.int0(cv2.cv.BoxPoints(ret))
    # cv2.polylines(frame, [pts], True, (0, 255, 0), 2)
    # cv2.imshow(WINDOW_TITLE, cv2.bitwise_and(frame, frame, mask=mask))
    
    robot0.update_pos(x + w/2, y + h/2)
    current_time = time.time()
    if (current_time > next_move_time):
        print "Making Move..."
        robot0.make_move(target)
        next_move_time = current_time + MOVE_TIME_DELTA
    cv2.rectangle(frame, (robot0.old_x-w/2, robot0.old_y-h/2),
                         (robot0.old_x+w/2, robot0.old_y+h/2), (0, 255, 255), 2)
    cv2.rectangle(frame, (robot0.x-w/2, robot0.y-h/2), (robot0.x+w/2, robot0.y+h/2), (0, 255, 0), 2)
    
    return track_window

next_move_time = 0
MOVE_TIME_DELTA = 1

mask = np.zeros((480, 640), np.uint8)
roi_hist = None
# Setup the termination criteria, either 10 iterations or move by at least 1 pt
TERM_CRIT = ( cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1 )    
track_window = None
def step(image, coverage):
    global roi_hist
    global track_window
    if roi_hist is None:
    	track_window, roi_hist = get_roi_hist(image)
    else:
    	track_window = track_some_shit(image, track_window, roi_hist)

