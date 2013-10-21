#!/usr/bin/env python
import sys
import threading
import collections
sys.path.append("../")
from statusfmt import StatusMessageFormatFactory
from elixysexceptions import ElixysValueError
from elixysobject import ElixysObject
#from logs import statlog as log


class ElixysReadOnlyError(ElixysValueError):
    pass


class Status(ElixysObject, collections.MutableMapping):
    def __init__(self, *args, **kwargs):
        self.fmt = StatusMessageFormatFactory()
        self.struct = self.fmt.get_struct()
        self.store = dict()
        self.update(dict(*args, **kwargs))
        self.lock = threading.Lock()

    def __getitem__(self, key):
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
                        for rkey, rval in rptmessagefmt.items():
                            unit_dict = dict()
                            unit_dict[rkey] = data[data_idx]
                            #print rkey, data_idx
                            data_idx += 1
                            units.append(unit_dict)
                    sub_dict['Units'] = units
            data_dict[subsystem] = sub_dict
        self.lock.acquire()
        self.store = data_dict
        self.lock.release()
        return data_dict

if __name__ == '__main__':
    from tests import pktdata
    status = Status()
    data = status.parse_packet(pktdata.test_packet)
