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
        
        # Initialize Header
        self.store['Header'] = {}
        self.store['Header']['packet_id'] = 0
        self.store['Header']['packet_type'] = 63
        self.store['Header']['system_error_code'] = 0

        # Initialize Mixers
        mixers = []
        self.store['Mixers'] = {}
        for i in range(self.sysconf['Mixers']['count']):
            mixer = {'duty_cycle':0.0, 'period': 0}
            self.store['Mixers'][i] = mixer
            mixers.append(mixer)
        
        self.store['Mixers']['Subs'] = mixers
        self.store['Mixers']['count'] = \
                self.sysconf['Mixers']['count']
        self.store['Mixers']['error_code'] = '\x00'
        self.store


        # Initialize Valves
        self.store['Valves'] = {}
        self.store['Valves']['error_code'] = '\x00'
        self.store['Valves']['state0'] = 0
        self.store['Valves']['state1'] = 0
        self.store['Valves']['state2'] = 0

        # Initialize Thermocouples
        thermocouples = []
        self.store['Thermocouples'] = {}
        for i in range(self.sysconf['Thermocouples']['count']):
            thermocouple = {'error_code': '\x00',
                            'temperature':25.0}
            self.store['Thermocouples'][i] = thermocouple
            thermocouples.append(thermocouple)

        self.store['Thermocouples']['Subs'] = thermocouples
        self.store['Thermocouples']['count'] = \
                self.sysconf['Thermocouples']['count']

        # Initialize AUX Thermocouples
        auxthermocouples = []
        self.store['AuxThermocouples'] = {}
        for i in range(self.sysconf['AuxThermocouples']['count']):
            auxthermocouple = {'error_code': '\x00',
                            'temperature':25.0}
            self.store['AuxThermocouples'][i] = auxthermocouple
            auxthermocouples.append(auxthermocouple)

        self.store['AuxThermocouples']['Subs'] = auxthermocouples
        self.store['AuxThermocouples']['count'] = \
                self.sysconf['AuxThermocouples']['count']
         
        # Initialize heaters
        self['Heaters'] = {'state':0}

        # Initialize Temperature Controllers
        tempctrls = []
        self.store['TemperatureControllers'] = {}
        for i in range(self.sysconf['TemperatureControllers']['count']):
            tempctrl = {'error_code':'\x00', 'setpoint':0.0}
            self.store['TemperatureControllers'][i] = tempctrl
            tempctrls.append(tempctrl)
        
        
        self.store['TemperatureControllers']['error_code'] = 0
        self.store['TemperatureControllers']['Subs'] = tempctrls
        self.store['TemperatureControllers']['count'] = \
                self.sysconf['TemperatureControllers']['count']

        # Initialize SMC Interfaces
        smcinterfaces = []
        self.store['SMCInterfaces'] = {}
        for i in range(self.sysconf['SMCInterfaces']['count']):
            smcinterface = {'analog_in':0.0,
                            'analog_out':0.0}
            self.store['SMCInterfaces'][i] = smcinterface
            smcinterfaces.append(smcinterface)
        
        self.store['SMCInterfaces']['Subs'] = smcinterfaces
        self.store['SMCInterfaces']['count'] = \
                self.sysconf['SMCInterfaces']['count']
        self.store['SMCInterfaces']['error_code'] = '\x00'
 
        # Initialize Fans
        self.store['Fans'] = {}
        self.store['Fans']['state'] = '\x01'

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
        self['LinearActuators']['count'] = \
                self.sysconf['LinearActuators']['count']

        # Initialize Digital Inputs
        self.store['DigitalInputs'] = {}
        self.store['DigitalInputs']['error_code'] = '\x00'
        self.store['DigitalInputs']['state'] = 4095  
        
        # Initialize Liquid Sensors
        liqsensors = []
        self.store['LiquidSensors'] = {}
        for i in range(self.sysconf['LiquidSensors']['count']):
            liqsensor = {'analog_in':0.0}
            self.store['LiquidSensors'][i] = liqsensor
            liqsensors.append(liqsensor)

        self.store['LiquidSensors']['Subs'] = liqsensors
        self.store['LiquidSensors']['count'] = \
                self.sysconf['LiquidSensors']['count']
        self.store['LiquidSensors']['error_code'] = '\x00'

        for key,value in self.store.items():
            setattr(self,key,value)


    def generate_packet_data(self):
        subs = self.fmt.subsystems
        vals = []
        for subname, subcount, subvals in subs:            
            # Top Level params
            ## print "BEGIN:", subname
            topparams = subvals.keys()
            ## print "TOPPARAMS", topparams 
            repeat = False
            if "Repeat" in topparams:
                ## print subname,"REPEAT"
                repeat = True                
                topparams.remove('Repeat')

            ## print "TOPPARAMS", topparams 
            if not topparams is None:
                for topparam in topparams:
                    ## print subname,":",topparam
                    vals.append(self.store[subname][topparam])
            
            if "Repeat" in subvals:                
                for i in range(subcount):
                    for subparam in subvals['Repeat'].keys():                    
                        vals.append(self.store[subname][i][subparam])
                    ## print subname,i,":", subcount, subvals['Repeat'].keys()



        return vals
            

    def generate_packet(self):
        data = self.generate_packet_data()
        fmtstruct = self.fmt.get_struct()
        return fmtstruct.pack(*data)
        #self.store[sub[0]]
             
        

class ElixysSimulator(ElixysObject):

    def __init__(self):
        self.stat = StatusSimulator()


if __name__ == "__main__":
    e = ElixysSimulator()
    simstatus = e.stat
