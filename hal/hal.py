#!/usr/bin/env python
import sys
from pyelixys.hal.hwconf import config
from pyelixys.logs import hallog as log
from pyelixys.hal.elixysobject import ElixysObject
from pyelixys.hal.wsserver import wscomproc, status, cmd_lookup

# All set_methods will send commands to hardware to change state
# they will not return (block( until hardware reflects changes,
# after timeout exception

# Some set_methods (e.g. temperature controller, axis position)
# may return IF the command takes time to complete, these
# commands will have additional flags on the system state they will
# wait for to let us know they are busy
# these special type of commands will be wrapped in additional
# logic that will determine if it fails, i.e. timers, etc.

# All get_methods will read from a special thread safe variable
# system "status" this status will be updated regularly from
# the synthesizer which will stream its state!

# Validation with decorators? Later


class SynthesizerObject(ElixysObject):
    status = status
    cmd_lookup = cmd_lookup
    comproc = wscomproc
    
    def start_com_proc(self):
        if not self.comproc.is_alive():
            log.debug("Starting the Websocket communication process")
            self.comproc.start()
        else:
            log.debug("The Websocket communication process is active")
        
    def stop_com_proc(self):
        self.comproc.stop()
        
                      
class SynthesizerSubObject(SynthesizerObject):
    """ All the subsystems inherit from this object,
    this give them access to their own specific configuration
    option, their own status, and the ability to
    send commands to hardware.
    """
    synthesizer_objects = []
    

    def __init__(self, id, configname=None):
        self.set_id(id)
        self.synthesizer_objects.append(self)
        self.configname = configname
        

    def set_id(self, id_):
        self.id_ = id_

    def get_config(self):
        return self.sysconf.get(self.configname, None)

    config = property(get_config)

    def get_unit_config(self):
        if not self.config is None:
            cfg = self.config.get('Units', None)
            if not cfg is None:
                return cfg.get(str(self.id_), None)
        return None

    unit_conf = property(get_unit_config)

    def __repr__(self):
        return "<%s(%s)>" % (self.__class__.__name__, str(self.id_))


class StateMessageParser(ElixysObject):
    pass


class State(ElixysObject):
    pass


class Mixer(SynthesizerSubObject):
    """ The synthesizer has mixers for agitating
    the contents of the reactors.
    """
    def __init__(self, id):
        super(Mixer, self).__init__(id, "Mixers")
        self.duty_ = 0
        self.period_ = 0
        self.on_ = False

    def set_duty_cycle(self, value):
        log.debug("Set Mixer %d duty cycle -> %f" % (self.id_, value))        
        if value >= 0.0 and value <= 100.0:
            self.duty_ = value
            cmd = self.cmd_lookup['Mixers']['set_duty_cycle'][self.id_](value)
            self.comproc.run_cmd(cmd)
        else:
            # Raise Exception, value out of range!
            log.error("Mixer %d duty cycle -> %f out of range" % (self.id_, value))                
        
    def get_duty_cycle(self):
        log.debug("Get Mixer %d duty cycle -> %f" % (self.id_, self.duty_))
        return self.duty_

    duty_cycle = property(get_duty_cycle, set_duty_cycle,
                          doc="Set duty cycle of mixer motor")

    def set_period(self, value):
        log.debug("Set Mixer %d period -> %f" % (self.id_, value))
        self.period_ = value

    def get_period(self):
        log.debug("Get Mixer %d period -> %f" % (self.id_, self.period_))
        return self.period_

    period = property(get_period, set_period,
                      doc="Period of mixer motor signal")

    def set_on(self, value):
        log.debug("Set Mixer %d on -> %s" % (self.id_, value))
        self.on_ = value
        if value is True:
            self.set_duty_cycle(100.0)
        else:
            self.set_duty_cycle(0.0)

    def get_on(self):
        log.debug("Get Mixer %d on -> %s" % (self.id_, self.on_))
        return self.on_

    on = property(get_on, set_on,
                  doc="Turn the mixer motor on")


