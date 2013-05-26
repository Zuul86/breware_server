import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket

import sys
import RPi.GPIO as GPIO
import os
import glob
import time

from tornado.options import define, options
import threading

define("port", default=8888, help="run on the given port", type=int)

base_dir = '/sys/bus/w1/devices/'

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)

device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/on", OnHandler),
            (r"/off", OffHandler),
            (r"/demoflot", DemoFlotHandler),
            (r"/temperaturesocket", TemperatureSocketHandler)
        ]
        settings = dict(
                template_path = os.path.join(os.path.dirname(__file__), "templates"),
                static_path = os.path.join(os.path.dirname(__file__), "static"),
                #xsrf_cookies=True,
                #cookie_secret="3wRI6Q7Nm50z",
        )
        tornado.web.Application.__init__(self, handlers, **settings)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("temperature_demo.html")
     
class OnHandler(tornado.web.RequestHandler):
    def get(self):
        GPIO.output(18, True)
        temp = read_temp()
        self.write(str(temp))

class OffHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Off")
        GPIO.output(18, False)

class TemperatureSocketHandler(tornado.websocket.WebSocketHandler):
    waiters = set()
    thread = set()
    lock = threading.Lock()
    
    def __init__(self, application, request, **kwargs):        
        self.thread = RepeatEvery(1, self.send_temperatures)
        tornado.websocket.WebSocketHandler.__init__(self, application, request, **kwargs)
        
    def on_message(self, message):
        if message == 'GetTemps':
            self.thread.start()
        
    def open(self):
        with self.lock:
            TemperatureSocketHandler.waiters.add(self)

    def on_close(self):
        print('Closing Socket')
        with self.lock:
            print('Lock')
            TemperatureSocketHandler.waiters.remove(self)
        print('Unlock')    

        if len(TemperatureSocketHandler.waiters) == 0:
            print('No more clients. Stop Thread.')
            self.thread.stop()
            self.thread.join(5)
        
    @classmethod
    def send_temperatures(cls):
        for waiter in cls.waiters:
            try:
                temp = read_temp()
                if temp >= 80:
                    GPIO.output(18, True)
                if len(cls.waiters) == 0:
                    break
                waiter.write_message(str(temp))
            except AttributeError, e:
                print("Error sending temp", e)
                break

class RepeatEvery(threading.Thread):
    def __init__(self, interval, func, *args, **kwargs):
        threading.Thread.__init__(self)
        self.interval = interval  # seconds between calls
        self.func = func          # function to call
        self.args = args          # optional positional argument(s) for call
        self.kwargs = kwargs      # optional keyword argument(s) for call
        self.runable = True
    def run(self):
        while self.runable:
            self.func(*self.args, **self.kwargs)
            time.sleep(self.interval)
    def stop(self):
        self.runable = False
        
def main():
    tornado.options.parse_command_line()
    
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 +32.0
    return temp_f

if __name__ == "__main__":
    main()
