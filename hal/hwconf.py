#!/usr/bin/env python

from configobj import ConfigObj
from validate import Validator

configspec = "hwconfspec.ini"
configfile = "hwconf.ini"
config = ConfigObj(configfile, configspec=configspec)
validator = Validator()
results = config.validate(validator, preserve_errors=True)