#!/usr/bin/python

import redis
import json

r = redis.StrictRedis(host='', port=, password='')

done = r.smembers('done')
for raw_experiment in done:
    # val = '{' + raw_experiment[29:]
    val = raw_experiment
    exp = json.loads(val.replace("u'", "'").replace("'", '"'))
    exp_name = exp['stdout'].split('.')[1]
    print "Found result %s" % (exp_name,)
    results_data = r.get(exp_name)
    if results_data:
        print "Getting experiment %s" % exp_name
        with open("%s.tar.gz" % exp_name, 'wb') as outfile:
            outfile.write(results_data)
        r.delete(exp_name)
