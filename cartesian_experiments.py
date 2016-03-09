#!/usr/bin/python
"""Generate cartesian product of experiment variables for execution"""


import redis
import itertools
from pprint import pprint
import subprocess
import json

GROUPS = []
CMDS = []
REPLACE_STR = '$exp'

from settings import *

r = redis.StrictRedis(host=REDIS_ENDPOINT, port=REDIS_PORT,
                      password=REDIS_PASSWORD)


def gen_agg_file(values, out_name):
    with open(out_name, 'w') as outf:
        for value in values:
            with open(value) as inf:
                outf.write(inf.read())


# first transform optional to empty, existing
for (name, conf) in GROUPS:
    if conf.get('use', None) == 'optional':
        conf['values'] = ['not'+conf['value'], conf['value']]
    if conf.get('type', None) == 'file' and conf.get('use', None) == 'agg':
        # generate aggregative files
        outfiles = []
        for i in range(len(conf['values'])):
            v = conf['values'][:i+1]
            outfile = "%s.%s.yaml" % ('_'.join(v), RUN_NAME)
            outfiles.append(outfile)
            gen_agg_file(map(lambda s: conf['dir'] + '/' + s, [conf['base']] + v), outfile)
        archive_name = '%s.%s.tar.gz' % (RUN_NAME, name)
        print 'Archiving agg conf files to %s' % archive_name
        subprocess.call(['tar', 'czf', archive_name] + outfiles)
        print 'Uploading'
        subprocess.call(['gsutil', 'cp', archive_name,  'gs://yapresearch/'])
        conf['values'] = outfiles


conf_values = map(lambda (name, conf): conf['values'], GROUPS)

executions = list(itertools.product(*conf_values))


for i, execution in enumerate(executions):
    print 'At execution %s' % str(execution)
    # files = [BASE_FILE]
    exp_strings = []
    command_line_options = []
    options = {}
    # for i, param in enumerate(execution):
    #     conf_name, conf = GROUPS[i]
    #     # print "\tAt conf %s" % conf_name
    #     # pprint(conf)
    #     # print "\tparam is %s" % str(param)
    #     if conf['type'] == 'option' and param:
    #         print "\t\tadd %s=%s to command line" % (conf_name, str(param))
    #         options[conf_name] = param
    #         # print "\t\tadd %s to command line" % str(conf['value'])
    #         # command_line_options.append(conf['value'])
    #     if conf.get('use', None) == 'optional':
    #         exp_strings.append(conf_name if param else 'no%s' % conf_name)
    #     else:
    #         exp_strings.append(param)
    #     if conf['type'] == 'file': #         if conf['use'] == 'agg':
    #             files += conf['values'][:conf['values'].index(param)+1]
    #         if conf['use'] == 'optional' and param:
    #             files.append(param)
    task = dict(zip(map(lambda (k, v): k, GROUPS), execution))
    cmds = []
    for execcmd in CMDS:
        for name, value in task.items():
            if value[0:3] == 'not':
                value = ''
            execcmd = execcmd.replace('$'+name, value)
        cmds.append(execcmd)
    # execcmd = execcmd.replace('$exp', '_'.join(execution))
    #     print execcmd
    task['download'] = '%s.gram.tar.gz' % RUN_NAME
    task['cmds'] = cmds
    task['outfiles'] = OUTFILES
    exp_string = '_'.join(map(lambda s: s.replace('-', ''), execution))
    task['exp'] = exp_string
    task['run'] = RUN_NAME
    task['num'] = i
    print exp_string
    # pprint(task)

    r.sadd(TASK_KEY, json.dumps(task))
    # exp_string = '_'.join(exp_strings)
    # outname = CONF_FILE % exp_string
    # print command_line_options
    # gen_agg_file(files, outname)
    # new_command = BASE.replace('$conf', outname).replace('$exp', exp_string, 2).replace('$flags', ' '.join(command_line_options))
    # print 'Executing %s' % new_command
    # os.system(new_command)
