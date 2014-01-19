#!/usr/bin/env python
"""
The StatusMessageFormatFactory object in statusfmt.py
parses the sysconf and generates
C source and header files for use on MCUs
that wish to communicate with the websocket server.
Status packet maintain the structure define in the INI
Additional information can be found in the comments below.
"""
# Full Status Packet Description

# Endianess -> ? TBD

#-----------------------------------------------------#
# Desc|frmt character|size(bytes)|possible vals(ascii)#
#-----------------------------------------------------#

# Header #
##########
# 1)Packet Type byte|'i'|4|'?'(status)
# 2)Packet ID Num unsigned int|'i'|4|0-4294967295(client auto increments)
# 3)System Error Code unsigned int|'i'|4|0-4294967295

# Mixer #
#########
# 4)Mixer error code unsigned char|'c'|1|See docs
# 5)Mixer 0 period setting microseconds|'i'|4|0-2147483647
# 6)Mixer 0 duty cycle percentage|'f'|4|0-1.0
# 7)Mixer 1 period setting microseconds|'i'|4|0-2147483647
# 8)Mixer 1 duty cycle percentage|'f'|4|0-1.0
# 9)Mixer 2 period setting microseconds|'i'|4|0-2147483647
# 10)Mixer 2 duty cycle percentage|'f'|4|0-1.0
# 11)Mixer 3 period setting microseconds|'i'|4|0-2147483647
# 12)Mixer 3 duty cycle percentage|'f'|4|0-1.0

# Valves #
##########
# 13)Valves error code |'c'|1|See docs
# 14)Valves state|'hhh'|48 bits set valves to on or off

# Thermocouples #
#################
# 15)Thermocouple 0 current temp |'f'|4|Decimal temperature
# 16)Thermocouple 0 error code |'c'|1|See docs
# 17)Thermocouple 1 current temp |'f'|4|Decimal temperature
# 18)Thermocouple 1 error code |'c'|1|See docs
# 19)Thermocouple 2 current temp |'f'|4|Decimal temperature
# 20)Thermocouple 2 error code |'c'|1|See docs
# 21)Thermocouple 3 current temp |'f'|4|Decimal temperature
# 22)Thermocouple 3 error code |'c'|1|See docs
# 23)Thermocouple 4 current temp |'f'|4|Decimal temperature
# 24)Thermocouple 4 error code |'c'|1|See docs
# 25)Thermocouple 5 current temp |'f'|4|Decimal temperature
# 26)Thermocouple 5 error code |'c'|1|See docs
# 27)Thermocouple 6 current temp |'f'|4|Decimal temperature
# 28)Thermocouple 6 error code |'c'|1|See docs
# 29)Thermocouple 7 current temp |'f'|4|Decimal temperature
# 30)Thermocouple 7 error code |'c'|1|See docs
# 31)Thermocouple 8 current temp |'f'|4|Decimal temperature
# 32)Thermocouple 8 error code |'c'|1|See docs

# Aux Thermocouples #
#####################
# 33)Aux Thermocouple 0 current temp |'f'|4|Decimal temperature
# 34)Aux Thermocouple 0 error code |'c'|1|See docs
# 35)Aux Thermocouple 1 current temp |'f'|4|Decimal temperature
# 36)Aux Thermocouple 1 error code |'c'|1|See docs
# 37)Aux Thermocouple 2 current temp |'f'|4|Decimal temperature
# 38)Aux Thermocouple 2 error code |'c'|1|See docs

# Heaters #
###########
# 39)Heaters State|'h'|1|See docs

# Temp Controllers #
####################
# 40)Temp Controller 0 setpoint|'f'|1|See docs
# 41)Temp Controller 0 error code|'c'|1|See docs
# 42)Temp Controller 1 setpoint|'f'|1|See docs
# 43)Temp Controller 1 error code|'c'|1|See docs
# 44)Temp Controller 2 setpoint|'f'|1|See docs
# 45)Temp Controller 2 error code|'c'|1|See docs

# SMC Interface #
#################
# 46)SMC Interfaces  error code|'c'|1|See docs
# 47)SMC Interface 0 Analog Out|'f'|4|0-10.0V
# 48)SMC Interface 0 Analog In|'f'|4|0-5.0V
# 49)SMC Interface 1 Analog Out|'f'|4|0-10.0V
# 50)SMC Interface 1 Analog In|'f'|4|0-5.0V

# Fans #
########
# 51)Fan status byte (3 bit)|'c'|See docs

