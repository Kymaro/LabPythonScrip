import pyvisa
import time
import csv
import matplotlib.pyplot as plt

# RIGOL DSG836A ID for opening ressources
# USB0::0x1AB1::0x099C::DSG8N213400002::INSTR (PALAISEAU)
# USB0::0x1AB1::0x099C::DSG8N213400006::INSTR (EVRY)

# SIGLENT SDM3045X multimeter
# USB0::0xF4EC::0xEE38::SDM34FBX5R1321::INSTR

"""             COMMANDES UTILES RIGOL
OUTPUT [ON/OFF] / [1/0] : Démarre ou stop la sortie RF

FREQ 2.45GHz : met la fréquence à 2.45GHz

LEVEL -10dBm : met la sortie à -10 dBm

             COMMANDES UTILES SIGLENT
MEAS:VOLT:DC?
open_resource(XXXXXX, write_termination='anti/n', query_delay=0.25)
"""
PALAISEAU = 1
POWER = -18
FREQ = 2300
voltageThreshold = 100 #mV
timeArray = []
voltageTimeArray = []

rm = pyvisa.ResourceManager()
rm.list_resources()

def annot_max(x, y, ax=None):
    xmax = x[y.index(max(y))]
    ymax = max(y)
    text = "x={}, y={}".format(xmax, ymax)
    if not ax:
        ax = plt.gca()
    bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
    arrowprops = dict(arrowstyle="->", connectionstyle="angle,angleA=0,angleB=60")
    kw = dict(xycoords='data', textcoords="axes fraction",
              arrowprops=arrowprops, bbox=bbox_props, ha="right", va="top")
    ax.annotate(text, xy=(xmax, ymax), xytext=(0.94, 0.96), **kw)

if PALAISEAU:
    gen = rm.open_resource('USB0::0x1AB1::0x099C::DSG8N213400002::INSTR')
else:
    gen = rm.open_resource('USB0::0x1AB1::0x099C::DSG8N213400006::INSTR')
mult = rm.open_resource('USB0::0xF4EC::0xEE38::SDM34FBX5R1321::INSTR', write_termination='\n', query_delay=0.25)

freqString = "FREQ %sMHz" % FREQ
gen.write(freqString)
powerString = "POWER %sdBm" % POWER
gen.write(powerString)
time.sleep(2)

voltage = round(float(mult.query('MEAS:VOLT:DC?')),5) * 1000
voltageTimeArray.append(voltage)
timeArray.append(0)
gen.write("OUTPUT ON")
start = time.time()
while voltage < voltageThreshold:
    #time.sleep(1)
    voltage = round(float(mult.query('MEAS:VOLT:DC?')),5) * 1000
    voltageTimeArray.append(voltage)
    timeArray.append(time.time() - start)
gen.write("OUTPUT OFF")

#timeArray = [i for i in range(len(voltageTimeArray))]
headerTimer = ['Time', 'Voltage']
voltageTimerData = [[timeArray[i], voltageTimeArray[i]] for i in range(len(voltageTimeArray))]
with open('timeCharging2.csv', 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(headerTimer)
    writer.writerows(voltageTimerData)
f.close()

"""                                     PLOTING DATA                                        """
plt.plot(timeArray, voltageTimeArray)
plt.title('Output Voltage (mV) depending time (s)\nwith an input power of {} dBm at {} MHz'.format(POWER, FREQ))
plt.grid()
plt.savefig('timeCharging2.svg')
plt.close()