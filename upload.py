#!/usr/bin/python

import sys
import redis
import requests

key, name, stdoutval = sys.argv[1:]

r = redis.StrictRedis(host='', port=, password='')

with open(name, 'rb') as infile:
    data = infile.read()
    print "Setting key %s" % key
    r.set(key, data)
    val = {'stdout': stdoutval, 'server': requests.get('http://metadata/computeMetadata/v1/instance/hostname', headers={'Metadata-Flavor':'Google'}).text}
    r.sadd('upload', val)
    print "Done setting key %s" % key
