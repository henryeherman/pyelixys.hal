#!/usr/env python
""" The Gripper model allows you to
lift, lower, open, and close the gripper,
It is also possible to check the open, close,
up and down sensor.
"""
import time
from datetime import timedelta
from datetime import datetime

from pyelixys.logs import hallog as log
from pyelixys.hal.hal import SynthesizerHAL
from pyelixys.hal.pneumaticactuator import PneumaticActuator

class Gripper(PneumaticActuator):
    """ The gripper can go up, down
    or open and close.  You can query
    whether it is down or closed.
    """
    def __init__(self, synthesizer):

        # Initialize the pneumaticactuator and
        #  the systemobject
        super(Gripper, self).__init__(synthesizer)

        # Get valve ids
        self._open_valve_id = self.conf['Valves']['open']
        self._close_valve_id = self.conf['Valves']['close']

        # Get sensor ids
        self._open_sensor_id = self.conf['Sensors']['open']
        self._close_sensor_id = self.conf['Sensors']['close']

    def _get_conf(self):
        return self.sysconf['Gripper']

    conf = property(_get_conf)

    def open(self):
        """ Open the gripper and make sure it opens """
        for i in xrange(self.conf['retry_count']):
            begintime = datetime.now()
            self.open_no_check()
            while self.timeout > datetime.now() - begintime:
                time.sleep(0.1)
                if self.is_open:
                    log.debug("Open actuator %s success", repr(self))
                    return

            log.info("Failed to open actautor %s before timeout, retry %d",
                        repr(self), i)
        log.error("Failed to open actuator %s after retrys", repr(self))
        #raise ElixysPneumaticError("Failed to open %s" % repr(self))

    def open_no_check(self):
        """ Open the gripper and don't check sensors"""
        log.debug("Gripper Open | Turn on valve:%d, Turn off valve:%d",
                self._open_valve_id, self._close_valve_id)
        self.synth.valves[self._close_valve_id].on = False
        time.sleep(0.2)
        self.synth.valves[self._open_valve_id].on = True
        time.sleep(0.2)

    def close(self):
        """ Close the gripper and make sure it closes """
        for i in xrange(self.conf['retry_count']):
            begintime = datetime.now()
            self.close_no_check()
            while self.timeout > datetime.now() - begintime:
                time.sleep(0.1)
                if self.is_closed:
                    log.debug("Close actuator %s success", repr(self))
                    return
            log.info("Failed to close actuator %s before timeout, retry %d",
                        repr(self), i)
        log.error("Failed to close actuator %s after retrys", repr(self))
        #raise ElixysPneumaticError("Failed to close %s" % repr(self))

    def close_no_check(self):
        """ Close the gripper and don't check the sensors """
        log.debug("Gripper Close | Turn off valve:%d, Turn on valve:%d",
                self._open_valve_id, self._close_valve_id)
        self.synth.valves[self._open_valve_id].on = False
        time.sleep(0.2)
        self.synth.valves[self._close_valve_id].on = True
        time.sleep(0.2)

    def _is_open(self):
        """ Check if the gripper is open """
        return self.synth.digital_inputs[self._open_sensor_id]

    def _is_closed(self):
        """ Check if the gripper is closed """
        return self.synth.digital_inputs[self._close_sensor_id]

    is_open = property(_is_open)
    is_closed = property(_is_closed)
