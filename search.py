#!/usr/bin/env python

import heapq

class PriorityQueue(object):
    def __init__(self):
        self.elements = []

    def empty(self):
        return len(self.elements) == 0

    def push(self, item, priority):
        heapq.heappush(self.elements, (priority, item))

    def get(self):
        return heapq.heappop(self.elements)[1]

dirs = ((-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1))
class Graph(object):
    def __init__(self, box_size, hsv):
        self.width = 48
        self.height = 36
        self.box_size = box_size
        self.bhs = box_size / 2
        def gen(x, y):
            return (x, y) if hsv[box_size*y+self.bhs, box_size*x+self.bhs, 0] != 0 else None 
        self.data = [[gen(x, y) for x in xrange(self.width)] for y in xrange(self.height)]

    def neighbors(self, (x, y)):
        for delta in dirs:
            (nx, ny) = (x+delta[0], y+delta[1])
            if (nx < 0 or nx >= self.width or ny < 0 or ny >= self.height or
                self.data[ny][nx] == None):
                continue
            yield (nx, ny)

    def draw(self, frame):
        for y in self.data:
            for x in self.data[y]:
                cv2.circle(frame, (x, y), self.bhs, (255, 255, 255), 2)

def reconstruct_path(came_from, start, goal):
    current = goal
    path = [current]
    while current != start:
        current = came_from[current]
        path.append(current)
    return path

def a_star_search(graph, start, goal):
    frontier = PriorityQueue()
    frontier.put(start, 0)
    came_from = {}
    cost_so_far = {}
    came_from[start] = None
    cost_so_far[start] = 0

    while not frontier.empty():
        current = frontier.get()

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

