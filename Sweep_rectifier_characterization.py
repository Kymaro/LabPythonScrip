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
START_FREQ = 1000   # MHz
STOP_FREQ = 3000    # MHz
STEP_FREQ = 50      # MHz

START_POWER = -30   # dBm
STOP_POWER = 10     # dBm
STEP_POWER = 1      # dBm

freqArray = []
powerArray = []
voltageFreqArray = []
voltagePowerArray = []

rm = pyvisa.ResourceManager()
rm.list_resources()

if PALAISEAU:
    gen = rm.open_resource('USB0::0x1AB1::0x099C::DSG8N213400002::INSTR')
else:
    gen = rm.open_resource('USB0::0x1AB1::0x099C::DSG8N213400006::INSTR')
mult = rm.open_resource('USB0::0xF4EC::0xEE38::SDM34FBX5R1321::INSTR', write_termination='\n', query_delay=0.25)

gen.write("LEVEL -18dBm")  # 2 dB of loss with cable so this is -20 dBm. -20 is our key value for power
gen.write("FREQ 1000MHz")
time.sleep(1)
gen.write("OUTPUT ON")

for freq in range(START_FREQ, STOP_FREQ + STEP_FREQ, STEP_FREQ):    # Frequency sweep at -20 dBm
    freqArray.append(freq)
    freqString = "FREQ %sMHz" % freq
    gen.write(freqString)
    time.sleep(0.5)
    voltage = mult.query('MEAS:VOLT:DC?')
    voltageFreqArray.append(round(float(voltage), 3))

gen.write("OUTPUT OFF")
headerFreq = ['Freq', 'Voltage']
voltageFreqData = [[freqArray[i], voltageFreqArray[i]] for i in range(len(freqArray))]
with open('voltageFreq.csv', 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(headerFreq)
    writer.writerows(voltageFreqData)
f.close()

maxVoltageIndex = voltageFreqArray.index(max(voltageFreqArray))
freqMaxVoltage = freqArray[maxVoltageIndex]
print("Frequency with the maximum output voltage: %s MHz", freqMaxVoltage)

freqMaxVoltageString = "FREQ %sMHz" % freqMaxVoltage
gen.write(freqMaxVoltageString)
gen.write("LEVEL -30dBm")
gen.write("OUTPUT ON")

for power in range(START_POWER, STOP_POWER + STEP_POWER, STEP_POWER):
    powerArray.append(power)
    powerString = "LEVEL %sdBm" % power
    gen.write(powerString)
    time.sleep(0.5)
    voltage = mult.query('MEAS:VOLT:DC?')
    voltagePowerArray.append(round(float(voltage), 3))

gen.write("OUTPUT OFF")
headerFreq = ['Power', 'Voltage']
voltageFreqData = [[powerArray[i], voltagePowerArray[i]] for i in range(len(powerArray))]
with open('voltagePower.csv', 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(headerFreq)
    writer.writerows(voltageFreqData)
f.close()

"""                                     PLOTING DATA                                        """
xF, xP, yF, yP = [], [], [], []
xFmax = 0

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


with open('voltageFreq.csv', 'r') as csvFile:
    plots = csv.reader(csvFile, delimiter=',')
    for row in plots:
        if row[0] == 'Freq':
            plt.xlabel(row[0] + ' in MHz')
            plt.ylabel(row[1] + ' in mV')
        else:
            xF.append(int(row[0]))
            yF.append(int(float(row[1]) * 1000))
plt.plot(xF, yF)
plt.title('Output Voltage (mV) depending on the input Frequency (MHz)\nwith Pin of -18 dBm')
plt.legend()
annot_max(xF, yF)
plt.grid()
plt.savefig('voltageFreq.svg')
plt.close()

xFmax = xF[yF.index(max(yF))]

with open('voltagePower.csv', 'r') as csvFile:
    plots = csv.reader(csvFile, delimiter=',')
    for row in plots:
        if row[0] == 'Power':
            plt.xlabel(row[0] + ' in dBm')
            plt.ylabel(row[1] + ' in mV')
        else:
            xP.append(int(row[0]))
            yP.append(int(float(row[1]) * 1000))
plt.plot(xP, yP)
plt.title('Output Voltage (mV) depending on the input Power (dBm)\nat a Frequency of {} MHz'.format(xFmax))
plt.legend()
#annot_max(xP, yP)
plt.grid()
plt.savefig('voltagePower.svg')
plt.close()
