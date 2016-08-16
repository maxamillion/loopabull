# This file is part of fedmsg.
# Copyright (C) 2016 Red Hat, Inc.
#
# fedmsg is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3 of the License, or (at your option) any later version.
#
# fedmsg is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with fedmsg; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
#
# Authors:
#   Adam Miller <admiller@redhat.com>
#   Ralph Bean <rbean@redhat.com>
#

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

install_requires = []
with open('requirements.txt', 'r') as req_file:
    for line in req_file:
        install_requires.append(line.strip())

tests_require = []
with open('requirements-test.txt', 'r') as testreq_file:
    for line in testreq_file:
        tests_require.append(line.strip())

description = "Event loop driven Ansible playbook execution engine"

setup(
    name='loopabull',
    version='0.0.3',
    description=description,
    long_description=description,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 2.7',
        'Topic :: System :: Systems Administration',
    ],
    author='Adam Miller',
    author_email='admiller@redhat.com',
    url='https://github.com/maxamillion/loopabull',
    license='GPLv3+',
    install_requires=install_requires,
    tests_require=tests_require,
    test_suite='py.test',
    packages=find_packages(),
    include_package_data=True,
    scripts=['bin/loopabull'],
)
# vim: set expandtab sw=4 sts=4 ts=4
