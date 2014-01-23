#!/usr/bin/env python
#import sys
#from hwconf import config
#from logs import errorlog as log


class ElixysError(Exception):
    pass


class ElixysHALError(ElixysError):
    pass


class ElixysValidationError(ElixysError):
    pass


class ElixysValueError(ElixysError, IndexError):
    pass


class ElixysPneumaticError(ElixysHALError):
    pass

class ElixysCommError(ElixysError):
    pass

class ElixysComportError(ElixysCommError):
    pass

class ElixysCBoxError(ElixysHALError):
    pass
