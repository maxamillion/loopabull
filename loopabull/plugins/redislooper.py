#
# Loopabull fedmsg plugin
#   http://www.fedmsg.com/en/latest/
#

from loopabull.plugin import Plugin

import time
import redis
import yaml

class RedisLooper(Plugin):
    """
    Loopabull plugin to implement looper for redis event loop
    """
    def __init__(self, config={}):
        """
        stub init
        """
        self.key = "RedisLooper"
        self.config = config
        self.setup_config()
        super(RedisLooper, self).__init__(self)
        
    def setup_config(self):
        """
        Goes through and verifies the config settings and fall back to sane defaults
        """
        self.config.get("host", "127.0.0.1")
        self.config.get("port", 6379)
        self.config.get("db", 0)

    def looper(self):
        """
        Implementation of the generator to feed the event loop
        """

        self.redis_connection = redis.StrictRedis(host=self.host, port=self.port, db=self.db)
        pubsub = self.redis_connection.pubsub()
        pubsub.psubscribe('*')

        for message in pubsub.listen():
            try:
                # TODO: create parser plugins and allow people to configure them in config
                payload = yaml.load(message["data"])
            except Exception:
                payload = dict()
                payload["msg"] = message["data"]

            yield(message["channel"], payload)

# vim: set expandtab sw=4 sts=4 ts=4
