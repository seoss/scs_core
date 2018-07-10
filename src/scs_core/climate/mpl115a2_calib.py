"""
Created on 20 Jun 2018

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

example JSON:
{"calibrated-on": "2018-06-20T10:25:39.045+00:00", "c25": 511}
"""

import os

from collections import OrderedDict

from scs_core.data.datum import Datum
from scs_core.data.json import PersistentJSONable
from scs_core.data.localized_datetime import LocalizedDatetime


# --------------------------------------------------------------------------------------------------------------------

class MPL115A2Calib(PersistentJSONable):
    """
    NXP MPL115A2 digital barometer - temperature calibration
    """

    DEFAULT_C25 = 472                                 # T adc counts at 25 ºC

    # ----------------------------------------------------------------------------------------------------------------

    __FILENAME = "mpl115a2_calib.json"

    @classmethod
    def filename(cls, host):
        return os.path.join(host.conf_dir(), cls.__FILENAME)


    # ----------------------------------------------------------------------------------------------------------------

    @classmethod
    def construct_from_jdict(cls, jdict):
        if not jdict:
            return None

        calibrated_on = Datum.datetime(jdict.get('calibrated-on'))
        c25 = jdict.get('c25')

        return MPL115A2Calib(calibrated_on, c25)


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, calibrated_on, c25):
        """
        Constructor
        """
        super().__init__()

        self.__calibrated_on = calibrated_on        # LocalizedDatetime
        self.__c25 = Datum.int(c25)                 # T adc count at 25 ºC


    # ----------------------------------------------------------------------------------------------------------------

    def save(self, host):
        if self.__calibrated_on is None:
            self.__calibrated_on = LocalizedDatetime.now()

        super().save(host)


    # ----------------------------------------------------------------------------------------------------------------

    def as_json(self):
        jdict = OrderedDict()

        jdict['calibrated-on'] = self.calibrated_on
        jdict['c25'] = self.c25

        return jdict


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def calibrated_on(self):
        return self.__calibrated_on


    @property
    def c25(self):
        return self.__c25


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "MPL115A2Calib:{calibrated_on:%s, c25:%s}" % (self.calibrated_on, self.c25)