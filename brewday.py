import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket

import sys
import os

import RequestHandlers

from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", RequestHandlers.MainHandler),
            (r"/on", RequestHandlers.OnHandler),
            (r"/off", RequestHandlers.OffHandler),
            (r"/temperaturesocket", RequestHandlers.TemperatureSocketHandler)
        ]
        settings = dict(
                template_path = os.path.join(os.path.dirname(__file__), "templates"),
                static_path = os.path.join(os.path.dirname(__file__), "static"),
                xsrf_cookies=True,
                cookie_secret="3wRI6Q7Nm50z",
        )
        tornado.web.Application.__init__(self, handlers, **settings)
        
def main():
    tornado.options.parse_command_line()
    
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
