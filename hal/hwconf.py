#!/usr/bin/env python

from configobj import ConfigObj
from validate import Validator
import re
from validate import ValidateError


def command_check(vals):
    # Validates the commands in the config file
    #print "Running command check"
    #print vals
    try:
        cmdint = int(vals[0])
    except IndexError:
        raise ValidateError("Command should be list separated by comma, first value should be integer")
    
    except ValueError:
        raise ValidateError("Command should be integer")
    
    try:
        fmtchropts = "xcbB?hHiIlLqQfdspP"
        if not str(vals[1]) in fmtchropts:
            raise ValidateError("Expected format character value: %s" % fmtchropts)
        fmtchr = str(vals[1])
    except IndexError:
        raise ValidateError("Command should be list separated by comma, second value should be character")
    #print vals
    
    return cmdint, fmtchr
    #raise ValidateError('A list was passed when an email address was expected')
    
configspec = "hwconfspec.ini"
configfile = "hwconf.ini"
config = ConfigObj(configfile, configspec=configspec)
validator = Validator({'command': command_check})
results = config.validate(validator,preserve_errors=True)