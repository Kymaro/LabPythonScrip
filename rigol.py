import pyvisa
import time

#RIGOL DSG836A ID for opening ressources
#USB0::0x1AB1::0x099C::DSG8N213400002::INSTR

"""             COMMANDES UTILES 
OUTPUT [ON/OFF] / [1/0] : Démarre ou stop la sortie RF

FREQ 2.45GHz : met la fréquence à 2.45GHz

LEVEL -10dBm : met la sortie à -10 dBm
"""

rm = pyvisa.ResourceManager()
rm.list_resources()
"""
psu = rm.open_resource('USB0::0x1AB1::0x099C::DSG8N213400002::INSTR')
for i in range(0,10):
    print(psu.write("OUTPUT OFF"))
    print(psu.write("FREQ 2.45GHz"))
    print(psu.write("LEVEL -20dBm"))
    print(psu.write("OUTPUT ON"))
    time.sleep(1)
    print(psu.write("LEVEL -10dBm"))
    print(psu.write("FREQ 1GHz"))
    time.sleep(0.1)
"""

