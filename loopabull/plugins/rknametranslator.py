#
# Loopabull filebased playbook hierarchy
#
import os

from loopabull.plugin import Plugin

class RknameTranslator(Plugin):
    """
    Loopabull Translator to check if routing_key is a valid string.
    This is the default method.
    """
    def __init__(self):
        """
        stub init
        """
        self.key = "RknameTranslator"
        super(RknameTranslator, self).__init__(self)

    def translate_path(self, routing_key):
        """
        Return routing_key.
        """
        return routing_key

# vim: set expandtab sw=4 sts=4 ts=4
