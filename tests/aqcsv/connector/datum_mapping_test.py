#!/usr/bin/env python3

"""
Created on 11 Mar 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

from scs_core.aqcsv.connector.datum_mapping import DatumMapping

from scs_core.data.json import JSONify
from scs_core.data.path_dict import PathDict


# --------------------------------------------------------------------------------------------------------------------

datum_mapping = DatumMapping("particulates", "pm2p5", "scs-particulates")
print(datum_mapping)
print("-")

jstr = '{"rec": "2019-03-11T13:59:00Z", ' \
        '"particulates": {"val": {"pm1": 3.5, "pm2p5": 5.0, "pm10": 5.6}, "tag": "scs-bgx-401", "src": "N2"}, ' \
        '"status": {"val": {"tz": {"name": "Europe/London", "utc-offset": "+00:00"}, ' \
        '"sch": {"scs-particulates": {"tally": 1.0, "interval": 10.0}, ' \
        '"scs-status": {"tally": 1.0, "interval": 60.0}, ' \
        '"scs-climate": {"tally": 1.0, "interval": 60.0}, "scs-gases": {"tally": 1.0, "interval": 10.0}}, ' \
        '"gps": {"pos": [50.83390976, -0.13919364], "qual": 1.0, "elv": 44.1}, ' \
        '"airnow": {"site": 826987654321.0}}, ' \
        '"tag": "scs-bgx-401"}}'

print(jstr)
print("-")

datum = PathDict.construct_from_jstr(jstr)
print(datum)
print("-")

print("     tag: %s" % datum_mapping.tag(datum))
print("   value: %s" % datum_mapping.value(datum))
print("  source: %s" % datum_mapping.source(datum))
print("duration: %s" % datum_mapping.duration(datum))
print("   s-map: %s" % datum_mapping.source_mapping(datum))
print("-")

print(JSONify.dumps(datum_mapping))
print("-")
