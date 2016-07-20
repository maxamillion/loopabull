#
# Loopabull fedmsg plugin
#

import fedmsg

from loopabull.plugin import Plugin


class Fedmsg(Plugin):
    """
    Loopabull plugin to implement looper for fedmsg event loop
    """
    def __init__(self):
        """
        stub init
        """
        super(Fedmsg, self).__init__(self)
        print __name__

    def looper(self):
        """
        Implementation of the generator to feed the event loop
        """
        for name, endpoint, topic, msg in fedmsg.tail_messages():
            yield (topic, dict(msg))
