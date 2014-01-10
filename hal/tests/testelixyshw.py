import sys
import time
import signal
import thread
sys.path.append("./")
sys.path.append("../")

import websocket
from websocket import ABNF

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
        self.cb_map = {}
        
        
        # Setup Callbacks for Mixer commands
        self.register_callback('Mixers',
                               'set_period', 
                               self.mixers_set_period)
        
        self.register_callback('Mixers',
                               'set_duty_cycle',
                               self.mixers_set_duty_cycle)
        
        # Setup Callbacks for Valve commands
        self.register_callback('Valves',
                               'set_state0',
                               self.valves_set_state0)

        self.register_callback('Valves',
                               'set_state1',
                               self.valves_set_state1)
        
        self.register_callback('Valves',
                               'set_state2',
                               self.valves_set_state2)

        # Setup Callbacks for Temperature controllers
        self.register_callback('TemperatureControllers',
                               'set_setpoint',
                               self.tempctrl_set_setpoint)
        
        self.register_callback('TemperatureControllers',
                               'turn_on',
                               self.tempctrl_turn_on)
 
        self.register_callback('TemperatureControllers',
                               'turn_off',
                               self.tempctrl_turn_off)
 
        # Setup Callbacks for SMC Intrefaces
        self.register_callback('SMCInterfaces',
                               'set_analog_out',
                               self.smcinterfaces_set_analog_out)
        
        # Setup Callbacks for Fans
        self.register_callback('Fans',
                               'turn_on',
                               self.fans_turn_on)

        self.register_callback('Fans',
                               'turn_off',
                               self.fans_turn_off)


        self.register_callback('LinearActuators',
                               'set_requested_position',
                               self.linacts_set_requested_position)

        self.register_callback('LinearActuators',
                               'home_axis',
                               self.linacts_home_axis)

    def register_callback(self,sub_sys,cmd_name, fxn):
        cmd_id, param_fmt = self.lookup_cmd(sub_sys,cmd_name)
        self.cb_map[cmd_id] = (fxn, param_fmt)

    def lookup_cmd(self, sub_sys, cmd_name):
        return self.sysconf[sub_sys]['Commands'][cmd_name]

    def run_callback(self, name=None, *args, **kwargs):
        pass
        #return func(*args, kwargs)

    def mixers_set_period(self, devid, period):
        pass

    def mixers_set_duty_cycle(self, devid, duty):
        pass

    def valves_set_state0(self, devid, state):
        pass

    def valves_set_state1(self, devid, state):
        pass

    def valves_set_state2(self, devid, state):
        pass

    def tempctrl_set_setpoint(self, devid, value):
        pass

    def tempctrl_turn_on(self, devid, value=None):
        pass

    def tempctrl_turn_off(self, devid, value=None):
        pass

    def smcinterfaces_set_analog_out(self, devid, value):
        pass

    def fans_turn_on(self, devid, value=None):
        pass

    def fans_turn_off(self, devid, value=None):
        pass

    def linacts_set_requested_position(self, devid, position):
        pass

    def linacts_home_axis(self, devid, value=None):
        pass


    

e = ElixysSimulator()
simstatus = e.stat

def on_message(ws, message):
    """ When test client receives a command print it to console """

    print "FROM SERVER: %s" % repr(message)


def on_error(ws, error):
    """ If we have a communication error print it to console """

    print error


def on_close(ws):
    """ If websocket hardware server closes the connection print to console """
    print "### closed ###"


def on_open(ws):
    """ On opening a new connection to the websocket server take the
    test_data increment the packet_id and send it to the server as
    a status packet.  This is done in a thread so the main thread
    can still receive the incoming command packets and print them to
    the console """
    i = 0
    def run(*args):
        i = 0
        while True:
            #print "Sent packet id: #%d" % i
            pkt = e.stat.generate_packet()
            ws.send(pkt, ABNF.OPCODE_BINARY)
            time.sleep(.2)
            i+=1
        #ws.close()
        #print "thread terminating..."
    thread.start_new_thread(run, ())


def exit_gracefully(signum, frame):
    """ If requested by signal, exit gracefully """
    print "Exit Gracefully, Ctrl+C pressed"
    sys.exit(0)



if __name__ == "__main__":

    # Setup signal callback
    signal.signal(signal.SIGINT, exit_gracefully)  

     #websocket.enableTrace(True) # Enable for websocket trace!
    ws = websocket.WebSocketApp("ws://localhost:8888/ws",
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    thread.start_new_thread(ws.run_forever,())

