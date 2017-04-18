# -*- coding: utf-8 -*-

import os
import time
import signal
import json
import logging
import threading

import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado.options import define, options, parse_command_line

from livetools.hipchat import HipClient

define("port", default=8888, help="run on the given port", type=int)
define("debug", default=True, help="run in debug mode")
#define("autoreload", fault=True, help="run in autoreload mode")

define("api_token", default="no token", help="hipcaht api token")
define("room_id", default=0, help="hipchat room id")
define("hls_url", default='http://127.0.0.1:3000/hls/live/test.m3u8', help='hls url')

MAX_WAIT_SECONDS_BEFORE_SHUTDOWN = 3

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html", hls_url=options.hls_url)

class ChatroomHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("chatroom.html")


class Broadcaster(object):
    channel = set()
    cache = []
    limit = 100
    client = None

    @classmethod
    def update_cache(cls, comment):
        if isinstance(comment, list):
            cls.cache.extend(comment)
        else:
            cls.cache.append(comment)

        if len(cls.cache) > cls.limit:
            cls.cache = cls.cache[-cls.limit:]

    @classmethod
    def send(cls, comment):
        for ch in cls.channel:
            try:
                ch.write_message(comment)
            except:
                logging.error("Error sending message", exc_info=True)
                ch.close()

    @classmethod
    def reload_and_notify(cls):
        #print('....... reload ......')
        msgs = cls.client.messages()
        if len(msgs) > 0:
            cls.update_cache(msgs)
            cls.send({'comments':msgs, 'active': len(cls.channel)})

    @classmethod
    def interval_reload(cls):
        if cls._timer is not None:
            cls.reload_and_notify()
            t = threading.Timer(5,cls.interval_reload)
            t.start()

    @classmethod
    def watch(cls):
        cls._timer = threading.Thread(target=cls.interval_reload)
        cls._timer.start()

    @classmethod
    def watch_done(cls):
        if cls._timer is not None:
            cls._timer = None


class ChatSocketHandler(tornado.websocket.WebSocketHandler):

    def check_origin(self, origin):
        return True

    def open(self):
        Broadcaster.channel.add(self)
        Broadcaster.send({'comments':Broadcaster.cache, 'active': len(Broadcaster.channel)})

    def on_close(self):
        Broadcaster.channel.remove(self)

    def on_message(self, message):
        comment = json.loads(message)
        if isinstance(comment['text'], unicode):
            comment['text'] = comment['text'].encode('utf-8')
            comment['from'] = comment['from'].encode('utf-8')
            comment['color'] = comment['color'].encode('utf-8')

        Broadcaster.client.send(comment)

        Broadcaster.reload_and_notify()

def shutdown():
    Broadcaster.watch_done()
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

    # hipchat
    client = HipClient(options.api_token, options.room_id)
    Broadcaster.client = client
    Broadcaster.update_cache(client.messages())
    Broadcaster.watch()

    # http server
    app = tornado.web.Application(
        [
            (r"/live", MainHandler),
            (r"/room", ChatroomHandler),
            (r"/chat", ChatSocketHandler),
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