class Valve(SynthesizerSubObject):
    """ The system uses pnuematic valves to drive
    actuators, the valve objects give access to
    turn them on or off an monitor the status
    """
    def __init__(self, id):
        super(Valve, self).__init__(id, "Valves")
        self.on_ = False
        Valve.valve_state0 = 0
        Valve.valve_state1 = 0
        Valve.valve_state2 = 0
        
    def set_on(self, value):
        if not hasattr(self,'valve_state0') or not hasattr(self,'valve_state1') \
            or not hasattr(self,'valve_state2'):
            self.load_states()
        log.debug("Set Valve %d on -> %s" % (self.id_, value))
        self.on_ = value
        if self.id_ < 16:
            log.debug("Before Set Valve %d (state0) on -> %s" % (self.id_, bin(Valve.valve_state0)))
            if value is True:
                Valve.valve_state0 |= (1<<(self.id_%16))            
            else:
                Valve.valve_state0 &= ~(1<<(self.id_%16))
            self.comproc.run_cmd(self.cmd_lookup['Valves']['set_state0'](Valve.valve_state0))
            log.debug("After Set Valve %d (state0) on -> %s" % (self.id_, bin(Valve.valve_state0)))
            self.on_ = True
        elif self.id_ < 32:
            if value is True:
                Valve.valve_state1 |= (1<< (self.id_%16))
            else:                
                Valve.valve_state1 &= ~(1<<(self.id_%16))
            self.comproc.run_cmd(self.cmd_lookup['Valves']['set_state1'](Valve.valve_state1))
            log.debug("Set Valve %d (state1) on -> %s" % (self.id_, bin(Valve.valve_state1)))
            self.on_ = True
        elif self.id_ < 48:            
            if value is True:
                Valve.valve_state2 |= (1<< (self.id_%16))                     
            else:                
                Valve.valve_state2 &= ~(1<<(self.id_%16))
            self.comproc.run_cmd(self.cmd_lookup['Valves']['set_state2'](Valve.valve_state2))
            log.debug("Set Valve %d (state2) on -> %s" % (self.id_, bin(Valve.valve_state2)))
            self.on_ = True
           
        
    def get_on(self):        
        if not hasattr(self,'valve_state0') or not hasattr(self,'valve_state1') \
            or not hasattr(self,'valve_state2'):
            self.load_states()
        val = False
        if self.id_ < 16:
            valve_state = self.status.Valves['state0']
            val = bool((valve_state >> self.id_) & 1)
            self.on_ = False
            
        elif self.id_ < 32:
            valve_state = self.status.Valves['state1']
            val = bool((valve_state >> (self.id_ - 16)) & 1)
            self.on_ = False
            
        elif self.id_ < 48:
            valve_state = self.status.Valves['state2']
            val = bool((valve_state >> (self.id_ - 32)) & 1)            
            self.on_ = False
        
        log.debug("Get Valve %d on -> %s" % (self.id_, val))
        
        return val

    on = property(get_on, set_on,
                  doc="Turn valve on")


class Thermocouple(SynthesizerSubObject):
    """ Each reactor has multiple thermocouples to
    monitor the temperature of each individual collet.
    This object is read-only but allows the monitoring
    of the collet temperatures
    """
    def __init__(self, id, configname="Thermocouples"):
        super(Thermocouple, self).__init__(id, configname)
        self.temperature_ = 25.0

    def get_temperature(self):
        log.debug("Get Thermocouple %d temperature -> %f"
                  % (self.id_, self.temperature_))
        self.temperature_ = self.status['Thermocouples'][self.id_]['temperature']
        return self.temperature_  # Checks temp and returns value
        
    temperature = property(get_temperature)


class AuxThermocouple(Thermocouple):
    """ Additional thermocouples are available
    for monitoring user define temperatures such
    as thermocouples place with in the vials
    """
    def __init__(self, id):
        super(AuxThermocouple, self).__init__(id,  "AuxThermocouples")
        
    def get_temperature(self):
        log.debug("Get AuxThermocouple %d temperature -> %f"
                  % (self.id_, self.temperature_))
        self.temperature_ = self.status['AuxThermocouples'][self.id_]['temperature']
        return self.temperature_  # Checks temp and returns value
        
    temperature = property(get_temperature)

class Heater(SynthesizerSubObject):
    """ Each collet has a separate AC heater
    each heater in controlled by a different
    temperature controller. This read-only
    object is used to determine when the heating
    element is active.  It CAN NOT be used to control
    the heater.  TemperatureController objects can turn
    on heaters.  This prevents a user from purposely or
    accidentally generating a 'run away' heater.
    """
    def __init__(self, id):
        super(Heater, self).__init__(id, "Heaters")
        self.on_ = False

    def get_on(self):        
        self.state_ = self.status['Heaters']['state']
        self.on_ = bool(self.state_ >> self.id_ & 1)
        log.debug("Get Heater %d on -> %s" % (self.id_, self.on_))
        return self.on_

    on = property(get_on)


