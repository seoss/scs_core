"""
Created on 4 Mar 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import json

from abc import ABCMeta, abstractmethod

from scs_core.csv.csv_reader import CSVReader


# --------------------------------------------------------------------------------------------------------------------

class CSVArchive(metaclass=ABCMeta):
    """
    classdocs
    """

    _retrieved = None                # must be overridden - as an {} - by each concrete class

    # ----------------------------------------------------------------------------------------------------------------

    @classmethod
    def retrieve(cls):
        reader = CSVReader(filename=cls.archive_location(), cast=False)

        try:
            for row in reader.rows:
                instance = cls.construct_from_jdict(json.loads(row))

                if instance.pk in cls._retrieved:
                    raise KeyError("duplicate pk '%s' for instance:%s" % (instance.pk, instance))

                cls._retrieved[instance.pk] = instance

        finally:
            reader.close()


    @classmethod
    def keys(cls):
        return cls._retrieved.keys()


    @classmethod
    def instances(cls):
        return cls._retrieved.values()


    @classmethod
    def instance(cls, pk):
        if pk is None:
            return None

        try:
            return cls._retrieved[pk]

        except KeyError:
            return None


    # ----------------------------------------------------------------------------------------------------------------

    @classmethod
    @abstractmethod
    def archive_location(cls):
        return ''


    @classmethod
    @abstractmethod
    def construct_from_jdict(cls, _):
        return None


    # ----------------------------------------------------------------------------------------------------------------

    @abstractmethod
    def pk(self):
        return None