#!/usr/bin/env python
import sys
import threading
from threading import Event, Thread


class ElixysThread(Thread):
    elixys_threads = []
    
    def __init__(self):
        Thread.__init__(self)
        self.elixys_threads.append(self)
    

class ElixysStoppableThread(ElixysThread):
    
    def __init__(self):
        ElixysThread.__init__(self)
        self.stop_event = Event()
        self.stop_event.clear()
    
    def run(self):
        while(!self.stop_event.isSet()):
            self.loop()

    def loop(self):
        pass