#!/usr/bin/env python
""" The ControlBoxSystem communicates with the
ControlBox Actuation board hardware over a virtual serial
port.  The COM port setting are imported from the
hwconf.  It allows the system to drive 2 SSR, 2 10V DACs,
and read 2 ADCs.
"""
import os
import sys
import time
import serial
from pyelixys.hal.elixysobject import ElixysObject
from pyelixys.logs import hallog as log
from pyelixys.elixysexceptions import ElixysComportError
import re

class ControlBoxSystem(ElixysObject):
    """ The ControlBoxStatus gives access to the features of
    the control box board, these include two solid state relays,
    normally one of which would be used to control the cooling system
    pump, two 10V DACs for setting the setpoints on the  and 2 ADCs
    for reading the current pressure from the pressure regulators.
    Additonally it is possible to set the LED Ring.
    """
    def __init__(self):
        super(ControlBoxSystem, self).__init__()
        self.conf = self.sysconf['ControlBox']
        if os.name == 'nt':
            self._port = self.conf['win_port']
        elif os.name == 'posix':
            self._port = self.conf['posix_port']
        else:
            raise ElixysComportError("Could not "
                    "determine platform for port")
        self._baud = self.conf['baud']
        self.serial = serial.Serial(port=self._port,
                                    baudrate=self._baud,
                                    timeout=0.2)

    def get_adcs(self):
        """ Query the CBox board for the ADC values
        convert them to integers, then multiple by the
        conversion factors in the hwconf.
        """
        self.clear_in_serial_buffer()
        s = "/ADC/run\n"
        self.serial.write(s)
        resp = self.serial.readline()
        regex = re.compile("(?:[ADC])+ "
                       "(?P<adc0>[0-9A-Fa-f]*), "
                       "(?P<adc1>[0-9A-Fa-f]*)")
        m = regex.match(resp)
        adcval0 = int(m.group('adc0'),16) * self.conf['ADCCONST0']
        adcval1 = int(m.group('adc1'),16) * self.conf['ADCCONST1']
        return adcval0, adcval1

    def get_adc0(self):
        return self.get_adcs()[0]

    def get_adc1(self):
        return self.get_adcs()[1]

    adc0 = property(get_adc0)
    adc1 = property(get_adc1)


    def get_dacs(self):
        """ Query the CBox board for the current DAC values
        convert them to integers, then multiple by the
        conversion factors in the hwconf.
        """
        self.clear_in_serial_buffer()
        s = "/DAC/run\n"
        self.serial.write(s)
        resp = self.serial.readline()
        regex = re.compile("(?:[DAC])+ "
                       "(?P<dac0>[0-9A-Fa-f]*), "
                       "(?P<dac1>[0-9A-Fa-f]*)")
        m = regex.match(resp)
        dacval0 = int(m.group('dac0'),16) * self.conf['DACCONST0']
        dacval1 = int(m.group('dac1'),16) * self.conf['DACCONST1']
        return dacval0, dacval1

    def get_dac0(self):
        return self.get_dacs()[0]

    def get_dac1(self):
        return self.get_dacs()[1]

    dac0 = property(get_dac0)
    dac1 = property(get_dac1)

    def clear_in_serial_buffer(self):
        """ Check the serial buffer and make sure it is clear """
        if self.serial.inWaiting():
            resp = self.serial.readall()
            log.warn("Unknown/unparsed serial response: %s", resp)


    def write(self, s):
        """ This will replace the serial write.
        This should make sure the comport is open
        and available.  It NOT retry to open!
        If we can't open raise exception.
        """
        pass

    def read(self, s):
        """ This will replace the serial read.
        Make sure comport is avialable. If so
        read! Else try to open.  If can't open
        raise exception.
        """
        pass


if __name__ == '__main__':

    cbox = ControlBoxSystem()
    from IPython import embed
    embed()
