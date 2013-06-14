import os
import glob

class TemperatureReader():
    base_dir = '/sys/bus/w1/devices/'

    os.system('modprobe w1-gpio')
    os.system('modprobe w1-therm')

    device_folder = glob.glob(base_dir + '28*')[0]
    device_file = device_folder + '/w1_slave'

    def read_temp_raw(self):
        f = open(self.device_file, 'r')
        lines = f.readlines()
        f.close()
        return lines

    def read_temp(self):
        lines = self.read_temp_raw()
        while self.tempDataContainsYes(lines):
            time.sleep(0.2)
            lines = self.read_temp_raw()
        temp_string = self.getTemperatureData(lines)
        if temp_string != '':
            temp_c = self.calculateCelcius(temp_string)
            temp_f = self.calculateFareheit(temp_c)
        return temp_f

    def getTemperatureData(self, tempDataString):
        equals_pos = tempDataString[1].find('t=')
        temp_string = '';
        if equals_pos != -1:
            temp_string = tempDataString[1][equals_pos+2:]
        return temp_string
    
    def tempDataContainsYes(self, tempDataString):
        return tempDataString[0].strip()[-3:] != 'YES'
    
    def calculateCelcius(self, tempString):
        return float(tempString) / 1000.0

    def calculateFareheit(self, tempCelcius):
        return tempCelcius * 9.0 / 5.0 +32.0
