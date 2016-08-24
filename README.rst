=========
loopabull
=========
.. image:: https://badge.fury.io/py/loopabull.svg
    :target: https://badge.fury.io/py/loopabull

.. image:: https://raw.githubusercontent.com/maxamillion/loopabull/master/images/loopabull.png

NOTE: THIS IS PRE-ALPHA QUALITY AT THIS TIME - UNDER HEAVY DEVELOPMENT
======================================================================

Event loop driven `Ansible`_ `playbook`_ execution engine.

General Concept
===============

You have some event loop that will produce a tuple ``(routing_key, [dict])``
where the ``routing_key`` will also be the name of the `Ansible`_ `playbook`_
and the ``[dict]`` is a `python`_ `dictionary`_ that contains the payload of the
event loop which will be fed to the Ansible playbook as `extra variables`_.

The event loop is an abstraction layer, this can be any kind of event loop that
you can dream up as long as you can write a plugin which provides a `python`_
`generator`_ function called ``looper`` that will produce tuples of the form
``(routing_key, [dict])`` as described above.

Ansible playbooks will then be executed like the following:

.. code-block:: python

    "ansible-playbook {}.yml -i {} -e @{}".format(
        routing_key,
        inventory_file,
        tmp_varfile
    )

In the code above, the ``ansible-playbook`` command is populated with the
``routing_key`` given to us from the event loop plugin and the ``.yml`` suffix
is appended. The contents of the ``[dict]`` from event loop plugin are written
to a tempfile (using `tmpfile.mkstemp`_) and passed to ``ansible-playbook``
using the ``-e @FILENAME`` syntax. Finally the playbook is executed.

::

    +-----------------+             +---------------+
    |                 |             |               |
    |    Events       +------------>|  Looper       |
    |                 |             |   (plugin)    |
    |                 |             |               |
    +-----------------+             +---------------+
                                                 |
                                                 |
                 +-------------------+           |
                 |                   |           |
                 |                   |           |
                 |    Loopabull      +<----------+
                 |  (Event Loop)     |
                 |                   |
                 +---------+---------+
                           |
                           |
                           |
                           |
                           V
                +----------+-----------+
                |                      |
                |   ansible-playbook   |
                |                      |
                +----------------------+



The Event Loop
==============

The event loop itself is meant to be the thing that executes ansible playbooks
while the plugins are meant to be an abstraction to the idea of what will feed
information to the event loop. The original idea was for a message bus to be
the input but even that was thought to be too specific.

Configuration
=============

.. note::
    Example configs can be found in the ``examples`` directory.

The configuration file will be `YAML`_ to follow in the trend of Ansible, this
config file will be passed to ``loopabull`` at execution time and will decide how
the application functions

routing keys
------------

In order to limit the routing keys that ``loopabull`` will trigger an action on
we will define a list of them in our config file. We might want to limit this in
the scenario of a message bus feeding the event loop plugin and we only
want to take action on the correct routing keys.

The following example is using the `fedmsg`_ loopabull plugin and the
routing keys in this example originate from the `Fedora fedmsg`_ specific
implementation.

.. code-block:: yaml

    routing_keys:
      - org.fedoraproject.prod.autocloud.image.success
      - org.fedoraproject.prod.releng.atomic.twoweek.complete

There is a reserved entry of a list with a single element in it and that element
is of the string value ``"all"``

.. code-block:: yaml

    routing_keys:
      - all

plugin
-------

This is a simple key/value assignment of the string representation of the plugin
to use as plugin to feed information to the event loop. None are enabled by
default and loopabull will exit non-zero and throw an error message explaining
that a valid configuration file must be provided.

At this time more than one plugin used at a time per loopabull instance is not
supported.

.. code-block:: yaml

    plugin: fedmsg

Current list of available plugins:

* fedmsg
* rkdirectory
* rkname

ansible
-------

Provide some information about ansible. Currently we need ``inventory_path`` and
``playbooks_dir``.

There is also the ability to optionally pass a ``modules_dir`` which will tell
``ansible-playbook`` where to find ansible modules not in the default location.

.. code-block:: yaml

    ansible:
      inventory_path: /path/to/inventory.txt
      playbooks_dir: /path/to/dir/where/playbooks/are/
      modules_dir: /path/to/custom/modules/location/

Writing Plugins
===============

Something to note is that in Loopabull, plugins are internally called "loopers"
for no real reason other than to isolate the namespace so that we don't collide
with the modules uses as data providers to the plugins.

As such, plugins shall be named ``${PLUGIN_NAME}looper.py`` and implement
a class named ``${PLUGIN_NAME_CAPITALIZED}Looper``

Example below (filename ``examplelooper.py``:

.. code-block:: python

    from loopabull.plugin import Plugin

    class ExampleLooper(Plugin):
        def __init__(self):
            self.key = "ExampleLooper"
            super(ExampleLooper, self).__init__(self)

        def looper(self):
            # A python generator implementation
            yield (router_key, dict(data))

Note that the configuration file entry for this will simply be "example" and the
rest of the mapping of the plugin to it's namespace is handled internally.

.. code-block:: yaml

    plugin: example

Hacking / Example
=================

An example of executing this from git checkout using the provided examples
configurations.

.. code-block:: bash

    $ git clone https://github.com/maxamillion/loopabull.git

    $ cd loopabull/

    $ PYTHONPATH=. bin/loopabull examples/configs/fedmsg_example.yml


This is also how you can hack on loopabull in your local checkout using the same
example command as above.


Installing
==========

Distro Packaging
----------------

If you find yourself on a `Fedora`_, `Red Hat Enterprise Linux`_, or `CentOS`_
system then you can use the `this COPR yum/dnf repository`_ and simply install
with ``yum`` or ``dnf``.

pypi
----

Loopabull is currently available in pypi.

::

    pip install loopabull

Creators
========

- `Adam Miller <https://fedoraproject.org/wiki/User:Maxamillion>`_
- `Ralph Bean <http://threebean.org/>`_

Image Credit
------------

The (currently interim) logo originated as a Public Domain entry found on
`Wikimedia Commons
<https://commons.wikimedia.org/wiki/File:Bull_cartoon_04.svg>`_ and was
originally created by `Mariana Ruiz Villarreal
<https://commons.wikimedia.org/wiki/User:LadyofHats>`_. It was then (very
amateurly/badly) edited by `Adam Miller`_.

.. _YAML: http://yaml.org/
.. _Fedora: https://getfedora.org/
.. _CentOS: https://www.centos.org/
.. _Red Hat Enterprise Linux: https://www.redhat.com/rhel
.. _Adam Miller: https://fedoraproject.org/wiki/User:Maxamillion
.. _Ralph Bean: http://threebean.org/
.. _python: https://www.python.org/
.. _fedmsg: http://www.fedmsg.com/en/latest/
.. _Ansible: https://github.com/ansible/ansible
.. _generator: https://wiki.python.org/moin/Generators
.. _playbook: http://docs.ansible.com/ansible/playbooks.html
.. _Fedora fedmsg: https://fedora-fedmsg.readthedocs.io/en/latest/
.. _tmpfile.mkstemp:
    https://docs.python.org/2/library/tempfile.html#tempfile.mkstemp
.. _dictionary:
    https://docs.python.org/3/library/stdtypes.html?highlight=dict#dict
.. _extra variables:
    http://docs.ansible.com/ansible/playbooks_variables.html#passing-variables-on-the-command-line
.. _this COPR yum/dnf repository:
    https://copr.fedorainfracloud.org/coprs/maxamillion/loopabull/