class TemperatureController(SynthesizerSubObject):
    """ Temperature controllers on the hardware link the
    thermocouples to the heater elements and use a feedback
    controller to maintain temperature. This object allows
    you to set the set-point and activate
    or deactivate the controller.
    """
    def __init__(self, id):
        super(TemperatureController, self).__init__(id,
                                                    "TemperatureControllers")

        self.setpoint_ = 25.0
        self.temperature_ = 25.0
        self.on_ = False

    def get_setpoint(self):
        log.debug("Get Temperature Controller %d setpoint -> %f"
                  % (self.id_, self.setpoint_))
        self.setpoint_ = self.status.TemperatureControllers[self.id_]['setpoint']
        return self.setpoint_

    def set_setpoint(self, value):        
        if value > 180.0:
            #Raise exception
            log.debug("Error Temperature Controller %d setpoint -> %f,"
                      "TOO HOT, should be less than 180" 
                      % (self.id_, self.setpoint_))
            return
        self.setpoint_ = value
        log.debug("Set Temperature Controller %d setpoint -> %f"
                  % (self.id_, self.setpoint_))
        cmd = self.cmd_lookup['TemperatureControllers']['set_setpoint'][self.id_](value)
        self.comproc.run_cmd(cmd)
        
    setpoint = property(get_setpoint, set_setpoint,
                        doc="Set the temperature controller setpoint")

    def get_temperature(self):
        log.debug("Get Temperature Controller %d temperature -> %f"
                  % (self.id_, self.temperature_))
        self.temperature_ = self.status.Thermocouples[self.id_]['temperature']
        return self.temperature_

    temperature = property(get_temperature,
                           doc="Get the current temperature")

    def get_on(self):
        log.debug("Get Temperature Controller %d on -> %s"
                  % (self.id_, self.on_))
        errcode = self.status.TemperatureControllers[0]['error_code']
        if errcode == '\x01':
            self.on_ = True
        else:
            self.on_ = False
        return self.on_

    def set_on(self, value):
        log.debug("Set Temperature Controller %d on -> %s"
                  % (self.id_, value))
        self.on_ = value
        if self.on_ is True:
            cmd = self.cmd_lookup['TemperatureControllers']['turn_on'][self.id_]()
        else:
            cmd = self.cmd_lookup['TemperatureControllers']['turn_off'][self.id_]()
        self.comproc.run_cmd(cmd)
    on = property(get_on, set_on,
                  doc="Turn temperature controller on/off")


class SMCInterface(SynthesizerSubObject):
    """ The pressure regulators and vacuum regulators
    allow he users to set the the pressures internal to the unit.
    This object allows you to read the raw ADC and set the DAC
    outputs. Additional methods allow the pressure to the read or set
    in psi.
    """
    def __init__(self, id):
        super(SMCInterface, self).__init__(id, "SMCInterfaces")
        self.analog_out_ = 0        

    def set_analog_out(self, value):
        if not(value >= 0.0 and value <= 10.0):
            # Should raise exception in future!!!!
            log.error("SMC Analog setpoint (%f) out of range" % value)
            return
        self.comproc.run_cmd(self.cmd_lookup['SMCInterfaces']['set_analog_out'][self.id_](value))
        log.debug("Set SMC Analog out %d on -> %s"
                  % (self.id_, value))
        
        self.analog_out_ = value

    def get_analog_out(self):
        log.debug("Get SMC Analog out %d on -> %s"
                  % (self.id_, self.analog_out_))
        self.analog_out_ = self.status.SMCInterfaces[self.id_]['analog_out']
        return self.analog_out_

    analog_out = property(get_analog_out, set_analog_out,
                          doc="Set the analog out 0-10V")

    def get_analog_in(self):        
        vref = self.sysconf['SMCInterfaces']['analog_in_vref'] # Depends on gain set on board!
        self.analog_in_ = self.status.SMCInterfaces[self.id_]['analog_in']
        log.debug("Get SMC RAW Analog in %d on -> %s"
                  % (self.id_, self.analog_in_))
        log.debug("VREF: %f" % vref)
        self.analog_in_ = self.analog_in_ / 4096.0 * vref
        log.debug("Get SMC Analog in %d on -> %s"
                  % (self.id_, self.analog_in_))
        return self.analog_in_
        
    analog_in = property(get_analog_in,
                         doc="Get the analog in 0-5V")


class Fan(SynthesizerSubObject):
    """ Elixys can get hot, lets help it blow off
    some steam by enabling or disabling the fans
    """
    def __init__(self, id):
        super(Fan, self).__init__(id, "Fans")
        self.on_ = False

    def get_on(self):
        log.debug("Get Fan %d on -> %s"
                  % (self.id_, self.on_))
        return self.on_

    def set_on(self, value):
        log.debug("Set Fan %d on -> %s"
                  % (self.id_, value))
        self.on_ = value
        if value is True:
            cmd = self.cmd_lookup['Fans']['turn_on'][self.id_]()
            log.debug("Turn On")
        else:
            log.debug("Turn Off")
            cmd = self.cmd_lookup['Fans']['turn_off'][self.id_]()
        
        self.comproc.run_cmd(cmd)
        
    on = property(get_on, set_on,
                  doc="Turn on/off fan")


