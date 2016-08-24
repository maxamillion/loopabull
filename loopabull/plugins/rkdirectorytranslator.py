#
# Loopabull sub-directory playbook hierarchy
#
import os

from loopabull.plugin import Plugin

class RkdirectoryTranslator(Plugin):
    """
    Loopabull PTranslator to convert routing_keys to OS independent file paths.
    """
    def __init__(self):
        """
        stub init
        """
        self.key = "RkdirectoryTranslator"
        super(RkdirectoryTranslator, self).__init__(self)

    def translate_path(self, routing_key):
        """
        Parse routing_key and return the playbook name.
        """
        path = routing_key.split(".")
        
        return os.path.join(*path)

# vim: set expandtab sw=4 sts=4 ts=4
