"""
Created on 20 Oct 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

from collections import OrderedDict

from scs_core.sample.sample import Sample


# --------------------------------------------------------------------------------------------------------------------

class ParticulatesSample(Sample):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, tag, rec, sample):
        """
        Constructor
        """
        bins = OrderedDict([(i, sample.bins[i]) for i in range(len(sample.bins))])

        super().__init__(tag, rec, ('per', sample.period),
                         ('pm1', sample.pm1), ('pm2p5', sample.pm2p5), ('pm10', sample.pm10), ('bins', bins),
                         ('mtf1', sample.bin_1_mtof), ('mtf3', sample.bin_3_mtof), ('mtf5', sample.bin_5_mtof),
                         ('mtf7', sample.bin_7_mtof))