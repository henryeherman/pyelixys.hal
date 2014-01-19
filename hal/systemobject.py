#!/usr/env python
""" The systemobject object all models
inherit from.
"""
import time
from pyelixys.logs import hallog as log
from pyelixys.hal.hal import SynthesizerHAL
from pyelixys.hal.elixysobject import ElixysObject


class SystemObject(ElixysObject):
    """ All higher level systems inherit
    from this object and gain access to the
    Synthesizer abstraction of the hardware
    """

    def __init__(self, synthesizer):
        self.synth = synthesizer

    def __str__(self):
        if hasattr(self,'id_'):
            return "<Elixys:%s(%d)>" % (self.__class__.__name__, self.id_)
        else:
            return "<Elixys:%s()>" % self.__class__.__name__

    def __repr__(self):
        return str(self)
