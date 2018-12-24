"""
Created on 13 Aug 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

Note that, for the ISO 8601 constructors, milliseconds are optional.

http://www.saltycrane.com/blog/2009/05/converting-time-zones-datetime-objects-python/
"""

import pytz
import re
import tzlocal

from datetime import datetime, timedelta, timezone


# TODO: object should carry a flag indicating presence of millis - for "preserve millis" mode

# --------------------------------------------------------------------------------------------------------------------

class LocalizedDatetime(object):
    """
    classdocs
    """

    @classmethod
    def now(cls):
        zone = tzlocal.get_localzone()
        localized = datetime.now(zone)

        return LocalizedDatetime(localized)


    @classmethod
    def construct_from_date(cls, date):             # TODO: deprecated
        zone = tzlocal.get_localzone()
        localized = zone.localize(datetime(date.year, date.month, date.day))

        return LocalizedDatetime(localized)


    @classmethod
    def construct_from_timestamp(cls, t, tz=None):
        zone = tzlocal.get_localzone() if tz is None else tz
        localized = datetime.fromtimestamp(t, zone)

        return LocalizedDatetime(localized)


    @classmethod
    def construct_from_iso8601(cls, datetime_str):
        if datetime_str is None:
            return None

        # Z timezone offset...
        localized = cls.__construct_from_iso8601_z(datetime_str)

        if localized:
            return localized

        # numeric timezone offset...
        return cls.__construct_from_iso8601_numeric(datetime_str)


    @classmethod
    def construct_from_jdict(cls, jdict):           # TODO: deprecated
        return cls.construct_from_iso8601(jdict)


    # ----------------------------------------------------------------------------------------------------------------

    @classmethod
    def __construct_from_iso8601_z(cls, datetime_str):
        # match...
        match = re.match('(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:.(\d{3}))?Z', datetime_str)

        if match is None:
            return None

        fields = match.groups()

        # fields...
        year = int(fields[0])
        month = int(fields[1])
        day = int(fields[2])

        hour = int(fields[3])
        minute = int(fields[4])
        second = int(fields[5])
        micros = int(fields[6]) * 1000 if fields[6] else 0

        # construct...
        zone_offset = timedelta(hours=0, minutes=0)
        zone = timezone(zone_offset)

        localized = datetime(year, month, day, hour, minute, second, micros, tzinfo=zone)

        return LocalizedDatetime(localized)


    @classmethod
    def __construct_from_iso8601_numeric(cls, datetime_str):
        # match...
        match = re.match('(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:.(\d{3}))?([ +\-]?)(\d{2}):(\d{2})',
                         datetime_str)

        if match is None:
            return None

        fields = match.groups()

        # fields...
        year = int(fields[0])
        month = int(fields[1])
        day = int(fields[2])

        hour = int(fields[3])
        minute = int(fields[4])
        second = int(fields[5])
        micros = int(fields[6]) * 1000 if fields[6] else 0

        zone_sign = -1 if fields[7] == '-' else 1
        zone_hours = int(fields[8])
        zone_mins = int(fields[9])

        # construct...
        zone_offset = zone_sign * timedelta(hours=zone_hours, minutes=zone_mins)
        zone = timezone(zone_offset)

        localized = datetime(year, month, day, hour, minute, second, micros, tzinfo=zone)

        return LocalizedDatetime(localized)


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, localized):
        """
        Constructor
        """
        self.__datetime = localized             # datetime


    def __add__(self, other: datetime):         # TODO: check validity of __add__(..)
        return LocalizedDatetime(self.__datetime + other)


    def __sub__(self, other):                   # TODO: check validity of __sub__(..)
        other_datetime = other.__datetime if type(other) == LocalizedDatetime else other

        return self.__datetime - other_datetime


    # ----------------------------------------------------------------------------------------------------------------

    def utc(self):
        localized = self.datetime.astimezone(pytz.timezone('Etc/UTC'))

        return LocalizedDatetime(localized)


    def localize(self, zone):                           # zone may be datetime.timezone or pytz.timezone
        localized = self.datetime.astimezone(zone)

        return LocalizedDatetime(localized)


    def timedelta(self, days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0):
        td = timedelta(days=days, seconds=seconds, microseconds=microseconds, milliseconds=milliseconds,
                       minutes=minutes, hours=hours, weeks=weeks)

        return LocalizedDatetime(self.__datetime + td)


    # ----------------------------------------------------------------------------------------------------------------

    def as_iso8601(self, include_millis=False):
        """
        example: 2016-08-13T00:38:05.210+01:00
        """
        date = self.__datetime.strftime("%Y-%m-%d")
        time = self.__datetime.strftime("%H:%M:%S")

        # millis...
        if include_millis:
            micros = float(self.__datetime.strftime("%f"))
            millis = ".%03d" % (micros // 1000)

        else:
            millis = ""

        # time zone...
        zone = self.__datetime.strftime("%z")

        # Z format...
        if float(zone[1:]) == 0.0:
            return "%sT%s%sZ" % (date, time, millis)

        # numeric format...
        zone_hours = zone[:3]
        zone_mins = zone[3:]

        return "%sT%s%s%s:%s" % (date, time, millis, zone_hours, zone_mins)


    def as_time(self):
        time = self.__datetime.strftime("%H:%M:%S")

        micros = float(self.__datetime.strftime("%f"))
        millis = "%03d" % (micros // 1000)

        return "%s.%s" % (time, millis)


    def timestamp(self):
        return self.__datetime.timestamp()


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def datetime(self):
        return self.__datetime


    @property
    def utc_datetime(self):
        utc_localised = self.utc()

        return utc_localised.datetime


    @property
    def tzinfo(self):
        return self.__datetime.tzinfo


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "LocalizedDatetime:{datetime:%s}" % self.datetime
