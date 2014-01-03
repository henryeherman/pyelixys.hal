#!/usr/bin/env python
import sys
import time
import threading
import collections
from Queue import Empty
sys.path.append("../")
from statusfmt import StatusMessageFormatFactory
from elixysexceptions import ElixysValueError
from elixysobject import ElixysObject
from utils.elixysthread import ElixysStoppableThread
from logs import statlog as log


class ElixysReadOnlyError(ElixysValueError):
    pass


class StatusThread(ElixysStoppableThread):
    def __init__(self, status, status_queue):
        super(StatusThread, self).__init__()
        self.queue = status_queue
        self.status = status
        
    def loop(self):        
        try:            
            statpkt = self.queue.get(block=False, timeout=0.1)
            self.status.parse_packet(statpkt)
        except Empty:
            time.sleep(0.1)

class Status(ElixysObject, collections.MutableMapping):
    def __init__(self, *args, **kwargs):
        self.fmt = StatusMessageFormatFactory()
        self.struct = self.fmt.get_struct()
        self.store = dict()
        self.update(dict(*args, **kwargs))
        self.lock = threading.Lock()
        self.is_valid = False

    def __getitem__(self, key):
        if self.is_valid is False:
            return None
        self.lock.acquire()
        val = self.store[self.__keytransform__(key)]
        self.lock.release()
        return val

    def __setitem__(self, key, value):
        raise ElixysReadOnlyError("Status Packet only updated"
                                  "by new packet from hardware")
        #self.store[self.__keytransform__(key)] = value

    def __delitem__(self, key):
        self.lock.acquire()
        del self.store[self.__keytransform__(key)]
        self.lock.release()

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def __keytransform__(self, key):
        return key

    def parse_packet(self, pkt):
        subsystems = self.fmt.subsystems
        data = self.struct.unpack(pkt)
        data_dict = dict()
        data_idx = 0
        for subsystem, count, messagefmt in subsystems:
            #print subsystem
            sub_dict = dict()

            for key, value in messagefmt.items():
                if isinstance(value, str):
                    #print key, data_idx
                    sub_dict[key] = data[data_idx]
                    data_idx += 1

                elif key == "Repeat":
                    rptmessagefmt = messagefmt['Repeat']
                    units = []
                    for i in range(count):
                        unit_dict = dict()
                        for rkey, rval in rptmessagefmt.items():                            
                            unit_dict[rkey] = data[data_idx]
                            #print rkey, data_idx
                            data_idx += 1
                        units.append(unit_dict)
                        sub_dict[i] = unit_dict
                    sub_dict['Subs'] = units
                    sub_dict['count'] = count
            data_dict[subsystem] = sub_dict
        self.lock.acquire()
        self.store = data_dict
        for key, value in data_dict.items():
            setattr(self,key,value)
        self.lock.release()
        self.is_valid = True
        return data_dict

    def update_from_queue(self, queue):
        self.thread = StatusThread(self, queue)
        self.thread.start()
        
    def stop_update(self):
        self.thread.stop()        
        
status = Status()

if __name__ == '__main__':
    from tests import pktdata    
    #data = status.parse_packet(pktdata.test_packet)
