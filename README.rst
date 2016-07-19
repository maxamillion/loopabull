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

.. code:: python

    "ansible-playbook {}.yml -i {} -e @{}".format(
        routing_key,
        inventory_file,
        tmp_varfile
    )

In the code above, the ``ansible-playbook`` command is populated with the
``routing_key`` given to us from the event loop plugin and the ``.yml`` suffix
is appended. The contents of the ``[dict]`` from event loop plugin are written
to a tempfile (using `tempfile.mkstemp`_) and passed to ``ansible-playbook``
using the ``-e @FILENAME`` syntax. Finally the playbook is executed.

The Event Loop
==============

The event loop itself is meant to be the thing that executes ansible playbooks
while the event loop plugins are meant to an abstraction to the idea of what will
feed information to the event loop. The original thought was for a message bus
but even that was thought to be too specific.

Creators
========

- `Adam Miller <https://fedoraproject.org/wiki/User:Maxamillion>`_
- `Ralph Bean <http://threebean.org/>`_


.. _python: https://www.python.org/
.. _Ansible: https://github.com/ansible/ansible
.. _generator: https://wiki.python.org/moin/Generators
.. _playbook: http://docs.ansible.com/ansible/playbooks.html
.. _tmpfile.mkstemp:
    https://docs.python.org/2/library/tempfile.html#tempfile.mkstemp
.. _dictionary:
    https://docs.python.org/3/library/stdtypes.html?highlight=dict#dict
.. _extra variables:
    http://docs.ansible.com/ansible/playbooks_variables.html#passing-variables-on-the-command-line
