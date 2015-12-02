#!/usr/bin/python

from settings import *

import redis
import os
from time import sleep
import logging

logging.basicConfig(filename='log', level=logging.DEBUG)

r = redis.StrictRedis(host=REDIS_ENDPOINT, port=REDIS_PORT,
                      password=REDIS_PASSWORD)

task_id = None


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


def iscomplete():
    return True


def iserror():
    pass


def poll():
    logging.info("Poll awakened")
    samplestate()
    if iscomplete() or iserror():
        logging.info("Execution %s" % ("complete" if iscomplete() else "error"))
        # upload resuls
        # update state
        # shutdown
        logging.info("Shutting down")
        shutdown('done')
        return False
    return True


def run_task(task):
    logging.info('Running task %s' % (task,))


def gettask():
    attempts = 0
    while attempts < MAX_TASK_ATTEMPTS:
        numtasks = r.scard(TASK_KEY)
        if numtasks > 0:
            return r.spop(TASK_KEY)
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

run_task(task)

while poll():
    sleep(POLL_TIMER)
