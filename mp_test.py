#!/usr/bin/env python

from multiprocessing import Process, Queue
import time

def shit_on_a_dick(q):
    pass
    #q.put("testicles")
    #q.put("testicles")
    #q.put("testicles")

if __name__ == "__main__":
    q = Queue()
    p = Process(target=shit_on_a_dick, args=(q,))
    p.start()
    time.sleep(3)
    try:
        while True:
            print q.get(block=False)
    except Queue.Empty:
        print "yay"
    p.join()
