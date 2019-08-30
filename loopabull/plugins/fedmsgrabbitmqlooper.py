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
import logging

import pika
import ssl

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

        # Credentials to connect to the rabbitmq server
        if self.config.get('tls'):
            credentials = pika.credentials.ExternalCredentials()
            config['rabbitmq']['credentials'] = credentials
            context = ssl.create_default_context(
                cafile=self.config['tls']['ca_cert']
            )
            context.load_cert_chain(
                self.config['tls']['certfile'],
                self.config['tls']['keyfile'],
            )
            ssl_options = pika.SSLOptions(context)
            config['rabbitmq']['ssl_options'] = ssl_options
        elif self.config.get('credentials'):
            username = self.config['credentials'].get('username')
            password = self.config['credentials'].get('password')
            credentials = pika.credentials.PlainCredentials(
                username=username,
                password=password,
            )
            config['rabbitmq']['credentials'] = credentials

        self.delivery_tag = None

        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(**config['rabbitmq'])
        )
        self.channel = self.connection.channel()

        # Which channel queue should we listen to?
        if not self.config.get("channel_queue"):
            raise IndexError(
                "channel_queue must be configured for loopabull to work "
                "with rabbitmq")
        queue_config = self.config.get("channel_queue")
        self.channel_queue = queue_config["name"]
        result = self.channel.queue_declare(
            queue=self.channel_queue,
            durable=queue_config.get('durable', False),
            exclusive=queue_config.get('exclusive', True),
            auto_delete=queue_config.get('auto_delete', True),
        )

        if config.get('routing_keys'):
            exchange_name = config.get('exchange', {}).get('name', 'amq.topic')
            for route in config.get('routing_keys'):
                self.logger.debug(
                    "Linking to exchange: %s with routing key: %s",
                    exchange_name, route
                )
                self.channel.queue_bind(
                    exchange=exchange_name,
                    queue=self.channel_queue,
                    routing_key=route,
                )
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
                yield (method_frame.routing_key, {"msg": payload_body})

    def done(self, result, **kwargs):
        """
        looper execution completion handler
        """

        self.logger.info("RESULT: {}".format(result))

        if self.delivery_tag is not None:
            if result in (Result.runfinished, Result.unrouted):
                self.logger.info("acking message: %s", self.delivery_tag)
                self.channel.basic_ack(delivery_tag=self.delivery_tag)
            elif result in (Result.error, Result.runerrored):
                self.logger.info("nacking message: %s", self.delivery_tag)
                self.channel.basic_nack(delivery_tag=self.delivery_tag)
        else:
            self.logger.info("No delivery tag found")

    def close(self):
        """
        Closes all connections.
        """
        requeued_messages = self.channel.cancel()
        print('Requeued %i messages' % requeued_messages)

        # Close the channel and the connection
        self.channel.close()
        self.connection.close()


# vim: set expandtab sw=4 sts=4 ts=4
