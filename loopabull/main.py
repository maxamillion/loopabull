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

        self.plugins_metadata = dict()

        # Setup the looper plugin metadata
        try:
            self.plugins_metadata["looper"] = self.compose_plugin_dict(config["plugin"], "looper")
        except IndexError as e:
            print("Invalid config, missing plugin section - {}".format(e))
            sys.exit(1)

        try:
            self.plugins_metadata["translator"] = self.compose_plugin_dict(config["path_translator"], "translator")
        except KeyError as e:
            self.plugins_metadata["translator"] = self.compose_plugin_dict("rkname", "translator")

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

    def compose_plugin_dict(self, name, plugin_type):
        """
        A generic composer for setting up a plugins metadata for loading later on
        """
        name = name.lower()
        plugin_type = plugin_type.lower()

        plugin_data = dict()
        plugin_data["name"] = name
        plugin_data["plugin_type"] = plugin_type
        plugin_data["internal_name"] = name + plugin_type
        plugin_data["module_name"] = name.capitalize() + plugin_type.capitalize()

        return plugin_data

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
        self.plugins = dict()

        for plugin_type in self.plugins_metadata:
            plugin_meta = self.plugins_metadata[plugin_type]
            try:
                plugin_path = os.path.join(
                    os.path.dirname(__file__),
                    'plugins',
                    "{}{}".format(
                        plugin_meta["internal_name"],
                        ".py"
                    ),
                )
                plugin_module = imp.load_source(
                    plugin_meta["internal_name"],
                    plugin_path
                )
                self.plugins[plugin_meta["plugin_type"]] = getattr(
                    plugin_module,
                    plugin_meta["module_name"]
                )()
            except (IOError, OSError, ImportError, SyntaxError, KeyError) as e:
                print(
                    "Failure to load module: {} : {} - {}".format(
                        plugin_meta["name"],
                        plugin_path,
                        e
                    )
                )
                sys.exit(2)

    def run(self):
        """
        Run the playbooks
        """
        for plugin_rk, plugin_dict in self.plugins["looper"].looper():
            if plugin_rk in self.routing_keys or self.routing_keys[0] == "all":
                tmp_varfile = tempfile.mkstemp()
                with open(tmp_varfile[-1], 'w') as yaml_file:
                    yaml.safe_dump(plugin_dict, yaml_file, allow_unicode=False)

                ansible_sp = subprocess.Popen(
                    "{} -e @{} {}.yml".format(
                        self.ansible_cmd,
                        tmp_varfile[-1],
                        os.path.join(
                            self.ansible["playbooks_dir"],
                            self.plugins["translator"].translate_path(plugin_rk)
                        ),
                    ).split(),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                ansible_out, ansible_err = ansible_sp.communicate()
                print ansible_out
                print ansible_err

# vim: set expandtab sw=4 sts=4 ts=4
