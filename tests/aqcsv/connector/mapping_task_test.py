#!/usr/bin/env python3

"""
Created on 13 Mar 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import json

from scs_core.aqcsv.connector.mapping_task import MappingTask

from scs_core.data.json import JSONify
from scs_core.data.localized_datetime import LocalizedDatetime


# --------------------------------------------------------------------------------------------------------------------

org = "south-coast-science-demo"
group = "brighton"
loc = 1
topic = "particulates"
device = "praxis-000401"
parameters = ("val.pm1", "val.pm2p5", "val.pm10")
checkpoint = "**:/01:00"

site_code = "123MM123456789"
pocs = {"88101": 2, "85101": 3 }

latest_rec = LocalizedDatetime.construct_from_jdict("2019-03-13T12:45:00Z")

task = MappingTask(org, group, loc, topic, device, parameters, checkpoint, site_code, pocs, latest_rec)
print(task)
print("-")

jstr = JSONify.dumps(task)
print(jstr)
print("-")

remade = MappingTask.construct_from_jdict(json.loads(jstr))
print(task)
print("-")

equality = remade == task

print("remade == task: %s" % equality)
print("-")
