#
# Loopabull fedmsg plugin
#   http://www.fedmsg.com/en/latest/
#

from loopabull.plugin import Plugin

import fedmsg

class FedmsgLooper(Plugin):
    """
    Loopabull plugin to implement looper for fedmsg event loop
    """
    def __init__(self, config={}):
        """
        stub init
        """
        self.key = "FedmsgLooper"
        super(FedmsgLooper, self).__init__(self)

    def looper(self):
        """
        Implementation of the generator to feed the event loop
        """
        for name, endpoint, topic, msg in fedmsg.tail_messages(mute=True):
            yield (topic, dict(msg))


# vim: set expandtab sw=4 sts=4 ts=4
