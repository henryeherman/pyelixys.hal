#!/usr/env python
""" The system model is the highest level
of abstraction of the system.  Everything should only
access the hardware through this object.
The sub system classes such as the gripper,
gas transfer, stopcocks, reactors and reagent robots,
are also locate in this module
"""
import time
from pyelixys.logs import hallog as log
from pyelixys.hal.hal import SynthesizerHAL
from pyelixys.hal.elixysobject import ElixysObject

class SystemObject(ElixysObject):
    """ All higher level systems inherit
    from this object and gain access to the
    Synthesizer abstraction of the hardware
    """

    def __init__(self, synthesizer):
        self.synth = synthesizer

    def __str__(self):
        if hasattr(self,'id_'):
            return "<Elixys:%s(%d)>" % (self.__class__.__name__, self.id_)
        else:
            return "<Elixys:%s()>" % self.__class__.__name__

    def __repr__(self):
        return str(self)

class Gripper(SystemObject):
    """ The gripper can go up, down
    or open and close.  You can query
    whether it is down or closed.
    """
    def __init__(self, synthesizer):
        super(Gripper, self).__init__(synthesizer)
        self.conf = self.sysconf['Gripper']
        
        # Get valve ids
        self._open_valve_id = self.conf['Valves']['open']
        self._close_valve_id = self.conf['Valves']['close']
        self._up_valve_id = self.conf['Valves']['up']
        self._down_valve_id = self.conf['Valves']['down']

        # Get sensor ids
        self._up_sensor_id = self.conf['Sensors']['up']
        self._down_sensor_id = self.conf['Sensors']['down']
        self._open_sensor_id = self.conf['Sensors']['open']
        self._close_sensor_id = self.conf['Sensors']['close']


    def open(self):
        """ Open the gripper """
        log.debug("Gripper Open | Turn on valve:%d, Turn off valve:%d",
                self._open_valve_id, self._close_valve_id)
        self.synth.valves[self._close_valve_id].on = False
        time.sleep(0.2)
        self.synth.valves[self._open_valve_id].on = True
        time.sleep(0.2)

    def close(self):
        """ Close the gripper """
        log.debug("Gripper Close | Turn off valve:%d, Turn on valve:%d",
                self._open_valve_id, self._close_valve_id)
        self.synth.valves[self._open_valve_id].on = False
        time.sleep(0.2)
        self.synth.valves[self._close_valve_id].on = True
        time.sleep(0.2)

    def lift(self):
        """ Move gripper up """
        log.debug("Gripper Lift | Turn off valve:%d, Turn on valve:%d",
                self._down_valve_id, self._up_valve_id)
        self.synth.valves[self._down_valve_id].on = False
        time.sleep(0.2)
        self.synth.valves[self._up_valve_id].on = True
        time.sleep(0.2)

    def lower(self):
        """ Move the gripper down """
        log.debug("Gripper Lower | Turn off valve:%d, Turn on valve:%d",
                self._up_valve_id, self._down_valve_id)
        self.synth.valves[self._up_valve_id].on = False
        time.sleep(0.2)
        self.synth.valves[self._down_valve_id].on = True
        time.sleep(0.2)

    def _is_open(self):
        """ Check if the gripper is open """
        return self.synth.digital_inputs[self._open_sensor_id]

    def _is_closed(self):
        """ Check if the gripper is closed """
        return self.synth.digital_inputs[self._close_sensor_id]

    def _is_up(self):
        """ Check if the gripper is up """
        return self.synth.digital_inputs[self._up_sensor_id]

    def _is_down(self):
        """ Check id the gripper is down """
        return self.synth.digital_inputs[self._down_sensor_id]

    is_open = property(_is_open)
    is_closed = property(_is_closed)
    is_up = property(_is_up)
    is_down = property(_is_down)

class GasTransfer(SystemObject):
    """ Gas Transfer gives access to
    pnuematic actuator and gas transfer valve
    """
    def __init__(self, synthesizer):
        super(GasTransfer, self).__init__(synthesizer)
        self.conf = self.sysconf['GasTransfer']

        # Get valve ids
        self._up_valve_id = self.conf['Valves']['up']
        self._down_valve_id = self.conf['Valves']['down']
        self._transfer_valve_id = self.conf['Valves']['transfer']

        # Get sensor ids
        self._up_sensor_id = self.conf['Sensors']['up']
        self._down_sensor_id = self.conf['Sensors']['down']

    def lift(self):
        """ Move the gas transfer axis up """
        log.debug("Gas Transfer Lift | Turn off valve:%d, Turn on valve:%d",
                 self._down_valve_id, self._up_valve_id)
        self.synth.valves[self._down_valve_id].on = False
        time.sleep(0.2)
        self.synth.valves[self._up_valve_id].on = True
        time.sleep(0.2)

    def lower(self):
        """ Move the gas transfer axis down """
        log.debug("Gas Transfer Lower | Turn off valve:%d, Turn on valve:%d",
                self._up_valve_id, self._down_valve_id)
        self.synth.valves[self._up_valve_id].on = False
        time.sleep(0.2)
        self.synth.valves[self._down_valve_id].on = True
        time.sleep(0.2)

    def _is_up(self):
        """ Check that the actuator is up """
        return self.synth.digital_inputs[self._up_sensor_id]

    def _is_down(self):
        """ Check that the actuator is down """
        return self.synth.digital_inputs[self._down_sensor_id]

    is_up = property(_is_up)
    is_down = property(_is_down)

    def start_transfer(self):
        """ Turn on the transfer valve """
        self.synth.valves[self._transfer_valve_id].on = True
        time.sleep(0.2)

    def stop_transfer(self):
        """ Turn off the transfer valve """
        self.synth.valves[self._transfer_valve_id].on = False
        time.sleep(0.2)


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


