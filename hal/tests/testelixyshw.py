import sys
import time
import signal
import thread
sys.path.append("./")
sys.path.append("../")
from status import Status

from elixysobject import ElixysObject



import collections

class StatusSimulator(Status):
    def __init__(self, *args, **kwargs):
        super(StatusSimulator, self).__init__(self, *args, **kwargs)
        self.is_valid = True 
        # Initialize heaters
        self['Heaters'] = {'state':0}

        # Initialize Linear Actuators
        linacts = []
        self['LinearActuators'] = dict()
        for i in range(self.sysconf['LinearActuators']['count']):
            linact = {'error_code': 0,
                      'position': 0,
                      'requested_position':0}
                    
            self.store['LinearActuators'][i] = linact
            linacts.append(linact)

        self['LinearActuators']['Subs'] = linacts
        self['LinearActuators']['count'] = self.sysconf['LinearActuators']['count']
        
        # Initialize SMC Interfaces
        smcinterfaces = []
        self.store['SMCInterfaces'] = {}
        for i in range(self.sysconf['SMCInterfaces']['count']):
            smcinterface = {'analog_in':0.0,
                            'analog_out':0.0}
            self.store['SMCInterfaces'][i] = smcinterface
            smcinterfaces.append(smcinterface)
        
        self.store['SMCInterfaces']['Subs'] = smcinterfaces
        self.store['SMCInterfaces']['count'] = self.sysconf['SMCInterfaces']['count']
        self.store['SMCInterfaces']['error_code'] = '\x00'

        # Initialize Thermocouples
        thermocouples = []
        self.store['Thermocouples'] = {}
        for i in range(self.sysconf['Thermocouples']['count']):
            thermocouple = {'error_code': '\x00',
                            'temperature':25.0}
            self.store['Thermocouples'][i] = thermocouple
            thermocouples.append(thermocouple)

        self.store['Thermocouples']['Subs'] = thermocouples
        self.store['Thermocouples']['count'] = self.sysconf['Thermocouples']['count']

        #  Initialize AUX Thermocouples
        auxthermocouples = []
        self.store['AuxThermocouples'] = {}
        for i in range(self.sysconf['AuxThermocouples']['count']):
            auxthermocouple = {'error_code': '\x00',
                            'temperature':25.0}
            self.store['AuxThermocouples'][i] = auxthermocouple
            auxthermocouples.append(auxthermocouple)

        self.store['AuxThermocouples']['Subs'] = auxthermocouples
        self.store['AuxThermocouples']['count'] = self.sysconf['AuxThermocouples']['count']
        
        # Initialize Liquid Sensors
        liqsensors = []
        self.store['LiquidSensors'] = {}
        for i in range(self.sysconf['LiquidSensors']['count']):
            liqsensor = {'analog_in':0.0}
            self.store['LiquidSensors'][i] = liqsensor
            liqsensors.append(liqsensor)

        self.store['LiquidSensors']['Subs'] = liqsensors
        self.store['LiquidSensors']['count'] = self.sysconf['LiquidSensors']['count']
        self.store['LiquidSensors']['error_code'] = '\x00'


        # Initialize Header
        self.store['Header'] = {}
        self.store['Header']['packet_id'] = 0
        self.store['Header']['packet_type'] = 63
        self.store['Header']['system_error_code'] = 0

        # 
        

class ElixysSimulator(ElixysObject):

    def __init__(self):
        self.stat = Status()


if __name__ == "__main__":
    pass
