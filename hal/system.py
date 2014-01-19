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
from pyelixys.hal.systemobject import SystemObject

from pyelixys.hal.f18 import F18
from pyelixys.hal.reactor import Reactor
from pyelixys.hal.reagentrobot import ReagentRobot


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
    s = main()
    from IPython import embed
    embed()

