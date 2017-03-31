"""
 Loopabull fedmsg rabbitmq plugin
   https://www.rabbitmq.com/

 This plugin is specific to consuming fedmsg[0] messages that have been
 serialized into rabbitmq using fedmsg-rabbitmq-serializer[1].

 Messages are JSON-serialized and UTF-8 encoded.

   Example::

       {
           "topic": "consumer.fmn.prefs.update",
           "body": {
               "topic": "consumer.fmn.prefs.update",
               "msg_id": "<year>-<random-uuid>",
               "msg": {
                   "openid": "<user's openid who updated their preferences>"
               }
           }
       }

 [0] - http://www.fedmsg.com/en/latest/
 [1] - https://pagure.io/fedmsg-rabbitmq-serializer
"""

import json
import pika
import logging

from loopabull.plugin import Plugin
from loopabull import Result


class FedmsgrabbitmqLooper(Plugin):
    """
    Loopabull plugin to implement looper for fedmsg event loop
    """

    def __init__(self, config={}):
        """
        stub init
        """
        self.key = "FedmsgrabbitmqLooper"
        self.config = config
        super(FedmsgrabbitmqLooper, self).__init__(self)

        # setup logging
        self.logger = logging.getLogger("loopabull")

        # host config entry in loopabull.yml for the looper
        self.host = self.config.get("host", "localhost")

        # Which channel queue should we listen to?
        self.channel_queue = self.config.get("channel_queue", "workers")

        self.delivery_tag = None

        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.host)
        )

        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.channel_queue, durable=True)
        self.channel.basic_qos(prefetch_count=1)

    def looper(self):
        """
        Implementation of the generator to feed the event loop
        """
        for method_frame, header_frame, body in \
                self.channel.consume(self.channel_queue):

            if method_frame == None or body == None:
                # The queue is likely empty, give loopabull fake data to throw
                # away as the None routing key should never be routable
                self.delivery_tag = None
                yield (None, {"nodata": "throw away"})

            else:
                # The channel.consume() will yield a tuple of length 3, the
                # third element (index 2) will be the message payload in JSON
                #
                # We can assume the format because we know the input from the
                # serializer
                self.delivery_tag = method_frame.delivery_tag
                payload_body = json.loads(body)
                yield (payload_body[u'topic'], payload_body[u'body'])

    def done(self, result, **kwargs):
        """
        looper execution completion handler
        """

        logging.info("RESULT: {}".format(result))

        if self.delivery_tag:
            if result in (Result.runfinished, Result.unrouted):
                self.channel.basic_ack(delivery_tag=self.delivery_tag)
            elif result == (Result.error, Result.runerrored):
                self.channel.basic_nack(delivery_tag=self.delivery_tag)


# vim: set expandtab sw=4 sts=4 ts=4
