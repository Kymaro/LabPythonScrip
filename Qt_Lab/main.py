# ------------------------------------------------------#
# ---------------------- main.py -----------------------#
# ------------------------------------------------------#
from PyQt5.QtCore import QObject, pyqtSignal, QThread
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi

from matplotlib.backends.backend_qt5agg import (NavigationToolbar2QT as NavigationToolbar)

import numpy as np
import time
import pyvisa
import random
import serial
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

POWER = 0  # dBm
FREQUENCY = 0  # MHz
VOLTAGE = 0  # mV
ENERGY = 0  # uJ
PALAISEAU = 1
CAPACITOR = 470000

START_FREQ = 10  # MHz
STEP_FREQ = 10  # MHz

START_POWER = -30  # dBm
STEP_POWER = 1  # dBm

freqArray = []
powerArray = []
voltageFreqArray = []
voltagePowerArray = []
timeArray = []
voltageTimeArray = []
headerTimer = ['Time', 'Voltage']
voltageTimerData = []

testX = [1, 2, 3, 4, 5]
testY = [1, 2, 3, 4, 5]

class QtLab(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        loadUi("LabMeasurement.ui", self)
        self.setWindowTitle("Lab measurement GUI")
        self.rectifierCharacterization.clicked.connect(self.rectifierCharacterizationF)
        self.saveFig.clicked.connect(self.saveFigF)
        self.timeCharging.clicked.connect(self.timeChargingF)
        self.inputVoltage.valueChanged.connect(self.inputVoltageF)
        self.inputPower.valueChanged.connect(self.inputPowerF)
        self.inputFrequency.valueChanged.connect(self.inputFrequencyF)
        self.palaiseau.stateChanged.connect(self.palaiseauF)
        self.inputVoltageLCD.returnPressed.connect(self.inputVoltageLCDF)
        self.inputPowerLCD.returnPressed.connect(self.inputPowerLCDF)
        self.inputFrequencyLCD.returnPressed.connect(self.inputFrequencyLCDF)

        global POWER
        global FREQUENCY
        global VOLTAGE
        POWER = self.inputPower.value()
        FREQUENCY = self.inputFrequency.value()
        VOLTAGE = self.inputVoltage.value()

        self.inputPowerLCD.setText(str(POWER))
        self.inputFrequencyLCD.setText(str(FREQUENCY))
        self.inputVoltageLCD.setText(str(VOLTAGE))

        self.addToolBar(NavigationToolbar(self.MplWidget.canvas, self))

    def inputVoltageLCDF(self):
        global VOLTAGE
        VOLTAGE = int(self.inputVoltageLCD.text())
        self.inputVoltage.setValue(VOLTAGE)

    def inputPowerLCDF(self):
        global POWER
        POWER = int(self.inputPowerLCD.text())
        self.inputPower.setValue(POWER)

    def inputFrequencyLCDF(self):
        global FREQUENCY
        FREQUENCY = int(self.inputFrequencyLCD.text())
        self.inputFrequency.setValue(FREQUENCY)

    def rectifierCharacterizationF(self):
        mult = rm.open_resource('USB0::0xF4EC::0xEE38::SDM34FBX5R1321::INSTR', write_termination='\n', query_delay=0.10)
        if PALAISEAU:
            gen = rm.open_resource('USB0::0x1AB1::0x099C::DSG8N213400002::INSTR')
        else:
            gen = rm.open_resource('USB0::0x1AB1::0x099C::DSG8N213400006::INSTR')
        gen.write("LEVEL {}dBm".format(POWER))
        gen.write("FREQ {}MHz".format(START_FREQ))
        gen.write("OUTPUT ON")

        for freq in range(START_FREQ, FREQUENCY + STEP_FREQ, STEP_FREQ):  # Frequency sweep at -20 dBm
            freqArray.append(freq)
            freqString = "FREQ %sMHz" % freq
            gen.write(freqString)
            time.sleep(0.5)
            voltage = mult.query('MEAS:VOLT:DC?')
            voltageFreqArray.append(round(float(voltage), 3))

        gen.write("OUTPUT OFF")
        self.MplWidget.canvas.axes.clear()
        self.MplWidget.canvas.axes.plot(freqArray, voltageFreqArray)
        self.MplWidget.canvas.axes.set_title('Output Voltage (mV) based on the Frequency (MHz) at Pin = -18 dBm')
        self.MplWidget.canvas.draw()

        gen.clear()
        gen.before_close()
        gen.close()
        mult.clear()
        mult.before_close()
        mult.close()

    def saveFigF(self):
        path = QFileDialog.getSaveFileName(self, 'Save File')[0]
        testXY = [[testX[i], testY[i]] for i in range(len(testX))]
        with open(path, 'w', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headerTimer)
            writer.writerows(voltageTimerData)
        f.close()

    def timeChargingF(self):
        #global VOLTAGE
        #global POWER
        #global FREQUENCY
        print(VOLTAGE)
        print(POWER)
        print(FREQUENCY)
        mult = rm.open_resource('USB0::0xF4EC::0xEE38::SDM34FBX5R1321::INSTR', write_termination='\n', query_delay=0.10)
        if PALAISEAU:
            gen = rm.open_resource('USB0::0x1AB1::0x099C::DSG8N213400002::INSTR')
        else:
            gen = rm.open_resource('USB0::0x1AB1::0x099C::DSG8N213400006::INSTR')

        gen.write("LEVEL {}dBm".format(POWER))
        gen.write("FREQ {}MHz".format(FREQUENCY))
        gen.write("OUTPUT ON")

        ard = serial.Serial('COM5', 9600)
        print("SERIAL OK")
        time.sleep(10)
        read_voltage = round(float(mult.query('MEAS:VOLT:DC?')), 3)
        ard.write(b'R')
        print("write done")
        start = time.time()
        while read_voltage * 1000 < VOLTAGE:
            read_voltage = round(float(mult.query('MEAS:VOLT:DC?')), 5)
            energy = int(read_voltage * read_voltage * CAPACITOR / 2)  # µJ
            self.energyNumber.display(energy)
            voltageTimeArray.append(round(read_voltage * 1000, 2))
            timeArray.append(round(time.time() - start, 3))
        ard.write(b'B')
        print("write B done")
        gen.write("OUTPUT OFF")
        global voltageTimerData
        voltageTimerData = [[timeArray[i], voltageTimeArray[i]] for i in range(len(voltageTimeArray))]

        self.MplWidget.canvas.axes.clear()
        self.MplWidget.canvas.axes.plot(timeArray, voltageTimeArray)
        self.MplWidget.canvas.axes.set_title('Output Voltage (mV) based on the Time (s) at Pin = -18 dBm')
        self.MplWidget.canvas.draw()

        gen.clear()
        gen.before_close()
        gen.close()
        mult.clear()
        mult.before_close()
        mult.close()

    def inputVoltageF(self):
        global VOLTAGE
        VOLTAGE = self.inputVoltage.value()
        self.inputVoltageLCD.setText(str(VOLTAGE))

    def inputPowerF(self):
        global POWER
        POWER = self.inputPower.value()
        self.inputPowerLCD.setText(str(POWER))

    def inputFrequencyF(self):
        global FREQUENCY
        FREQUENCY = self.inputFrequency.value()
        self.inputFrequencyLCD.setText(str(FREQUENCY))

    def palaiseauF(self):
        global PALAISEAU
        if self.palaiseau.checkState():
            PALAISEAU = 1
        else:
            PALAISEAU = 0


if __name__ == "__main__":
    rm = pyvisa.ResourceManager()

    app = QApplication([])
    windows = QtLab()
    windows.show()
    app.exec_()
