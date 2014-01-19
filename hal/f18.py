#!/usr/env python
""" The system model is the highest level
of abstraction of F18 injection valve system.
Everything should only access it through this object.
Each reactor has access to this object.
"""
import time
from pyelixys.logs import hallog as log
from pyelixys.hal.systemobject import SystemObject


class F18(SystemObject):
    """ F18 object controls the enterance of F18
    into the synthesizer.  A valve pressurizes a vessel,
    while a stopcock valve control the path, either waste
    or the reactor 1 vial.
    """
    def __init__(self, synthesizer):
        super(F18, self).__init__(synthesizer)
        self.conf = self.sysconf['F18']
        self._valve_id = self.conf['Valves']['transfer']

    def turn_on(self):
        """ Turn on the F18 transfer valve """
        log.debug("Turn on F18 transfer valve")
        self.synth.valves[self._valve_id].on = True
        time.sleep(0.2)

    def turn_off(self):
        """ Turn off the F18 transfer valve """
        log.debug("Turn off F18 transfer valve")
        self.synth.valves[self._valve_id].on = False
        time.sleep(0.2)

    def _is_on(self):
        """ Is F18 transfer valve on """
        return self.synth.valve[self._valve_id].on

    def _is_off(self):
        """ Is F18 transfer valve off """
        return not self.synth.valve[self._valve_id].on

    is_on = property(_is_on)
    is_off = property(_is_off)
