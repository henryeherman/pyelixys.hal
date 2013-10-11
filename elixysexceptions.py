#!/usr/bin/env python
import sys
from hwconf import config
from logs import errorlog as log

class ElixysError(Exception):
    pass
    
class ElixysHALError(ElixysError):
    pass
    
class ElixysValidationError(ElixysError):
    pass
    
