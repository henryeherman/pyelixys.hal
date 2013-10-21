#!/usr/bin/env python
import sys
import struct
import copy
from multiprocessing import Queue
sys.path.append("../")
from elixysobject import ElixysObject
from elixysexceptions import ElixysValueError

cmd_queue = Queue(maxsize=0)

class Command(ElixysObject):
    queue = cmd_queue
    
    def __init__(self, sub_system, cmd_name, cmd_id, device_id=None, parameter=0):
        self.sub_system = sub_system
        self.cmd_name = cmd_name
        self.cmd_id = cmd_id
        self.device_id_ = device_id
        self.param = parameter
        

    def set_device_id(self, device_id):        
        if not(device_id >=0 and device_id < self.sysconf[self.sub_system].get('count', 0)):
            raise ElixysValueError("System has no unit with device_id = %s" % str(device_id))                    
        self.device_id_ = device_id
    
    def get_device_id(self):     
        return self.device_id_

    device_id = property(get_device_id, set_device_id)
        
    def __getitem__(self, key):               
        new_cmd = copy.copy(self)
        new_cmd.device_id = key
        return new_cmd
        
    def __setitem__(self, ket, value):
        raise ElixysValueError("Command device_ids are read only")
    
    device_id = property(get_device_id, set_device_id)
        
        
    def __call__(self, parameter=None):
        if not parameter is None:
            self.param = parameter
        return self

    def __str__(self):            
        cmd_pkt =  self.struct_.pack(self.cmd_id[0],
                                     self.device_id,
                                     self.param)
        return cmd_pkt        
    
    def get_fmt_str(self):
        self.fmt_str_ = "<"  # Endianess-> Little 
        self.fmt_str_ += "i"  # Command identifier
        self.fmt_str_ += "i"  # Command identifier
        self.fmt_str_ += self.cmd_id[1]  # Parameter type
        return self.fmt_str_

    fmt_str = property(get_fmt_str)
            
    def get_struct(self):
        return struct.Struct(self.fmt_str)
    
    struct_ = property(get_struct)
    
        
        
    def __repr__(self):
        return "CommandObject(%s,%s,%s,%s)" % (self.sub_system, 
                                            self.cmd_name, 
                                            str(self.device_id),
                                            self.param)

class CommandLookup(ElixysObject, dict):
    def __init__(self, *args, **kwargs):        
        self.update(*args, **kwargs)

    def __getitem__(self, key):
        val = dict.__getitem__(self, key)        
        return copy.copy(val)

    def __setitem__(self, key, val):        
        dict.__setitem__(self, key, val)

    def __repr__(self):
        dictrepr = dict.__repr__(self)
        return '%s(%s)' % (type(self).__name__, dictrepr)

    def update(self, *args, **kwargs):        
        for k, v in self.parse_cmds().iteritems():
            self[k] = v

    def parse_cmds(self):
        secs = ((name, value['Commands']) for
                name, value in self.sysconf.iteritems()
                if isinstance(value, dict)
                if "Commands" in value)
        cmddict = dict()
        for key, val in secs:
            secdict = dict()
            for subkey, subval in val.iteritems():
                if subkey != 'Repeat':
                    secdict[subkey] = Command(key, subkey, subval) #subsubvalsubval
                else:
                    for subsubkey, subsubval in val["Repeat"].iteritems():
                        secdict[subsubkey] = Command(key, subsubkey, subsubval) #subsubval
            cmddict[key] = secdict

        return cmddict


cmd_lookup = CommandLookup()

