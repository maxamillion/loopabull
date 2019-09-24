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
        each looper plugin has to implement this method

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

    def translate_path(self, routing_key):
        """
        each path translator plugin has to implement this method

        this method should take a string(routing_key) and return string with a
        path to a playbook sans the leading "playbook/" directory and the post
        ".yml" file type.

        Example usage:
            playbook = plugin.translate_path("com.example.playbooks.install")
        """
        raise NotImplementedError()

    def done(self, result, **kwargs):
        """
        a looper plugin can implement this method optionally

        result is a value of loopabull.Result.

        kwargs includes extra variables that depends on the result value.
        For Result.runerrored, an exitcode kwarg is provided with the ansible
        exit code.
        For result.Error, an exception kwarg is provided with the Exception
        object.

        This function will always be called exactly once for every call to
        looper(), and it will be the result of handling the very last returned
        message by looper().
        """
        pass


    def close(self):
        """
        a looper plugin can implement this method optionally

        This function will be called when loopabull stops. It allows the
        plugin to close any connections that may need to be close at the
        end of the process.
        """
        pass

# vim: set expandtab sw=4 sts=4 ts=4
