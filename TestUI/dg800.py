#Install pyvisa, use pip for example:
#pip3 install pyvisa
import pyvisa as visa

class DG800(object):
    def __init__(self):
        pass

    def findDevs(self):
        rm = visa.ResourceManager()
        res = rm.list_resources()
        return res[0]
    
    #Place your Serial number here
    def conn(self, constr="USB0::0x1AB1::0x0643::DG8XXXXXXXXXX::INSTR"):
        """Attempt to connect to instrument"""
        rm = visa.ResourceManager()
        self.inst = rm.open_resource(constr)

    def identify(self):
        """Return identify string which has serial number"""
        return self.inst.query("*IDN?")

    def readOutputState(self, channel="1"):
        resp = self.inst.query(":OUTP"+channel+"?")
        return resp.rstrip()

    def getPNG(self):
        self.inst.write(':HCOP:SDUM:DATA:FORM PNG')
        self.inst.write(':HCOPy:SDUMp:DATA?')
        bmpdata = self.inst.read_raw(391734+11)
        bmpdata = bmpdata[11:]
        return bmpdata
    
    def querying(self, command="*IDN?"):
        resp = self.inst.query(command)
        return resp.rstrip()
    
    def dis(self):
        del self.inst

    def writing(self, command=""):
        self.inst.write(command)
        
if __name__ == '__main__':
    test = DG800()
    
    devs = test.findDevs()
    print(devs)
    
    #test.conn()
    #print (test.identify())
    #print ("Output Channel 1 is "+test.readOutputState("1"))
    #print ("Output Channel 2 is "+test.readOutputState("2"))
