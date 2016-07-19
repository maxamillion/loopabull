#!/usr/bin/env python
#
# Loopabull - an event loop driven ansible execution engine
#

import os
import yaml
import subprocess
import tempfile


class Loopabull(object):
    """
    Main Loopabull object

    This is where ansible will be executed
    """

    def __init__(self, config):
        """
        Loopable __init__
        """

        self.load_config(config)

    def load_config(self, config):
        """
        Load the various values from the config
        """

        self.plugin = config.plugin
        self.routing_keys = config.routing_keys

    def load_plugin(self, plugin_name):
        """
        load plugin
        """

    def run(self):
        """
        Run the playbooks
        """

        for plugin_rk, plugin_dict in self.plugin.looper():
            if plugin_rk in self.routing_keys:
                tmp_varfile = tempfile.mkstemp()
                with open(tmp_varfile[-1], 'w') as yaml_file:
                    yaml.safe_dump(plugin_dict, yaml_file, allow_unicode=False)

                ansible_sp = subprocess.Popen(
                    "ansible-playbook {}.yml -i inventory.txt -e @{}".format(
                        plugin_rk,
                        tmp_varfile[-1]
                    ).split(),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                ansible_out, ansible_err = ansible_sp.communicate()
                print ansible_out
                print ansible_err

# vim: set expandtab sw=4 sts=4 ts=4
