"""
Created on 26 Aug 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import os
import time


# --------------------------------------------------------------------------------------------------------------------

class QueueReport(object):
    """
    classdocs
   """

    __BACKLOG_MIN = 4

    # ----------------------------------------------------------------------------------------------------------------

    @classmethod
    def load(cls, filename):
        if not os.path.isfile(filename):
            return QueueReport(None)

        f = open(filename, 'r')
        line = f.readline()
        f.close()

        return QueueReport(int(line.strip()))


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, length):
        """
        Constructor
        """
        self.__length = length                  # int or None


    # ----------------------------------------------------------------------------------------------------------------

    def has_backlog(self):
        return self.__length is not None and self.__length > self.__BACKLOG_MIN


    def save(self, filename):
        if self.__length is None:
            return

        # file...
        tmp_filename = filename + '.' + str(int(time.time()))

        f = open(tmp_filename, 'w')
        f.write(str(self.__length) + '\n')
        f.close()

        # atomic operation...
        os.rename(tmp_filename, filename)


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def length(self):
        return self.__length


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "QueueReport:{length:%s}" % self.length