# Linear Axis #
###############
# 52)Axis 0 Position steps (unsigned int)|'I'|0-4294967295
# 53)Axis 0 Requested Position steps (unsigned int)|'I'|0-4294967295
# 54)Axis 0 error code|'I'|4|0-4294967295
# 55)Axis 1 Position steps (unsigned int)|'I'|0-4294967295
# 56)Axis 1 Requested Position steps (unsigned int)|'I'|0-4294967295
# 57)Axis 1 error code|'I'|4|0-4294967295
# 58)Axis 2 Position steps (unsigned int)|'I'|0-4294967295
# 59)Axis 2 Requested Position steps (unsigned int)|'I'|0-4294967295
# 60)Axis 2 error code|'I'|4|0-4294967295
# 61)Axis 3 Position steps (unsigned int)|'I'|0-4294967295
# 62)Axis 3 Requested Position steps (unsigned int)|'I'|0-4294967295
# 63)Axis 3 error code|'I'|4|0-4294967295
# 64)Axis 4 Position steps (unsigned int)|'I'|0-4294967295
# 65)Axis 4 Requested Position steps (unsigned int)|'I'|0-4294967295
# 66)Axis 4 error code|'I'|4|0-4294967295

# Digital Inputs #
##################
# 67)Digital input error code |'c'|1|See docs
# 68)Digital input state (12bits)|'H'|2|See Docs

# Liquid Sensors #
###################
# 69)Liquid sensor error code|'c'|1|See docs
# 70)Liquid sensor 0 Analog In|'f'|4|0-3.3V
# 71)Liquid sensor 1 Analog In|'f'|4|0-3.3V
# 72)Liquid sensor 2 Analog In|'f'|4|0-3.3V
# 73)Liquid sensor 3 Analog In|'f'|4|0-3.3V
# 74)Liquid sensor 4 Analog In|'f'|4|0-3.3V
# 75)Liquid sensor 5 Analog In|'f'|4|0-3.3V
# 76)Liquid sensor 6 Analog In|'f'|4|0-3.3V
# 77)Liquid sensor 7 Analog In|'f'|4|0-3.3V

# Additional Error Codes #
##########################
# Error Code 2 unsigned int|'I'|4|0-4294967295
# Error Code 3 unsigned int|'I'|4|0-4294967295
# Error Code 4 unsigned int|'I'|4|0-4294967295


import struct
import jinja2
from pyelixys.hal.fmt_lookup import fmt_chr
from pyelixys.hal.hwconf import config

class StatusMessageFormatFactory(object):
    """ Returns an object capable of generating struct
    objects for parsing the status messages returning from
    the elixys system
    """
    messagefmtsection = "Message Format"
    repeatfmtsection = "Repeat"

    def __init__(self, config=config):
        self.conf = config

    def get_struct(self):
        """ Returns a struct to pack or unpack a status packet """
        fmt = self.parse_config_fmt_str()
        return struct.Struct(fmt)

    def get_subsystems(self):
        return [(name, sub.get('count', 1), sub[self.messagefmtsection])
                for name, sub in self.conf.items()
                if(self.messagefmtsection in sub)]

    subsystems = property(get_subsystems)

    def parse_config_fmt_str(self):
        """ Reads the configuration dictionary and constructs the format string
        for converting binary packet data to python types
        """
        msg = [self.parse_subsystem(name, sub) for name,
               sub in self.conf.items() if(self.messagefmtsection in sub)]
        return "<"+"".join(msg) # Little endian!

    def parse_subsystem(self, name, subsystem):
        """ Parses the subsystem configurations on the configuration
        dictionary and constructs their underlying format strings
        """
        msg = []
        msgsec = subsystem[self.messagefmtsection]
        for key, value in msgsec.items():
            if not isinstance(value, dict):
                msg.append(value)

        if self.repeatfmtsection in msgsec:
            rpsec = subsystem[self.messagefmtsection][self.repeatfmtsection]
            for unit_id in range(subsystem['count']):
                vals = []
                for key, value in rpsec.items():
                    vals.append(value)
                msg.append("".join(vals))
        return "".join(msg)

    def generate_c_header(self, filename=None):
        template_loader = jinja2.FileSystemLoader(searchpath=".")
        template_env = jinja2.Environment(loader=template_loader,
                                          trim_blocks=True,
                                          lstrip_blocks=True)
        TEMPLATE_FILE = self.conf['c_status_header_template']
        template = template_env.get_template(TEMPLATE_FILE)
        template_vars = {"systems": self.subsystems,
                         "fmt_chr": fmt_chr}
        output_text = template.render(template_vars)

        if filename:
            f = open(filename, "w")
            f.write(output_text)
            f.close()
        return output_text
    
    
    def generate_c_src(self, filename=None):
        template_loader = jinja2.FileSystemLoader(searchpath=".")
        template_env = jinja2.Environment(loader=template_loader,
                                          trim_blocks=True,
                                          lstrip_blocks=True)
        TEMPLATE_FILE = self.conf['c_status_source_template']
        template = template_env.get_template(TEMPLATE_FILE)
        template_vars = {"systems": self.subsystems,
                         "fmt_chr": fmt_chr}
        output_text = template.render(template_vars)

        if filename:
            f = open(filename, "w")
            f.write(output_text)
            f.close()
        return output_text

if __name__ == '__main__':
    fmt_factory = StatusMessageFormatFactory()
    stat_struct = fmt_factory.get_struct()
    empty_packet = '\x00' * stat_struct.size
    empty_data = stat_struct.unpack(empty_packet)
    empty_data = list(empty_data)
    empty_data[1] = 1
    new_packet = stat_struct.pack(*empty_data)
