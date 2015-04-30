#/usr/bin/env python

WINDOW_TITLE = "ASS BALLS"

class Point(object):
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

class State(object):
    def __init__(self):
        self.state = 0
        self.selected_robot = None
        self.target = Point()

p1 = Point()
p2 = Point()
state = State()