class LinearActuator(SynthesizerSubObject):
    """ The system has multiple linear actuators that
    can have their positions set, and read.
    """
    def __init__(self, id):
        super(LinearActuator, self).__init__(id, "LinearActuators")

    def set_position(self, value):
        log.debug("Set Actuator %d Position -> %s"
                  % (self.id_, value))
        self.position_ = value

    def get_position(self):
        log.debug("Get Actuator %d Position -> %s"
                  % (self.id_, self.position_))
        return self.position_

    position = property(get_position, set_position,
                        doc="Set Actuator position")

    def set_home(self, value):
        log.debug("Set Actuator %d Home -> %s"
                  % (self.id_, value))
        self.home_ = value

    def get_home(self):
        log.debug("Get Actuator %d Home -> %s"
                  % (self.id_, self.home_))
        return self.home_

    home = property(get_home, set_home,
                    doc="Tell the axis to home")


class DigitalInput(SynthesizerSubObject):
    """ The pneumatically controlled axis have up/down
    sensors for feedback on position.
    """
    def __init__(self, id):
        super(DigitalInput, self).__init__(id, "DigitalInputs")
        self.tripped_ = False

    def get_tripped(self):        
        self.state_ = self.status.DigitalInputs['state']
        self.tripped_ = not bool(self.state_ >> self.id_ & 1)
        log.debug("Get Digital input %d tripped -> %s"
                  % (self.id_, self.tripped_))
        return self.tripped_

    tripped = property(get_tripped,
                       doc="Check if position sensor tripped")
    
    def __nonzero__(self):
        return self.tripped

    def __bool__(self):
        return self.__nonzero__()

    def all(self):
        self.state_ = self.status.DigitalInputs['state']               
        self.all_state_ = [not bool(self.state_ >> sensorbit & 1) 
            for sensorbit in range(self.sysconf['DigitalInputs']['count'])]
        log.debug("Get Digital input %d tripped -> %s"
                  % (self.id_, self.tripped_))
        return self.all_state_
        

class LiquidSensor(SynthesizerSubObject):
    """ Liquid sensors can be used as feedback on
    the processes
    """
    def __init__(self, id):
        super(LiquidSensor, self).__init__(id, "LiquidSensors")
        self.analog_out_ = 0

    def get_analog_out(self):
        self.analog_out_ = self.status.LiquidSensors[self.id_]['analog_in'] / 4095.0
        log.debug("Get Liquid Sensor Analog in %d on -> %s"
                  % (self.id_, self.analog_out_))                  
        return self.analog_out_

    analog_out = property(get_analog_out,
                          doc="Liquid sensor ADC value")


class SynthesizerHAL(SynthesizerObject):
    """ The is the Synthesizer object giving
    access to all the sub systems.
    """
    def __init__(self):
        
        super(SynthesizerHAL, self).__init__()        
        
        log.debug("Initializing SynthesizerHAL")
        self.mixer_motors = [Mixer(i) for i in
                             range(self.sysconf['Mixers']['count'])]
        self.valves = [Valve(i) for i in
                       range(self.sysconf['Valves']['count'])]
        self.thermocouples = [Thermocouple(i) for i in
                              range(self.sysconf['Thermocouples']['count'])]
        self.aux_thermocouples = [
            AuxThermocouple(i) for i in
            range(self.sysconf['AuxThermocouples']['count'])]

        self.heaters = [Heater(i) for i in
                        range(self.sysconf['Heaters']['count'])]

        self.temperature_controllers = [
            TemperatureController(i) for i in
            range(self.sysconf['TemperatureControllers']['count'])]

        self.smc_interfaces = [SMCInterface(i) for i in
                               range(self.sysconf['SMCInterfaces']['count'])]

        self.fans = [Fan(i) for i in
                     range(self.sysconf['Fans']['count'])]

        self.linear_axis = [LinearActuator(i) for i in
                            range(self.sysconf['LinearActuators']['count'])]

        self.digital_inputs = [DigitalInput(i) for i in
                               range(self.sysconf['DigitalInputs']['count'])]

        self.liquid_sensors = [LiquidSensor(i) for i in
                               range(self.sysconf['LiquidSensors']['count'])]
        self.start_com_proc()
        
if __name__ == '__main__':
    s = SynthesizerHAL()
