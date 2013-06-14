import tornado.web
import tornado.websocket

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.OUT)

from RepeatEvery import RepeatEvery
from TemperatureReader import TemperatureReader

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
        self.thread = RepeatEvery(1, self.__send_temperatures)
        tornado.websocket.WebSocketHandler.__init__(self, application, request, **kwargs)
        
    def on_message(self, message):
        #TODO: Take JSON objects as messages.
        #      Use a message factory to process different types of messages.
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
        
    def __send_temperatures(self):
        for waiter in self.waiters:
            try:
                temp = TemperatureReader().read_temp()
                if temp >= 80:
                    GPIO.output(23, True)
                if temp < 80:
                    GPIO.output(23, False)
                if len(self.waiters) == 0:
                    break
                waiter.write_message(str(temp))
            except AttributeError, e:
                print("Error sending temp", e)
                break
