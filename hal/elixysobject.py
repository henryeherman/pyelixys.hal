#!/usr/bin/env python
import sys
from pyelixys.hal.hwconf import config

class ElixysObject(object):
    """Parent object for all elixys systems
    All onjects can therefore access the system
    config and status
    """
    sysconf = config
        
