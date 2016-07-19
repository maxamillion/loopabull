import fedmsg

class Fedmsg(Loopabull.looper):
        for name, endpoint, topic, msg in fedmsg.tail_messages():
            yield (topic, dict(msg))
