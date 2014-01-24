#!/usr/bin/env python
""" The TempCtrl allows the user to
set the setpoint and turn on the heaters.
Each TempCtrl is composed of 3 temp controls
on the hardware, and each of these is used
to heat one of the three heaters on each collet.
The Reactor creates a TempCtrl according
to the list of ids in the hwconf.
"""
import time
from pyelixys.logs import hallog as log
from pyelixys.hal.systemobject import SystemObject
import numpy as np

class TempCtrl(SystemObject):
    """ The Elixys TempCtrl, is composed of
    3 HW tempctrls.  On the Synthesizer board,
    this means it monitors the temps of each of
    three thermcouples and can turn on the associated
    temp controllers on the hw.  The actual controllers,
    are implemented in the firmware and control their
    respective AC solid state relays."""
    def __init__(self, devids, synthesizer):
        """ Initialize the TempCtrl """
        super(TempCtrl, self).__init__(synthesizer)

        # This is the devids of the individual
        #  temp ctrls this will control
        self.ids = devids
        all_tempctrls = self.synth.temperature_controllers
        self.tempctrls = [all_tempctrls[i] for i in devids]
        self.set_setpoint(25.0)
        self.turn_off()

    def set_setpoint(self, temp):
        """ Set the setpoint on the temp controls """
        for tc in self.tempctrls:
            tc.setpoint = temp
        self._setpoint = temp

    def get_setpoint(self):
        return self._setpoint

    setpoint = property(get_setpoint, set_setpoint)

    def get_temperatures(self):
        """ Get the temperatures from each controller """
        return [tc.temperature for tc in self.tempctrls]

    def get_temperature(self):
        """ Get the average temperature """
        return np.mean(self.get_temperatures())

    temperature = property(get_temperature)

    def turn_on(self):
        """ Turn on the tempctrls """
        for tc in self.tempctrls:
            tc.on = True

        self._on = True

    def turn_off(self):
        """ Turn off the tempctrls """
        for tc in self.tempctrls:
            tc.on = False

        self._on = False

    def set_on(self, value):
        for tc in self.tempctrls:
            tc.on = value

    def get_on(self):
        return self._on

    on = property(get_on, set_on)
