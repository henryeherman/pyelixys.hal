#!/usr/bin/env python
""" The system model is the highest level
of abstraction of the stopcock system.
Everything should only access the stopcocks
access the this object, which is attached to the
reactor objects.
The sub system allows you to rotate the
stopcocks either clockwise or counter clockwise.
"""
import time
from pyelixys.logs import hallog as log
from pyelixys.hal.systemobject import SystemObject


class Stopcock(SystemObject):
    """ The Elixys system has nine stopcock valves,
    three per reactor. It is possible to turn them clockwise
    or counter clockwise, and check the state. """
    def __init__(self, devid, synthesizer):
        super(Stopcock, self).__init__(synthesizer)
        self.id_ = devid
        self._cw_valve_id = self.conf['Valves']['CW']
        self._ccw_valve_id = self.conf['Valves']['CCW']

    def turn_clockwise(self):
        """ Turn the stopcock clockwise """
        log.debug("Turn stopcock %d clockwise", self.id_)
        self.synth.valves[self._ccw_valve_id].on = False
        time.sleep(0.2)
        self.synth.valves[self._cw_valve_id].on = True
        time.sleep(0.2)

    def turn_counter_clockwise(self):
        """ Turn the stopcock counter clockwise """
        log.debug("Turn stopcock %d counter-clockwise", self.id_)
        self.synth.valves[self._cw_valve_id].on = False
        time.sleep(0.2)
        self.synth.valves[self._ccw_valve_id].on = True
        time.sleep(0.2)

    def _is_counter_clockwise(self):
        """ Check if the stopcock is clockwise """
        return self.synth.valves[self._cw_valve_id].on

    def _is_clockwise(self):
        """ Check if the stopcock is counter clockwise """
        return self.synth.valves[self._ccw_valve_id].on

    is_counter_clockwise = property(_is_counter_clockwise)
    is_clockwise = property(_is_clockwise)

    def _get_conf(self):
        """ Return the stopcock configuraton """
        return self.sysconf['Stopcocks']['Stopcock%d' % self.id_]

    conf = property(_get_conf)
