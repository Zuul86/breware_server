import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket

import sys
import RPi.GPIO as GPIO
import os
import glob
from RepeatEvery import RepeatEvery

from tornado.options import define, options
import threading

define("port", default=8888, help="run on the given port", type=int)

base_dir = '/sys/bus/w1/devices/'

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.OUT)

device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/on", OnHandler),
            (r"/off", OffHandler),
            (r"/temperaturesocket", TemperatureSocketHandler)
        ]
        settings = dict(
                template_path = os.path.join(os.path.dirname(__file__), "templates"),
                static_path = os.path.join(os.path.dirname(__file__), "static"),
                xsrf_cookies=True,
                cookie_secret="3wRI6Q7Nm50z",
        )
        tornado.web.Application.__init__(self, handlers, **settings)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("temperature_demo.html")
     
class OnHandler(tornado.web.RequestHandler):
    def get(self):
        GPIO.output(23, True)
        self.write("On")

class OffHandler(tornado.web.RequestHandler):
    def get(self):
        GPIO.output(23, False)
        self.write("Off")

class TemperatureSocketHandler(tornado.websocket.WebSocketHandler):
    waiters = set()
    thread = set()
    
    def __init__(self, application, request, **kwargs):        
        self.thread = RepeatEvery(1, self.send_temperatures)
        tornado.websocket.WebSocketHandler.__init__(self, application, request, **kwargs)
        
    def on_message(self, message):
        if message == 'GetTemps':
            self.thread.start()
        
    def open(self):
        TemperatureSocketHandler.waiters.add(self)

    def on_close(self):
        TemperatureSocketHandler.waiters.remove(self)  
        print('Connection Closed')
        if len(TemperatureSocketHandler.waiters) == 0:
            print('No more clients. Stop Thread.')
            self.thread.stop()
        
    @classmethod
    def send_temperatures(cls):
        for waiter in cls.waiters:
            try:
                temp = TemperatureReader().read_temp()
                if temp >= 80:
                    GPIO.output(23, True)
                if temp < 80:
                    GPIO.output(23, False)
                if len(cls.waiters) == 0:
                    break
                waiter.write_message(str(temp))
            except AttributeError, e:
                print("Error sending temp", e)
                break


        
def main():
    tornado.options.parse_command_line()
    
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

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

if __name__ == "__main__":
    main()
