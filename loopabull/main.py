#!/usr/bin/env python
#
# Loopabull - an event loop driven ansible execution engine
#

import os
import sys
import imp
import yaml
import logging
import tempfile
import argparse
import subprocess

import loopabull
from loopabull import Result

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

    def load_config(self, config_path):
        """
        Load the various values from the config
        """

        with open(config_path, 'r') as conf_yaml:
            config = yaml.safe_load(conf_yaml)

        self.plugins_metadata = dict()

        # Set log level from config file, allow for some common synonyms that
        # people would likely expect to work.
        #
        # Default to info
        conf_loglevel = config.get("loglevel", "info").lower()
        if conf_loglevel in ["debug", "debugging"]:
            loopabull.logger.setLevel(logging.DEBUG)
            loopabull.logger.info("Log Level Set: DEBUG")
        elif conf_loglevel in ["warn", "warning"]:
            loopabull.logger.setLevel(logging.WARNING)
            loopabull.logger.info("Log Level Set: WARNING")
        elif conf_loglevel in ["error"]:
            loopabull.logger.setLevel(logging.ERROR)
            loopabull.logger.info("Log Level Set: ERROR")
        elif conf_loglevel in ["info"]:
            loopabull.logger.setLevel(logging.INFO)
            loopabull.logger.info("Log Level Set: INFO")

        # Load user plugins
        for plugin, plugin_config in config["plugins"].items():
            self.compose_plugin_dict(plugin_config, plugin.lower())
        # Fall back to defaults
        if "looper" not in self.plugins_metadata:
            self.compose_plugin_dict({"name": "fedmsg"}, "looper")
        if "translator" not in self.plugins_metadata:
            self.compose_plugin_dict({"name": "rkname"}, "translator")

        try:
            self.routing_keys = config["routing_keys"]
        except IndexError as e:
            print(
                "Invalid config, missing routing_keys section - {}".format(e)
            )
            sys.exit(1)

        try:
            self.ansible = config["ansible"]
            self.ansible['playbooks_dir']
            self.ansible['cfg_file_path']
            self.ansible['playbook_cmd']
        except IndexError as e:
            print(
                "Invalid config, missing valid ansible section - {}".format(e)
            )
            sys.exit(1)

    def compose_plugin_dict(self, plugin_config, plugin_type):
        """
        A generic composer for setting up a plugins metadata for loading later on
        """
        name = plugin_config["name"].lower()
        plugin_type = plugin_type.lower()

        plugin_data = dict()
        plugin_data["name"] = name
        plugin_data["plugin_type"] = plugin_type
        plugin_data["internal_name"] = name + plugin_type
        plugin_data["module_name"] = name.capitalize() + plugin_type.capitalize()
        plugin_data["config"] = plugin_config

        loopabull.logger.debug("plugin_data: {}".format(plugin_data))

        self.plugins_metadata[plugin_type] = plugin_data

    def load_plugin(self):
        """
        load plugin
        """
        self.plugins = dict()

        for plugin_type in self.plugins_metadata:
            plugin_meta = self.plugins_metadata[plugin_type]

            loopabull.logger.debug(
                "plugin_type: {}\nplugin_metadata: {}\n".format(
                    plugin_type,
                    plugin_meta
                )
            )

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
                )(plugin_meta["config"])
            except (IOError, OSError, ImportError, SyntaxError, KeyError) as e:
                print(
                    "Failure to load module: {} : {} - {}".format(
                        plugin_meta["name"],
                        plugin_path,
                        e
                    )
                )
                sys.exit(2)

    def run_playbook(self):
        """
        Run the playbooks.
        """
        loopabull.logger.info("Waiting on messages")
        for plugin_rk, plugin_dict in self.plugins["looper"].looper():
            loopabull.logger.info("Message from routing key: %s", plugin_rk)
            loopabull.logger.debug(
                "Message dict: {}".format(plugin_rk, plugin_dict)
            )

            if plugin_rk not in self.routing_keys and self.routing_keys[0] != "all":
                loopabull.logger.info("Unsupported routing_key: %s", plugin_rk)
                self.plugins["looper"].done(Result.unrouted)
                continue

            try:
                tmp_varfile = tempfile.mkstemp()
                with open(tmp_varfile[-1], 'w') as yaml_file:
                    yaml.safe_dump(plugin_dict, yaml_file, allow_unicode=False)

                cmd = [self.ansible['playbook_cmd']]
                cmd.append(os.path.join(
                    self.ansible['playbooks_dir'],
                    self.plugins["translator"].translate_path(plugin_rk) + '.yml',
                ))
                cmd.extend(['-e', '@{}'.format(tmp_varfile[-1])])

                print('Running: %s' % cmd)

                ansible_sp = subprocess.Popen(
                    cmd,
                    env={'ANSIBLE_CONFIG': self.ansible['cfg_file_path']}
                )
                ansible_sp.communicate()
                loopabull.logger.info(
                    "Ansible run done and returned: %s", ansible_sp.returncode)

                if ansible_sp.returncode == 0:
                    self.plugins["looper"].done(Result.runfinished)
                else:
                    self.plugins["looper"].done(
                        Result.runerrored,
                        exitcode=ansible_sp.returncode)
            except Exception as ex:
                loopabull.logger.exception(
                    "An un-expected exception was raised in the code")
                self.plugins["looper"].done(Result.error, exception=ex)
                # For now, we raise it (and thus crash).
                raise

    def run(self):
        """
        Run loopabull
        """
        try:
            self.run_playbook()
        except KeyboardInterrupt:
            loopabull.logger.info(
                "User stopped loopabull")
        finally:
            self.plugins["looper"].close()


# vim: set expandtab sw=4 sts=4 ts=4
