import sys
import time
import signal
import thread
sys.path.append("./")
sys.path.append("../")
from status import Status

from elixysobject import ElixysObject


class ElixysSimulator(ElixysObject):

    def __init__(self):
        self.stat = Status()


if __name__ == "__main__":
    pass
