#!/usr/bin/env python
from hwconf import config
import struct
import unittest
import random

# Full Status Packet Description
# Configuration of this packet is done in the
# hwconf.ini

# Endianess -> ? TBD

#######################################################
# Desc|frmt character|size(bytes)|possible vals(ascii)#
#######################################################

##########
# Header #
##########
# Packet Type byte|'i'|4|'?'(status)
# Packet ID Num unsigned int|'i'|4|0-4294967295(client auto increments)
# System Error Code unsigned int|'i'|4|0-4294967295

#########
# Mixer #
#########
# Mixer error code unsigned char|'c'|1|See docs
# Mixer 0 period setting microseconds|'i'|4|0-2147483647
# Mixer 0 duty cycle percentage|'f'|4|0-1.0
# Mixer 1 period setting microseconds|'i'|4|0-2147483647
# Mixer 1 duty cycle percentage|'f'|4|0-1.0
# Mixer 2 period setting microseconds|'i'|4|0-2147483647
# Mixer 2 duty cycle percentage|'f'|4|0-1.0
# Mixer 3 period setting microseconds|'i'|4|0-2147483647
# Mixer 3 duty cycle percentage|'f'|4|0-1.0


##########
# Valves #
##########
# Valves error code |'c'|1|See docs
# Valves state|'hhh'|48 bits set valves to on or off


#################
# Thermocouples #
#################
# Thermocouple 0 current temp |'f'|4|Decimal temperature
# Thermocouple 0 error code |'c'|1|See docs
# Thermocouple 1 current temp |'f'|4|Decimal temperature
# Thermocouple 1 error code |'c'|1|See docs
# Thermocouple 2 current temp |'f'|4|Decimal temperature
# Thermocouple 2 error code |'c'|1|See docs
# Thermocouple 3 current temp |'f'|4|Decimal temperature
# Thermocouple 3 error code |'c'|1|See docs
# Thermocouple 4 current temp |'f'|4|Decimal temperature
# Thermocouple 4 error code |'c'|1|See docs
# Thermocouple 5 current temp |'f'|4|Decimal temperature
# Thermocouple 5 error code |'c'|1|See docs
# Thermocouple 6 current temp |'f'|4|Decimal temperature
# Thermocouple 6 error code |'c'|1|See docs
# Thermocouple 7 current temp |'f'|4|Decimal temperature
# Thermocouple 7 error code |'c'|1|See docs
# Thermocouple 8 current temp |'f'|4|Decimal temperature
# Thermocouple 8 error code |'c'|1|See docs

#####################
# Aux Thermocouples #
#####################
# Aux Thermocouple 0 current temp |'f'|4|Decimal temperature
# Aux Thermocouple 0 error code |'c'|1|See docs
# Aux Thermocouple 1 current temp |'f'|4|Decimal temperature
# Aux Thermocouple 1 error code |'c'|1|See docs
# Aux Thermocouple 2 current temp |'f'|4|Decimal temperature
# Aux Thermocouple 2 error code |'c'|1|See docs

###########
# Heaters #
###########
# Heaters State|'h'|1|See docs

####################
# Temp Controllers #
####################
# Temp Controller 0 setpoint|'f'|1|See docs
# Temp Controller 0 error code|'c'|1|See docs
# Temp Controller 1 setpoint|'f'|1|See docs
# Temp Controller 1 error code|'c'|1|See docs
# Temp Controller 2 setpoint|'f'|1|See docs
# Temp Controller 2 error code|'c'|1|See docs

#################
# SMC Interface #
#################
# SMC Interfaces  error code|'c'|1|See docs
# SMC Interface 0 Analog Out|'f'|4|0-10.0V
# SMC Interface 0 Analog In|'f'|4|0-5.0V
# SMC Interface 1 Analog Out|'f'|4|0-10.0V
# SMC Interface 1 Analog In|'f'|4|0-5.0V


########
# Fans #
########
# Fan status byte (3 bit)|'c'|See docs

