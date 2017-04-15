# -*- coding: utf-8 -*-

import threading

from hypchat import HypChat

from tornado.options import options


class HipClient(object):

    def __init__(self, token, room_id):
        chat = HypChat(token)
        self._room = chat.get_room(room_id)
        self._latest_date = None


    def to_dict(cls,m):

        #print(m)

        d = {'text': m['message']}
        d['from'] = m['from'] if isinstance(m['from'], str) else m['from']['name']
        d['color'] = m['color'] if 'color' in m else 'black'
        return d

    def messages(cls,limit=100):
        ms = []
        latest = cls._latest_date

        for m in cls._room.history(maxResults=limit)['items']:
            message_date = m['date']
            d = cls.to_dict(m)

            if latest is None:
                ms.append(d)
                cls._latest_date = message_date
                latest = message_date
            elif latest < message_date:
                #print("ADD::" + str(d))
                ms.append(d)

        cls._latest_date = message_date if cls._latest_date < message_date else cls._latest_date

        return ms

    def send(cls,comment):
        #cls._room.notification(message=comment['text'], color=comment['color'])
        data = {'message': comment['text'], 'notify': False, 'message_format': 'text', 'from': comment['from'], 'color': comment['color']}
        cls._room._requests.post(cls._room.url + '/notification', data=data)

        #cls.root.message(comment)

