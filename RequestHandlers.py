import tornado.web
import tornado.websocket

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.OUT)

from RepeatEvery import RepeatEvery
from TemperatureReader import TemperatureReader
from MessageFactory import MessageFactory
from MessageProducer import MessageProducerFactory

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
    __waiters = set()
    thread = set()
    stepTemperature = 0
    stepDuration = 0
    temperatureControlOverriden = False
    action = set()
    state = False
    lastState = False
    currentTemperature = 0

    def __init__(self, application, request, **kwargs):
        self.thread = RepeatEvery(1, self.__send_temperatures)
        tornado.websocket.WebSocketHandler.__init__(self, application, request, **kwargs)
        
    def on_message(self, message):
        messageObject = MessageFactory.get_message(message)
        messageObject.processMessage(self)
        
        messageProducerObject = MessageProducerFactory.get_message(self.action)
        messageProducerObject.produceMessage(self)
        
    def open(self):
        TemperatureSocketHandler.__waiters.add(self)

    def on_close(self):
        TemperatureSocketHandler.__waiters.remove(self)  
        print('Connection Closed')
        if len(TemperatureSocketHandler.__waiters) == 0:
            print('No more clients. Stop Thread.')
            self.thread.stop()
        
    def __send_temperatures(self):
        for waiter in self.__waiters:
            try:
                self.currentTemperature = TemperatureReader().read_temp()
                
                if self.currentTemperature >= self.stepTemperature:
                    self.state = False
                if self.currentTemperature < self.stepTemperature:
                    self.state = True
                if len(self.__waiters) == 0:
                    break
                if not self.temperatureControlOverriden:
                    self.toggleGPIO()
                    
                messageProducerObject = MessageProducerFactory.get_message('state_change')
                if (self.lastState != self.state):
                    messageProducerObject.produceMessage(self)
                self.lastState = self.state
                
                messageProducerObject = MessageProducerFactory.get_message('send_temperature')
                messageProducerObject.produceMessage(self)
            except AttributeError as e:
                print("Error sending temp", e)
                break
        
    def toggleGPIO(self):
        GPIO.output(23, self.state)