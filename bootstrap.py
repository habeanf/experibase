#!/usr/bin/python

from settings import *

import redis
import os
import subprocess
from time import sleep
import logging
import json
import requests

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(filename='log', level=logging.DEBUG, format=FORMAT)

r = redis.StrictRedis(host=REDIS_ENDPOINT, port=REDIS_PORT,
                      password=REDIS_PASSWORD)

task_id = None

FILES = []

hostname = requests.get('http://metadata/computeMetadata/v1/instance/hostname',
                        headers={'Metadata-Flavor': 'Google'}).text


def shutdown(reason):
    # notify of shutdown with log
    if DO_SHUTDOWN:
        os.system("shutdown -h now")


def run_command(cmd):
    pass


def samplestate():
    pass


def uploadresult():
    pass


def iscomplete(process):
    return process.poll() is not None


def iserror(process):
    return False


def poll(process, task):
    logging.info("Poll awakened")
    samplestate()
    if iserror(process) or iscomplete(process):
        logging.info("Execution %s" %
                     ("complete" if iscomplete(process) else "error"))
        # closing files
        [f.close() for f in FILES]
        # upload resuls
        # update state
        task['server'] = hostname
        r.sadd('done', task)
        # shutdown
        logging.info("Shutting down")
        shutdown('done')
        return False
    return True


def run_task(task, files):
    cmd = task['cmd']
    logfile = 'runstatus.log'
    errfile = 'error.log'
    logging.info('Running cmd %s; logging to (%s, %s)' % (cmd, logfile, errfile))
    stdout, stderr = open(logfile, 'w'), open(errfile, 'w')
    files += [stdout, stderr]
    return subprocess.Popen(cmd.split(), stdout=stdout, stderr=stderr)


def gettask():
    attempts = 0
    while attempts < MAX_TASK_ATTEMPTS:
        numtasks = r.scard(TASK_KEY)
        if numtasks > 0:
            raw_task = r.spop(TASK_KEY)
            task = json.loads(raw_task)
            return task
        logging.info(
            "No task found, waiting %d seconds for and another %d retries" %
            (GET_TASK_WAIT, MAX_TASK_ATTEMPTS-attempts))
        sleep(GET_TASK_WAIT)
        attempts += 1
    logging.info("No task found")
    return None


task = gettask()
if not task:
    shutdown('no task found')

while task:
    logging.info("Got task %s" % (str(task),))
    process = run_task(task, FILES)
    while poll(process, task):
        sleep(POLL_INTERVAL)
    task = gettask()
