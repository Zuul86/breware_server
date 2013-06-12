import os
import glob

class TemperatureReader:
    def read_temp_raw(self):
        f = open(device_file, 'r')
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
