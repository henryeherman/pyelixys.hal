#!/usr/env python
""" The system model is the highest level
of abstraction of the system.  Everything should only
access the hardware through this object.
The sub system classes such as the gripper,
gas transfer, stopcocks, reactors and reagent robots,
are also locate in this module
"""
import sys
sys.path.append("../")
sys.path.append("./")
from hwconf import config
from logs import hallog as log
from hal import SynthesizerHAL
from elixysobject import ElixysObject
import time

class SystemObject(ElixysObject):
    """ All higher level systems inherit
    from this object and gain access to the
    Synthesizer abstraction of the hardware """

    def __init__(self, synthesizer):
        self.synth = synthesizer

class Gripper(SystemObject):
    """ The gripper can go up, down
    or open and close.  You can query
    whether it is down or closed.
    """
    def __init__(self, synthesizer):
        super(Gripper, self).__init__(synthesizer)

    def open(self):
        """ Open the gripper """
        pass

    def close(self):
        """ Close the gripper """
        pass

    def lift(self):
        """ Move gripper up """
        pass

    def lower(self):
        """ Move the gripper down """
        pass

    def _is_open(self):
        """ Check if the gripper is open """
        pass

    def _is_closed(self):
        """ Check if the gripper is closed """
        pass

    def _is_up(self):
        """ Check if the gripper is up """
        pass

    def _is_down(self):
        """ Check id the gripper is down """
        pass

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

    def lift(self):
        """ Move the gas transfer axis up """
        pass

    def lower(self):
        """ Move the gas transfer axis down """
        pass

    def _is_up(self):
        """ Check that the actuator is up """
        pass

    def _is_down(self):
        """ Check that the actuator is down """
        pass

    is_up = property(_is_up)
    is_down = property(_is_down)

    def start_transfer(self):
        """ Turn on the transfer valve """
        pass

    def stop_transfer(self):
        """ Turn off the transfer valve """
        pass


class Stopcock(SystemObject):
    """ The Elixys system has nine stopcock valves,
    three per reactor. It is possible to turn them clockwise
    or counter clockwise, and check the state. """
    def __init__(self, devid, synthesizer):
        super(Stopcock, self).__init__(synthesizer)
        self.id_ = devid

    def turn_clockwise(self):
        """ Turn the stopcock clockwise """
        pass

    def turn_counter_clockwise(self):
        """ Turn the stopcock counter clockwise """
        pass

    def _is_counter_clockwise(self):
        """ Check if the stopcock is clockwise """
        pass

    def _is_clockwise(self):
        """ Check if the stopcock is counter clockwise """
        pass

    is_counter_clockwise = property(_is_counter_clockwise)
    is_clockwise = property(_is_clockwise)



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
        self._up_valve_id = self.conf['Valves']['up']
        self._down_valve_id = self.conf['Valves']['down']
        self._up_sensor_id = self.conf['Sensors']['up']
        self._down_sensor_id = self.conf['Sensors']['down']
    
    def get_conf(self):
        return self.sysconf['Reactors']['Reactor%d' % self.id_]                

    conf = property(get_conf)

    def lift(self):
        """ Move the reactor up """
        log.debug("Reactor %d lift | Turn on valve:%d, Turn off valve:%d" % 
                (self.id_, self._up_valve_id, self._down_valve_id))
        self.synth.valves[self._down_valve_id].on = False
        time.sleep(0.2)
        self.synth.valves[self._up_valve_id].on = True


    def lower(self):
        """ Move the reactor down """
        log.debug("Reactor %d lower | Turn on valve:%d, Turn off valve:%d" % 
                (self.id_, self._down_valve_id, self._up_valve_id))
        self.synth.valves[self._up_valve_id].on = False
        time.sleep(0.2)
        self.synth.valves[self._down_valve_id].on = True


    def _is_up(self):
        """ Check if reactor is up """
        pass

    def _is_down(self):
        """ Check if reactor is down """
        pass

    is_up = property(_is_up)
    is_down = property(_is_down)

class System(SystemObject):
    """ The system object is an abstraction of the
    elixys hardware and organizes the method calls
    and status information so that a user can directly
    access the hardware according to the physical
    mechanisms on the synthesize, i.e. Reactors,
    Gas Transfer, Gripper, Reagent Delivery, and etc.
    """
    def __init__(self, synthesizer):
        super(System, self).__init__(synthesizer)
        reactors_conf = self.sysconf['Reactors']
        self.reactors = []
        for reactor_section in reactors_conf.sections:
            reactor_id = reactors_conf[reactor_section]['id']
            self.reactors.append(Reactor(reactor_id, synthesizer))



def main():
    """ Main function called when executing this script """
    synth = SynthesizerHAL()
    system = System(synth)
    return system

if __name__ == '__main__':
    pass
