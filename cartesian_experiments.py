#!/usr/bin/python
"""Generate cartesian product of experiment variables for execution"""


import redis
import itertools
# from pprint import pprint
import os
import json

GROUPS = []
CMDS = []
REPLACE_STR = '$exp'

from settings import *

r = redis.StrictRedis(host=REDIS_ENDPOINT, port=REDIS_PORT,
                      password=REDIS_PASSWORD)


# first transform optional to empty, existing
for (name, conf) in GROUPS:
    if conf.get('use', None) == 'optional':
        conf['values'] = ['not'+conf['value'], conf['value']]

conf_values = map(lambda (name, conf): conf['values'], GROUPS)

executions = list(itertools.product(*conf_values))

def gen_agg_file(values, out_name):
    with open(out_name, 'w') as outf:
        for value in values:
            with open(value) as inf:
                outf.write(inf.read())

for execution in executions:
    print 'At execution %s' % str(execution)
    files = [BASE_FILE]
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
    #     if conf['type'] == 'file':
    #         if conf['use'] == 'agg':
    #             files += conf['values'][:conf['values'].index(param)+1]
    #         if conf['use'] == 'optional' and param:
    #             files.append(param)
    for execcmd in CMDS:
        task = dict(zip(map(lambda (k, v): k, GROUPS), execution))
        for name, value in task.items():
            if value[0:3] == 'not':
                value = ''
            execcmd = execcmd.replace('$'+name, value)
        task.get('cmds',[]).append(execcmd)
        print execcmd
    # execcmd = execcmd.replace('$exp', '_'.join(execution))
    #     print execcmd
    task['outfiles'] = OUTFILES
    exp_string = '_'.join(map(lambda s:s.replace('-',''),execution))
    task['exp'] = exp_string
    print exp_string

    # r.sadd(TASK_KEY, json.dumps(task))
    # exp_string = '_'.join(exp_strings)
    # outname = CONF_FILE % exp_string
    # print command_line_options
    # gen_agg_file(files, outname)
    # new_command = BASE.replace('$conf', outname).replace('$exp', exp_string, 2).replace('$flags', ' '.join(command_line_options))
    # print 'Executing %s' % new_command
    # os.system(new_command)
