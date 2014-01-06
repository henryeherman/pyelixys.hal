#!/usr/bin/env python
import sys
import time
import threading
from threading import Event, Thread


class ElixysThread(Thread):
    elixys_threads = []
    
    def __init__(self):
        super(ElixysThread,self).__init__()
        self.elixys_threads.append(self)
    

class ElixysStoppableThread(ElixysThread):
    
    def __init__(self):
        super(ElixysStoppableThread, self).__init__()
        self.stop_event = Event()
        self.daemon = True
    
    def run(self):
        while(not self.stop_event.is_set()):
            self.loop()        

    def stop(self):
        self.stop_event.set()
        self.join()
        
    def loop(self):
        print "Doing loop"
        time.sleep(1.0)