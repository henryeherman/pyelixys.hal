#!/usr/bin/env python
""" A pnuematic actuator controls and up and a down valve,
it also generally has an up an down sensor.
The current elixys system has 5 of these axis.
Eache reactor, the gripper and the gas transfer inherit from
this object
"""
import time
from datetime import timedelta
from datetime import datetime

from pyelixys.logs import hallog as log
from pyelixys.hal.systemobject import SystemObject
from pyelixys.elixysexceptions import ElixysPneumaticError

class PneumaticActuator(SystemObject):
    """ The PneumaticActuator class has an API,
    that allows the actuator to be lifted, and lowered.
    It provide axis to the sensor data. When lifting or lowering
    a timeout is imported from the config file along with a retry count.
    The object SHOULD have a conf attribute where it can pull
    the valve and sensor ids. The Reactor,
    GasTransfer and Gripper inherit from
    this object.
    """

    def __init__(self, synthesizer):
        super(PneumaticActuator, self).__init__(synthesizer)
        # Get valve ids
        self._up_valve_id = self.conf['Valves']['up']
        self._down_valve_id = self.conf['Valves']['down']

        # Get sensor ids
        self._up_sensor_id = self.conf['Sensors']['up']
        self._down_sensor_id = self.conf['Sensors']['down']
        self.timeout = timedelta(0, self.conf['timeout'])

    def _get_conf(self):
        """ Anything that inherits from the this class you
        create a function that return the device's real
        config, this is intended as virtual """
        return {}

    conf = property(_get_conf)

    def lift(self):
        """ Move the actuator up and ensure it gets there """
        for i in xrange(self.conf['retry_count']):
            begintime = datetime.now()
            self.lift_no_check()
            while self.timeout > datetime.now() - begintime:
                time.sleep(0.1)
                if self.is_up:
                    log.debug("Lift actuator %s success", repr(self))
                    return

            log.info("Failed to raise actautor %s before timeout, retry %d",
                        repr(self), i)
        log.error("Failed to raise actuator %s after retrys", repr(self))
        #raise ElixysPneumaticError("Failed to lift %s" % repr(self))


    def lift_no_check(self):
        """ Lift actuator but don't wait """
        log.debug("Actuator %s lift | Turn on valve:%d, Turn off valve:%d",
                repr(self), self._up_valve_id, self._down_valve_id)
        self.synth.valves[self._down_valve_id].on = False
        time.sleep(0.2)
        self.synth.valves[self._up_valve_id].on = True

    def lower(self):
        """ Lower actuator and unsure it gets there """
        for i in xrange(self.conf['retry_count']):
            begintime = datetime.now()
            self.lower_no_check()
            while self.timeout > datetime.now() - begintime:
                time.sleep(0.1)
                if self.is_down:
                    log.debug("Lower actuator %s success", repr(self))
                    return
            log.info("Failed to raise actuator %s before timeout, retry %d",
                        repr(self), i)
        log.error("Failed to lower actuator %s after retrys", repr(self))
        #raise ElixysPneumaticError("Failed to lower %s" % repr(self))

    def lower_no_check(self):
        """ Move the actuator down but don't wait """
        log.debug("Actuator %s lower | Turn on valve:%d, Turn off valve:%d",
                repr(self), self._down_valve_id, self._up_valve_id)
        self.synth.valves[self._up_valve_id].on = False
        time.sleep(0.2)
        self.synth.valves[self._down_valve_id].on = True

    def _is_up(self):
        """ Check if actuator is up """
        return self.synth.digital_inputs[self._up_sensor_id]

    def _is_down(self):
        """ Check if actuator is down """
        return self.synth.digital_inputs[self._down_sensor_id]

    is_up = property(_is_up)
    is_down = property(_is_down)
