=========
loopabull
=========

Event loop driven `Ansible`_ `playbook`_ execution engine.

General Concept
===============

You have some event loop that will produce a tuple ``(routing_key, [dict])``
where the ``routing_key`` will also be the name of the `Ansible`_ `playbook`_
and the ``[dict]`` is a `python`_ `dictionary`_ that contains the payload of the
event loop which will be fed to the Ansible playbook as `extra variables`_.

The event loop is an abstraction layer, this can be any kind of event loop that
you can dream up as long as you can write a plugin which has a `python`_
`generator`_ that will produce tuples of the form ``(routing_key, [dict])`` as
described above.

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

The Event Loop
==============

The event loop itself is meant to be the thing that executes ansible playbooks
while the event loop plugins are meant to an abstraction to the idea of what will
feed information to the event loop. The original thought was for a message bus
but even that was thought to be too specific.

Configuration
=============

The configuration file will be `YAML`_ to follow in the trend of Ansible, this
config file will be passed to ``loopabull`` at execution time and will decide how
the application functions

routing keys
------------

In order to limit the routing keys that ``loopabull`` will trigger an action on
we will define a list of them in our config file. We might want to limit this in
the scenario of a message bus feeding the event loop plugin and we only want to
take action on the correct routing keys.

The following example is using the `fedmsg`_ loopabull plugin and the routing
keys in this example originate from the `Fedora fedmsg`_ specific
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

plugins
-------

List of plugins to use, none are enabled by default and loopabull will exit
non-zero and throw an error message explaining that a valid configuration file
must be provided.

At this time more than one plugin used at a time per loopabull instance is not
supported.

.. clode-block:: yaml

    plugins:
      - fedmsg

Creators
========

- `Adam Miller <https://fedoraproject.org/wiki/User:Maxamillion>`_
- `Ralph Bean <http://threebean.org/>`_


.. _YAML: http://yaml.org/
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

