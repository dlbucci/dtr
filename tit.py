#!/usr/bin/env python

from multiprocessing import Process, Queue
import time

def shit_on_a_dick(q):
    time.sleep(3)
    q.put("testicles")

if __name__ == "__main__":
    q = Queue()
    p = Process(target=shit_on_a_dick, args=(q,))
    p.start()
    print q.get(block=False)
    p.join()
