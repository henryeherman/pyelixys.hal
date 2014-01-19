#!/usr/env python
""" The gas tansfer model allow you to control
the gas transfer head, lift, lower, open, close,
transfer on or transfer off.  It also give access
to all the position sensors on the gas transfer head.
"""
import time
from pyelixys.logs import hallog as log
from pyelixys.hal.pneumaticactuator import PneumaticActuator

class GasTransfer(PneumaticActuator):
    """ Gas Transfer gives access to
    pnuematic actuator and gas transfer valve
    """
    def __init__(self, synthesizer):
        super(GasTransfer, self).__init__(synthesizer)

        # Get valve ids
        self._transfer_valve_id = self.conf['Valves']['transfer']

    def _get_conf(self):
        return self.sysconf['GasTransfer']

    conf = property(_get_conf)

    def start_transfer(self):
        """ Turn on the transfer valve """
        self.synth.valves[self._transfer_valve_id].on = True
        time.sleep(0.2)

    def stop_transfer(self):
        """ Turn off the transfer valve """
        self.synth.valves[self._transfer_valve_id].on = False
        time.sleep(0.2)