###############
# Linear Axis #
###############
# Axis 0 Position steps (unsigned int)|'I'|0-4294967295
# Axis 0 Requested Position steps (unsigned int)|'I'|0-4294967295
# Axis 0 error code|'I'|4|0-4294967295
# Axis 1 Position steps (unsigned int)|'I'|0-4294967295
# Axis 1 Requested Position steps (unsigned int)|'I'|0-4294967295
# Axis 1 error code|'I'|4|0-4294967295
# Axis 2 Position steps (unsigned int)|'I'|0-4294967295
# Axis 2 Requested Position steps (unsigned int)|'I'|0-4294967295
# Axis 2 error code|'I'|4|0-4294967295
# Axis 3 Position steps (unsigned int)|'I'|0-4294967295
# Axis 3 Requested Position steps (unsigned int)|'I'|0-4294967295
# Axis 3 error code|'I'|4|0-4294967295
# Axis 4 Position steps (unsigned int)|'I'|0-4294967295
# Axis 4 Requested Position steps (unsigned int)|'I'|0-4294967295
# Axis 4 error code|'I'|4|0-4294967295

##################
# Digital Inputs #
##################
# Digital input error code |'c'|1|See docs
# Digital input state (12bits)|'H'|2|See Docs


###################
# Liquid Sensors #
###################
# Liquid sensor error code|'c'|1|See docs
# Liquid sensor 0 Analog In|'f'|4|0-3.3V
# Liquid sensor 1 Analog In|'f'|4|0-3.3V
# Liquid sensor 2 Analog In|'f'|4|0-3.3V
# Liquid sensor 3 Analog In|'f'|4|0-3.3V
# Liquid sensor 4 Analog In|'f'|4|0-3.3V
# Liquid sensor 5 Analog In|'f'|4|0-3.3V
# Liquid sensor 6 Analog In|'f'|4|0-3.3V
# Liquid sensor 7 Analog In|'f'|4|0-3.3V


##########################
# Additional Error Codes #
##########################
# Error Code 2 unsigned int|'I'|4|0-4294967295
# Error Code 3 unsigned int|'I'|4|0-4294967295
# Error Code 4 unsigned int|'I'|4|0-4294967295

class StatusMessageFormatFactory(object):
    """ Returns an object capable of generating struct
    objects for parsing the status messages returning from
    the elixys system
    """
    messagefmtsection = "Message Format"
    repeatfmtsection = "Repeat"      
    
    def __init__(self,config=config):
        self.conf = config
    
    def get_struct(self):
        """ Returns a struct to pack or unpack a status packet """        
        fmt = self.parse_config_fmt_str()
        return struct.Struct(fmt)
        
    def parse_config_fmt_str(self):
        """ Reads the configuration dictionary and constructs the format string
        for converting binary packet data to python types
        """
        msg = [self.parse_subsystem(name, sub) for name, 
            sub in self.conf.items() if(sub["is_subsystem"]==True)]
        return "".join(msg)
        
    def parse_subsystem(self, name, subsystem):                
        """ Parses the subsystem configurations on the configuration
        dictionary and constructs their underlying format strings
        """
        msg = []
        msgsec = subsystem[self.messagefmtsection]        
        for key, value in msgsec.items():
            if not isinstance(value, dict):
                msg.append(value)
        
        if msgsec.has_key(self.repeatfmtsection):
            rpsec = subsystem[self.messagefmtsection][self.repeatfmtsection]
            for unit_id in range(subsystem['count']):                
                vals = []
                for key, value in rpsec.items():
                    vals.append(value)
                msg.append("".join(vals))        
        return "".join(msg)        

        
if __name__ == '__main__':
    fmt_factory = StatusMessageFormatFactory()
    stat_struct = fmt_factory.get_struct()
    empty_packet = '\x00' * stat_struct.size
    empty_data = stat_struct.unpack(empty_packet)
    empty_data = list(empty_data)
    empty_data[1] = 1
    new_packet = stat_struct.pack(*empty_data)