class Reactor(SystemObject):
    """ The Elixys System has three reactors,
    each reactor is composed of 3 stopcocks,
    a temperature controller, a linear actuator
    and a pnuematic actuator. These sub-features
    can be controller via this object.
    """
    def __init__(self, devid, synthesizer):
        super(Reactor, self).__init__(synthesizer)
        self.id_ = devid

        # Get valve ids
        self._up_valve_id = self.conf['Valves']['up']
        self._down_valve_id = self.conf['Valves']['down']

        # Get sensor ids
        self._up_sensor_id = self.conf['Sensors']['up']
        self._down_sensor_id = self.conf['Sensors']['down']
        
        # Initialize the stopcocks
        self._stopcock_ids = self.conf['stopcock_ids']
        self.stopcocks = [Stopcock(id_, synthesizer)
                            for id_ in self._stopcock_ids]

        # Gain access to the F18 valve
        self.f18 = F18(synthesizer)

    def _get_conf(self):
        """ Get the reactor config for reactor with this id"""
        return self.sysconf['Reactors']['Reactor%d' % self.id_]

    conf = property(_get_conf)

    def lift(self):
        """ Move the reactor up """
        log.debug("Reactor %d lift | Turn on valve:%d, Turn off valve:%d",
                self.id_, self._up_valve_id, self._down_valve_id)
        self.synth.valves[self._down_valve_id].on = False
        time.sleep(0.2)
        self.synth.valves[self._up_valve_id].on = True


    def lower(self):
        """ Move the reactor down """
        log.debug("Reactor %d lower | Turn on valve:%d, Turn off valve:%d",
                self.id_, self._down_valve_id, self._up_valve_id)
        self.synth.valves[self._up_valve_id].on = False
        time.sleep(0.2)
        self.synth.valves[self._down_valve_id].on = True

    def turn_f18_transfer_on(self):
        """ Turn on F18 valve """
        self.f18.turn_on()


    def turn_f18_transfer_off(self):
        """ Turn off f18 valve """
        self.f18.turn_off()

    def _is_up(self):
        """ Check if reactor is up """
        return self.synth.digital_inputs[self._up_sensor_id]

    def _is_down(self):
        """ Check if reactor is down """
        return self.synth.digital_inputs[self._down_sensor_id]
        pass

    is_up = property(_is_up)
    is_down = property(_is_down)


class ReagentRobot(SystemObject):
    """ The Elixys Reagent Robot allows the user to
    select reagents using the gripper and gas transfer.
    An X-Y table allows the selection of positions.
    """
    def __init__(self, synthesizer):
        super(ReagentRobot, self).__init__(synthesizer)

        # Create the Gas Transfer
        self.gas_transfer = GasTransfer(synthesizer)

        # Create Gripper
        self.gripper = Gripper(synthesizer)



class System(SystemObject):
    """ The system object is an abstraction of the
    elixys hardware and organizes the method calls
    and status information so that a user can directly
    access the hardware according to the physical
    mechanisms on the synthesize, i.e. Reactors,
    Gas Transfer, Gripper, Reagent Delivery, and etc.
    """
    def __init__(self):

        # Initialize the hw api
        synthesizer = SynthesizerHAL()

        # Call the constructor
        super(System, self).__init__(synthesizer)

        # Read Reactor configs and create reactors
        reactors_conf = self.sysconf['Reactors']
        self.reactors = []
        for reactor_section in reactors_conf.sections:
            reactor_id = reactors_conf[reactor_section]['id']
            self.reactors.append(Reactor(reactor_id, synthesizer))

        # Create a reagent delivery robot
        self.reagent_robot = ReagentRobot(synthesizer)

        # Give top level system object access to F18 valve
        self.f18 = F18(synthesizer)


def main():
    """ Main function called when executing this script """
    system = System()
    return system

if __name__ == '__main__':
    pass
