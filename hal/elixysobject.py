#!/usr/bin/env python
import sys
from hwconf import config

class ElixysObject(object):
    """Parent object for all elixys systems
    All onjects can therefore access the system
    config and status
    """
    sysconf = config
    status_ = None

    def get_status(self):
        """ Get the current system state """
        return self.status_

    status = property(get_status,
                      doc="Access the system status")