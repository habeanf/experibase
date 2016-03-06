#!/usr/bin/python

from settings import *

import redis
import os
import subprocess
from time import sleep
import logging
import json
import requests
from datetime import datetime

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
        os.system("sudo shutdown -h now")


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


def heartbeat(task):
    r.set(task['run'] + '-' + task['exp'],
          json.dumps({'heartbeat': str(datetime.now()),
                      'lastdone': task.get('lastdonestage', None)}))


def uploadfiles(task, files):
    run = task['run']
    logging.info("compressing files")
    subprocess.call(['bash','-c',' '.join(['tar', 'czvf', str(task['num']) + '.results.tar.gz'] + files + ['log', 'interm*'])])
    logging.info("Uploading files")
    subprocess.call(['gsutil', 'cp', str(task['num']) + '.results.tar.gz',
                     'gs://yapresearch/' + run + '/'])
    # subprocess.call(['rm', 'results.tar.gz'])


def resetdir(files):
    subprocess.call(['rm'] + files + ['interm*'])


def markcomplete(task):
    r.sadd(task['run']+'-done', task['exp'])


def run_task(task, files):
    cmds = task['cmds']
    outfiles = task['outfiles']
    cmdouts = zip(cmds, outfiles)
    logfile = 'stdout.log'  # always empty for some reason
    for cmd, outfile in cmdouts:
        logging.info('Running cmd %s; logging to (%s, %s)' %
                     (cmd, logfile, outfile))
        stdout, stderr = open(logfile, 'w'), open(outfile, 'w')
        files += [stdout, stderr]
        p = subprocess.Popen(cmd.split(), stdout=stdout, stderr=stderr)
        logging.info('Started cmd %s' % (cmd,))
        while not iscomplete(p):
            logging.info('Sleeping..')
            sleep(POLL_INTERVAL)
            heartbeat(task)
            logging.info("process poll awakened")
        logging.info('cmd ended closing files')
        [f.close() for f in files]
        task['lastdonestage'] = cmd
        logging.info("cmd ended")
    uploadfiles(task, outfiles)
    markcomplete(task)
    resetdir(outfiles)


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
    run_task(task, FILES)
    task = gettask()

shutdown('done')
