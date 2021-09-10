import pyvisa
import time

import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
from datetime import datetime

#RIGOL DSG836A ID for opening ressources
#USB0::0x1AB1::0x099C::DSG8N213400002::INSTR (PALAISEAU)
#USB0::0x1AB1::0x099C::DSG8N213400006::INSTR (EVRY)

#SIGLENT SDM3045X multimeter
#USB0::0xF4EC::0xEE38::SDM34FBX5R1321::INSTR

"""             COMMANDES UTILES RIGOL
OUTPUT [ON/OFF] / [1/0] : Démarre ou stop la sortie RF

FREQ 2.45GHz : met la fréquence à 2.45GHz

LEVEL -10dBm : met la sortie à -10 dBm
"""
"""             COMMANDES UTILES SIGLENT
MEAS:VOLT:DC?
open_resource(XXXXXX, write_termination='anti/n', query_delay=0.25)
"""

rm = pyvisa.ResourceManager()
rm.list_resources()

gen = rm.open_resource('USB0::0x1AB1::0x099C::DSG8N213400006::INSTR')
#mult = rm.open_resource('USB0::0xF4EC::0xEE38::SDM34FBX5R1321::INSTR')

gen.write("OUTPUT OFF")
gen.write("FREQ 2.45GHz")

i = 0
mytree = ET.parse('Situation_52b.xml')
myroot = mytree.getroot()

max_power = []
duration = []
NRJ = []
totalNRJ = [0]
transmit = []
gen.write("OUTPUT ON")
for x in myroot.findall('Sweep'):
    stringArray = x.find('Values').text
    array = stringArray.split(';')
    array.pop()
    array = [float(i) for i in array]
    m = int(max(array))
    print(m)
    rigol = "LEVEL %sdBm" %m
    gen.write(rigol)
    time.sleep(0.5)
    print(rigol)
gen.write("OUTPUT OFF")