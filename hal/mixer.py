#!/usr/bin/env python
""" The Mixer allows Class allows the
the mixer motor speed to be controlled
"""
import time
from pyelixys.logs import hallog as log
from pyelixys.hal.systemobject import SystemObject

class Mixer(SystemObject):
    """ The Elixys Mixer controls the PWM
    on the Synthesizer board and is used to
    drive the 24V stir mixer motors.
    While their are actually four mixers on the
    system only 3 are used.  Each reactor object
    has a corresponding Mixer instance.
    """
    def __init__(self, devid, synthesizer):
        super(Mixer, self).__init__(synthesizer)

        self.id_ = devid
        self._mixer = self.synth.mixer_motors[self.id_]

    def set_duty_cycle(self, value):
        """ Sets duty cycle on mixer,
        MAX is 1.0, Min is 0.0 """
        self._mixer.duty_cycle = value

    def get_duty_cycle(self):
        """ Retrieve Mixer duty cycle """
        return self._mixer.duty_cycle

    duty_cycle = property(get_duty_cycle, set_duty_cycle)

