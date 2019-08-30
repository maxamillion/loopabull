#!/usr/bin/python3

import json
import os
import sys

print(os.environ.get('MY_ENV_VARIABLE'))

msg = sys.argv[1]
msg = json.loads(msg)

user = msg['owner']
name = msg['name']
epoch = msg['epoch']
version = msg['version']
release = msg['release']
instance = msg['instance']

print(
    '{0} built: {1}:{2}-{3}-{4} in {5}'.format(
        user, name, epoch, version, release, instance)
)


print('Plugin done')
