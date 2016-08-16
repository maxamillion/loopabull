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

        # set variable from conf file
        self.load_config(config_path)

        # load plugin
        self.load_plugin()

        # put together the
        self.compose_ansible_playbook_command()

    def load_config(self, config_path):
        """
        Load the various values from the config
        """

        with open(config_path, 'r') as conf_yaml:
            config = yaml.safe_load(conf_yaml)

        try:
            self.plugin_name = config["plugin"]
            self.plugin_name_internal = self.plugin_name + "looper"
            self.plugin_module_name = self.plugin_name.capitalize() + "Looper"
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
            if 'inventory_path' not in self.ansible:
                raise IndexError
            if 'playbooks_dir' not in self.ansible:
                raise IndexError
        except IndexError as e:
            print(
                "Invalid config, missing valid ansible section - {}".format(e)
            )
            sys.exit(1)

    def compose_ansible_playbook_command(self):
        """
        Put together ansible-playbook command with different options based on
        configuration settings
        """

        ansible_cmd = "ansible-playbook -i {}".format(
            self.ansible["inventory_path"]
        )

        if 'modules_dir' in self.ansible:
            ansible_cmd += " -M {}".format(self.ansible["modules_dir"])

        self.ansible_cmd = ansible_cmd

    def load_plugin(self):
        """
        load plugin
        """

        try:
            plugin_path = os.path.join(
                os.path.dirname(__file__),
                'plugins',
                "{}{}".format(self.plugin_name_internal,".py"),
            )
            plugin_module = imp.load_source(
                self.plugin_name_internal,
                plugin_path
            )
            self.plugin = getattr(
                plugin_module,
                self.plugin_module_name
            )()
        except (IOError, OSError, ImportError, SyntaxError) as e:
            print(
                "Failure to load module: {} : {} - {}".format(
                    self.plugin_name,
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
            if plugin_rk in self.routing_keys or self.routing_keys[0] == "all":
                tmp_varfile = tempfile.mkstemp()
                with open(tmp_varfile[-1], 'w') as yaml_file:
                    yaml.safe_dump(plugin_dict, yaml_file, allow_unicode=False)

                ansible_sp = subprocess.Popen(
                    "{} -e @{} {}.yml".format(
                        self.ansible_cmd,
                        tmp_varfile[-1],
                        os.path.join(self.ansible["playbooks_dir"], plugin_rk),
                    ).split(),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                ansible_out, ansible_err = ansible_sp.communicate()
                print ansible_out
                print ansible_err



# vim: set expandtab sw=4 sts=4 ts=4
