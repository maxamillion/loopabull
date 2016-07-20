#!/usr/bin/env python
#
# Loopabull - an event loop driven ansible execution engine
#

import os
import sys
import imp
import yaml
import tempfile
import argparse
import subprocess


class Loopabull(object):
    """
    Main Loopabull object

    This is where ansible will be executed
    """

    def __init__(self, config_path):
        """
        Loopable __init__
        """

        self.load_config(config_path)
        self.load_plugin()

    def load_config(self, config_path):
        """
        Load the various values from the config
        """

        with open(config_path, 'r') as conf_yaml:
            config = yaml.safe_load(conf_yaml)

        try:
            self.plugin = config["plugin"]
        except IndexError as e:
            print("Invalid config, missing plugin section - {}".format(e))
            sys.exit(1)

        try:
            self.routing_keys = config["routing_keys"]
        except IndexError as e:
            print(
                "Invalid config, missing routing_keys section - {}".format(e)
            )
            sys.exit(1)

        try:
            self.ansible = config["ansible"]
            if 'inventory_path' not in self.ansible.keys():
                raise IndexError
            if 'playbook_dir' not in self.ansible.keys():
                raise IndexError
        except IndexError as e:
            print(
                "Invalid config, missing valid ansible section - {}".format(e)
            )
            sys.exit(1)

    def load_plugin(self):
        """
        load plugin
        """

        try:
            plugin_path = os.path.join(
                os.path.dirname(__file__),
                'plugins',
                "{}{}".format(self.plugin,".py"),
            )
            imp.load_source(self.plugin, plugin_path)
        except (IOError, OSError, ImportError, SyntaxError) as e:
            print(
                "Failure to load module: {} : {} - {}".format(
                    self.plugin,
                    plugin_path,
                    e
                )
            )
            sys.exit(2)

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
                    "ansible-playbook {}.yml -i {} -e @{}".format(
                        plugin_rk,
                        self.ansible["inventory_path"],
                        tmp_varfile[-1]
                    ).split(),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                ansible_out, ansible_err = ansible_sp.communicate()
                print ansible_out
                print ansible_err


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="event loop driven ansible execution engine"
    )

    parser.add_argument('config', help='path to loopabull YAML config file')

    args = parser.parse_args()

    lbull = Loopabull(args.config)
    lbull.run()

# vim: set expandtab sw=4 sts=4 ts=4
