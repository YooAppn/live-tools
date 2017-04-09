# -*- coding: utf-8 -*-

import threading

from hypchat import HypChat


_chat = HypChat()
_roomid = 
_latest_date = None



def to_dict(m):
    d = {'text': m['message'], 'date': m['date']}
    d['from'] = m['from'] if isinstance(m['from'], str) else m['from']['name']
    d['color'] = m['color'] if 'color' in m else 'black'
    return d


def messages(limit=100):
    room = _chat.get_room(_roomid)
    ms = []

    global _latest_date

    latest = _latest_date

    for m in room.history(maxResults=limit)['items']:
        d = to_dict(m)
        message_date = d['date']
        if latest is None :
            ms.append(d)
            _latest_date = message_date
            latest = message_date
        elif latest < message_date:
            ms.append(d)

        _latest_date = message_date if _latest_date < message_date else _latest_date


    return ms

