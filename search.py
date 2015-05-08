#!/usr/bin/env python

import cv2
import heapq
import numpy as np
from point import Point

class PriorityQueue(object):
    def __init__(self):
        self.elements = []

    def empty(self):
        return len(self.elements) == 0

    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))

    def get(self):
        return heapq.heappop(self.elements)[1]

dirs = ((-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1))
class Graph(object):
    def __init__(self, box_size, hsv):
        self.width = 480 / box_size
        self.height = 360 / box_size
        self.box_size = box_size
        self.bhs = box_size / 2
        def gen(x, y):
            if hsv[box_size*y+self.bhs, box_size*x+self.bhs, 2] != 0:
                return (x, y)
            else:
                return None
        self.data = [[gen(x, y) for x in xrange(self.width)] for y in xrange(self.height)]

    def neighbors(self, (x, y)):
        for delta in dirs:
            (nx, ny) = (x+delta[0], y+delta[1])
            if (nx < 0 or nx >= self.width or ny < 0 or ny >= self.height or
                self.data[ny][nx] == None):
                continue
            yield (nx, ny)
    
    def point_for(self, x, y):
        ix, iy = int(x / self.box_size), int(y / self.box_size)
        if self.data[iy][ix] is not None:
            return (ix, iy)
        else:
            i = 1
            for i in xrange(3):
                if iy-i >= 0 and self.data[iy-i][ix] is not None:
                    return (ix, iy-i)
                if iy+i < len(self.data) and self.data[iy+i][ix] is not None:
                    return (ix, iy+i)
                if ix-i >= 0 and self.data[iy][ix-i] is not None:
                    return (ix-i, iy)
                if ix+i < len(self.data[iy]) and self.data[iy][ix+i] is not None:
                    return (ix+i, iy)
            return None
    def point_to_pos(self, (x, y)):
        return Point(x*self.box_size+self.bhs, y*self.box_size+self.bhs)

    def cost(self, (ax, ay), (bx, by)):
        if ax == bx or ay == by:
            return 1
        else:
            return 1.4

    def draw(self, frame):
        for y, L in enumerate(self.data):
            for x, d in enumerate(L):
                if d is not None:
                    cv2.circle(frame, (x*self.box_size+self.bhs, y*self.box_size+self.bhs),
                               2, (255, 255, 255), 2)

def reconstruct_path(came_from, start, goal):
    current = goal
    path = [current]
    while current != start:
        current = came_from[current]
        path.append(current)
    return path

def heuristic((x1, y1), (x2, y2)):
    dx = abs(x1-x2)
    dy = abs(y1-y2)
    mi = min(dx, dy)
    ma = max(dx, dy)
    return ma + .4*mi

def a_star_search(graph, start, goal):
    frontier = PriorityQueue()
    frontier.put(start, 0)
    came_from = {}
    cost_so_far = {}
    came_from[start] = None
    cost_so_far[start] = 0

    while not frontier.empty():
        current = frontier.get()
        print current

        if current == goal:
            break

        for neighbor in graph.neighbors(current):
            new_cost = cost_so_far[current] + graph.cost(current, neighbor)
            
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                priority = new_cost + heuristic(goal, neighbor)
                frontier.put(neighbor, priority)
                came_from[neighbor] = current

    return came_from, cost_so_far

