import sys
sys.path.append("../")
from statusfmt import config

test_packet = ('?\x00\x00\x00\x10\x02\x00\x00\x00\x00\x00'
               '\x00A\x00\x00\x00d\x00\x00\x00\x00\x00\x00'
               '?d\x00\x00\x00\x00\x00\x00?d\x00\x00\x00'
               '\x00\x00\x00?d\x00\x00\x00\x00\x00\x00?'
               '\x00\x00\xaa\x00\xaa\x00\xaa\x00\x00\x00'
               '\x00\x00\x00\x00\xc8A\x00\x00\x00\x00\x00'
               '\x00\xc8A\x00\x00\x00\x00\x00\x00\xc8A\x00'
               '\x00\x00\x00\x00\x00\xc8A\x00\x00\x00\x00'
               '\x00\x00\xc8A\x00\x00\x00\x00\x00\x00\xc8A'
               '\x00\x00\x00\x00\x00\x00\xc8A\x00\x00\x00'
               '\x00\x00\x00\xc8A\x00\x00\x00\x00\x00\x00'
               '\xc8A\x00\x00\x00\x00\x00\x00\xc8A\x00\x00'
               '\x00\x00\x00\x00\xc8A\x00\x00\x00\x00\x00'
               '\x00\xc8A\xf0\x00\x00\x00\x00\x00\xc8A\x00'
               '\x00\x00\x00\x00\x00\xc8A\x00\x00\x00\x00'
               '\x00\x00\xc8A\x00\x00\x00\x00\x00\x00 A'
               '\x00\x00\xa0@\x00\x00 A\x00\x00\xa0@\xa0'
               '\x00\x00\x00\xe8\x03\x00\x00\xd0\x07\x00'
               '\x00\x00\x00\x00\x00\xe8\x03\x00\x00\xd0'
               '\x07\x00\x00\x00\x00\x00\x00\xe8\x03\x00'
               '\x00\xd0\x07\x00\x00\x00\x00\x00\x00\xe8'
               '\x03\x00\x00\xd0\x07\x00\x00\x00\x00\x00'
               '\x00\xe8\x03\x00\x00\xd0\x07\x00\x00\x00'
               '\x00\x00\x00\x00\x00\xaa\xaa\x00\x00\x00'
               '\x00\x00\x00\xc0?\x00\x00\xc0?\x00\x00'
               '\xc0?\x00\x00\xc0?\x00\x00\xc0?\x00\x00'
               '\xc0?\x00\x00\xc0?\x00\x00\xc0?')


test_data = []

#--------#
# Header #
#--------#
# Packet type '?' means full status
test_data.append(ord('?'))
# Packet id, client should auto-increment
test_data.append(528)
# Zero means no error, not necessary error, could be just info!
# error_code < 0 means hw exception!
test_data.append(0)

#--------#
# Mixers #
#--------#
# Mixer error code
test_data.append('A')
# Mixer Period and duty cycle
for i in range(config["Mixers"]["count"]):
    test_data.append(100)
    test_data.append(0.5)

#--------#
# Valves #
#--------#
# Valves error code
test_data.append('\x00')
# Valves state
test_data.append(0xAA)
test_data.append(0xAA)
test_data.append(0xAA)

#---------------#
# Thermocouples #
#---------------#
for i in range(config['Thermocouples']['count']):
    # Thermocouple error code
    test_data.append('\x00')
    # Thermocouple temperature
    test_data.append(25.0)

#-------------------#
# Aux Thermocouples #
#-------------------#
for i in range(config['AuxThermocouples']['count']):
    # Thermocouple error code
    test_data.append('\x00')
    # Thermocouple temperature
    test_data.append(25.0)
#--------#
# Heater #
#--------#
# Heater state
test_data.append(0b11110000)

#-------------------------#
# Temperature Controllers #
#-------------------------#
for i in range(config['TemperatureControllers']['count']):
    # Temperature Controller Error Code
    test_data.append('\x00')
    # Temperature Controller setpoint
    test_data.append(25.0)

#----------------#
# SMC Interfaces #
#----------------#
# SMC Interface error code
test_data.append('\x00')
for i in range(config['SMCInterfaces']['count']):
    # SMC Interface analog out voltage
    test_data.append(10.0)
    # SMC Interface analog in voltage
    test_data.append(5.0)

#------#
# Fans #
#------#
# Fan state
test_data.append(chr(0b10100000))

#-------------#
# Linear Axis #
#-------------#
for i in range(config['LinearActuators']['count']):
    # Linear Axis position
    test_data.append(1000)
    # Linear Axis requested position
    test_data.append(2000)
    # Linear Axis error code
    test_data.append(0)

#----------------#
# Digital Inputs #
#----------------#
# Digital Inputs Error Code
test_data.append('\x00')
# Digital Input state
test_data.append(0xAAAA)

#----------------#
# Liquid Sensors #
#----------------#
# Liquid Sensors Error Code
test_data.append('\x00')

# Liquid Sensors Analog In
for i in range(config['LiquidSensors']['count']):
    test_data.append(1.5)
