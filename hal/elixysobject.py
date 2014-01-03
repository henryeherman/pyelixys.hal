#!/usr/bin/env python
import sys
from hwconf import config
#from wsserver import status, wscomproc, cmd_lookup

class ElixysObject(object):
    """Parent object for all elixys systems
    All onjects can therefore access the system
    config and status
    """
    sysconf = config
        