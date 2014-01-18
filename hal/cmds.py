#!/usr/bin/env python
import sys
import struct
import copy
from pyelixys.hal.elixysobject import ElixysObject
from pyelixys.elixysexceptions import ElixysValueError


class Command(ElixysObject):
    """ The command object allows the system to create
    correctly formatted hardware commands and send them
    to the websocket command queue for transmission to
    the synthesizer hardware """
    
    def __init__(self, sub_system, cmd_name, cmd_id, device_id=None, parameter="\x00"):
        self.sub_system = sub_system
        self.cmd_name = cmd_name
        self.cmd_id = cmd_id
        self.device_id_ = device_id
        self.param = parameter
        

    def set_device_id(self, device_id):
        """ Used to set the device_id for a command.
        only valid for commands where the count parameter
        in the INI file in set to a value greater than 0 """
        
        if not(device_id >=0 and device_id < self.sysconf[self.sub_system].get('count', 0)):
            raise ElixysValueError("System has no unit with device_id = %s" % str(device_id))                    
        self.device_id_ = device_id
    
    def get_device_id(self):
        """ Getter for the device_id, 
        maybe someday add value checking?
        """
        return self.device_id_ if not self.device_id_ is None else 0

    device_id = property(get_device_id, set_device_id)
        
    def __getitem__(self, key):
        """ Allows the creation of a new command object
        when this command is called using the [] syntax.
        The device_id is set the the value of key.
        This will raise an exception if the device_id (key)
        is not allowed due to the count parameter in the INI file.        
        """
        new_cmd = copy.copy(self)
        new_cmd.device_id = key
        return new_cmd
        
    def __setitem__(self, ket, value):
        """ Can only retrieved not set!
        """
        raise ElixysValueError("Command device_ids are read only")
    
    device_id = property(get_device_id, set_device_id)
        
        
    def __call__(self, parameter=None):
        """ Allows the use of the cmd[device_id](param) syntax,
        for the returning of a new Command object.
        This command can then be place in the queue for transmission
        """
        if not parameter is None:
            self.param = parameter
        return self

    def __str__(self):
        """ Converts the command to a byte string.
        These byte can then be sent to the synthesizer
        """       
        try:
            cmd_pkt =  self.struct_.pack(self.cmd_id[0],
                                         self.device_id,
                                         self.param)
        except struct.error:
		    try:
			    cmd_pkt =  self.struct_.pack(self.cmd_id[0],
                                         self.device_id,
                                         *self.param)
		    except TypeError as e:
			    cmd_pkt = None
			    raise ElixysValueError("Bad parameter: %s" % e)
			
        return cmd_pkt        
    
    def get_fmt_str(self):
        """ Uses the format character from the INI file
        to construct a format string of the proper type
        for generating a struct that can properly
        pack the bytes for transmission
        """
        self.fmt_str_ = "<"  # Endianess-> Little         
        self.fmt_str_ += "i"  # Command identifier
        self.fmt_str_ += "i"  # Device id
        self.fmt_str_ += self.cmd_id[1]  # Parameter type
        return self.fmt_str_

    fmt_str = property(get_fmt_str)
            
    def get_struct(self):
        """ Returns the struct associated with the
        proper format string for packing the command
        for transmission to the hardware
        """
        return struct.Struct(self.fmt_str)
    
    struct_ = property(get_struct)
    
        
        
    def __repr__(self):
        """ Pretty print the command for
        human readability
        """         
        return "CommandObject(%s,%s,%s,%s)" % (self.sub_system, 
                                            self.cmd_name, 
                                            str(self.device_id),
                                            self.param)

class CommandLookup(ElixysObject, dict):
    """ The CommandLookup object has a dictionary like
    interface for accessing the the commands defined in the INI
    These commands can be sent to the hardware. Each value returns a 
    Command object that can be shipped to the hardware for
    execution.
    """
    
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
        """ parse_cmds, looks at the sysconf generated
        from the INI file and constructs a dictionary of command
        objects.  These objects are directly accessible from this object
        using the standard dictionary interface
        """
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
        
        cmddict["System"] = dict()
        for key, val in self.sysconf['Commands'].iteritems():
            cmddict["System"][key] =  Command("System", key, val)
            
        return cmddict


cmd_lookup = CommandLookup()

