import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QPixmap
import time

from PyQt5.QtWidgets import QFileDialog

qtCreatorFile = "GUI.ui" # Enter file here.
 
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

from dg800 import DG800
 
class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):
    
        
    def liveUpdate(self):
        if(self.checkLive.isChecked()):
            self.getLiveview()
            self.statusBar().showMessage('Wait 3 seconds for refresh.')
            time.sleep(1)
            self.statusBar().showMessage('Wait 2 seconds for refresh.')
            time.sleep(1)
            self.statusBar().showMessage('Wait 1 seconds for refresh.')
            time.sleep(1)
            self.getLiveview()
            self.statusBar().showMessage('Liveview updated.')
    
    def toggle_output_channel_1(self):
        if (self.inst.readOutputState("1") == "ON"):
            self.inst.writing(':OUTP1 OFF')
        else:
            self.inst.writing(':OUTP1 ON')
        
    def toggle_output_channel_2(self):
        if (self.inst.readOutputState("2") == "ON"):
            self.inst.writing(':OUTP2 OFF')
        else:
            self.inst.writing(':OUTP2 ON')
    
    def tryConnect(self):
        myDevice = self.boxDevices.currentText()
        if ("USB" in myDevice):
            self.inst.conn(myDevice)
            self.liveUpdate()
            self.statusBar().showMessage('Connected to: '+myDevice)
            self.getLiveview()
    
    def setWaveform(self):
        self.inst.writing(':SOUR1:FUNC '+self.boxWaveform.currentText())
        self.liveUpdate()
    
    def setWaveform2(self):
        self.inst.writing(':SOUR2:FUNC '+self.boxWaveform2.currentText())
        self.liveUpdate()
        
    def setFreqChan1(self):
        freq = int(self.textFrequencyChannel1.text())*1000**self.boxFreqMultiplicator.currentIndex()
        if(freq<=100000000):
            self.inst.writing(':SOUR1:FREQ '+str(freq))
            self.liveUpdate()
    
    def setFreqChan2(self):
        freq = int(self.textFrequencyChannel2.text())*1000**self.boxFreqMultiplicator2.currentIndex()
        if(freq<=100000000):
            self.inst.writing(':SOUR2:FREQ '+str(freq))
            self.liveUpdate()
    
    def setAmpChannel1(self):
        Amp = self.textAmplitudeChannel1.text()
        self.inst.writing(':SOUR1:VOLT:UNIT '+self.boxUnitChannel1.currentText())
        self.inst.writing(':SOUR1:VOLT '+str(Amp))
        self.liveUpdate()
    
    def setAmpChannel2(self):
        Amp = self.textAmplitudeChannel2.text()
        self.inst.writing(':SOUR2:VOLT:UNIT '+self.boxUnitChannel2.currentText())
        self.inst.writing(':SOUR2:VOLT '+str(Amp))
        self.liveUpdate()
        
    def getLiveview(self):
        png = self.inst.getPNG()
        with open('tmp.png',"wb") as f:
            f.write(png)
        mypix = QPixmap('tmp.png')
        self.labelView.setPixmap(mypix)
        
    def toggleHighZChan1(self):
        Status = self.inst.querying(":OUTP1:IMP?")
        if (Status=="5.000000E+01"):
            self.inst.writing(":OUTP1:IMP INF")
        else:
            self.inst.writing(":OUTP1:LOAD 50")
        self.liveUpdate()
    
    def toggleHighZChan2(self):
        Status = self.inst.querying(":OUTP2:IMP?")
        if (Status=="5.000000E+01"):
            self.inst.writing(":OUTP2:IMP INF")
        else:
            self.inst.writing(":OUTP2:LOAD 50")
        self.liveUpdate()
    
    def takeScreenshot(self):
        fname = QFileDialog.getSaveFileName()#(self, 'Open file', '/home')
        png = self.inst.getPNG()
        with open(fname[0],"wb") as f:
            f.write(png)
    
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.inst = DG800()
        self.buttonOutput1.clicked.connect(self.toggle_output_channel_1)
        self.buttonOutput2.clicked.connect(self.toggle_output_channel_2)
        self.buttonConnect.clicked.connect(self.tryConnect)
        self.buttonLive.clicked.connect(self.getLiveview)
        self.buttonToggleHighZ_Ch1.clicked.connect(self.toggleHighZChan1)
        self.buttonToggleHighZ_Ch2.clicked.connect(self.toggleHighZChan2)
        self.textFrequencyChannel1.returnPressed.connect(self.setFreqChan1)
        self.textFrequencyChannel2.returnPressed.connect(self.setFreqChan2)
        self.textAmplitudeChannel1.returnPressed.connect(self.setAmpChannel1)
        self.textAmplitudeChannel2.returnPressed.connect(self.setAmpChannel2)
        self.boxWaveform.currentIndexChanged.connect(self.setWaveform)
        self.boxWaveform2.currentIndexChanged.connect(self.setWaveform2)
        self.statusBar().showMessage('Not connected.')
        self.boxDevices.addItem(self.inst.findDevs())
        self.buttonScreenshot.clicked.connect(self.takeScreenshot)
        self.tryConnect()
        self.textFrequencyChannel1.setText(str(2450)
 
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())