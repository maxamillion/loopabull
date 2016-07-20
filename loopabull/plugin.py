class Plugin(object):
    """ abstract plugin class """

    def __init__(self, key):
        """
        constructor
        """

        self.key = key

    def __str__(self):
        return "{}".format(self.key)

    def __repr__(self):
        return "Plugin(key='{}')".format(self.key)

    def looper(self):
        """
        each plugin has to implement this method

        this method should be generator that yields the following tuple:

            (routing_key, [dict])

        such that the routing_key is the key to link to an ansible playbook
        and the [dict] is python dict representation of the payload to pass
        to the ansible playbook as variables

        Example usage:
            for routing_key, payload_dict in plugin.looper():
                # do something

        """
        raise NotImplementedError()

# vim: set expandtab sw=4 sts=4 ts=4
