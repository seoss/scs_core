#!/usr/bin/env python3

"""
Created on 10 Jan 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

from scs_core.data.json import JSONify

from scs_core.position.gpgga import GPGGA
from scs_core.position.gps_location import GPSLocation
from scs_core.position.nmea_sentence import NMEASentence


# --------------------------------------------------------------------------------------------------------------------
# run...

s = NMEASentence.construct("$GPGGA,092725.00,4717.11399,N,00833.91590,E,1,08,1.01,499.6,M,48.0,M,,*5B")
print(s)
print("-")

gga = GPGGA.construct(s)
print(gga)
print("-")

loc = GPSLocation.construct(gga)
print(loc)
print("-")

print(JSONify.dumps(loc))
print("-")
