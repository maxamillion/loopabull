class Plugin(object):
    """ abstract plugin class """

    # unique plugin identification
    # output of this plugin can be found in results specified with this key,
    # same thing goes for input: use this key for providing input for this plugin
    key = None

    def __init__(self, *args, **kwargs):
        """
        constructor
        """

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

