# -*- coding: utf-8 -*-

import os
import time
import signal
import logging

import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.websocket

from tornado.options import define, options, parse_command_line

define("port", default=8888, help="run on the given port", type=int)
define("debug", default=True, help="run in debug mode")
define("autoreload", fault=True, help="run in autoreload mode")

MAX_WAIT_SECONDS_BEFORE_SHUTDOWN = 3

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html", messages=[{'id':'test', 'text':'ttt'}])


class Broadcaster(Object):
    channel = set()
    cache = []
    limit = 100

    @classmethod
    def update_cahe(cls, comment):
        cls.cache.append(comment)
        if len(cls.cache) > limit:
            cls.cache = cls.cache[-cls.limit:]

    @classmethod
    def send(cls, comment):
        for ch in cls.channel:
            try:
                ch.write_message(comment)
            except:
                cls.channel.remove(ch)


class ChatSocketHandler(tornado.websocket.WebSocketHandler):

    def open(self):
        Broadcaster.channel.add(self)

    def on_close(self):
        Broadcaster.channel.remove(self)


def shutdown():
    server.stop()

    io_loop = tornado.ioloop.IOLoop.instance()
    deadline = time.time() + MAX_WAIT_SECONDS_BEFORE_SHUTDOWN

    def stop_loop():
        now = time.time()
        if now < deadline and (io_loop._callbacks or io_loop._timeouts):
            io_loop.add_timeout(now + 1, stop_loop)
        else:
            io_loop.stop()
    stop_loop()


def sig_handler(sig, frame):
    tornado.ioloop.IOLoop.instance().add_callback(shutdown)


def main():
    parse_command_line()
    app = tornado.web.Application(
        [
            (r"/", MainHandler),
        ],
        cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "statics"),
        xsrf_cookies=True,
        debug=options.debug,
        )

    global server
    server = tornado.httpserver.HTTPServer(app)
    server.listen(options.port)

    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)

    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
