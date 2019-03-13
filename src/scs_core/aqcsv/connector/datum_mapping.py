"""
Created on 11 Mar 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

example document:
{"topic": "particulates", "species": "pm1", "site-code": null}
"""

from collections import OrderedDict

from scs_core.aqcsv.conf.airnow_site_conf import AirNowSiteConf

from scs_core.aqcsv.connector.source_mapping import SourceMapping

from scs_core.aqcsv.data.aqcsv_datetime import AQCSVDatetime
from scs_core.aqcsv.data.aqcsv_record import AQCSVRecord

from scs_core.data.json import JSONable
from scs_core.data.localized_datetime import LocalizedDatetime
from scs_core.data.path_dict import PathDict

from scs_core.location.timezone import Timezone

from scs_core.position.gps_datum import GPSDatum


# --------------------------------------------------------------------------------------------------------------------

class DatumMapping(JSONable):
    """
    classdocs
    """

    __SCHEDULES = {
        'gases': 'scs-gases',
        'particulates': 'scs-particulates'
    }

    # ----------------------------------------------------------------------------------------------------------------

    @classmethod
    def construct_from_jdict(cls, jdict):
        if jdict is None:
            return None

        topic = jdict.get('topic')
        species = jdict.get('species')
        site_code = jdict.get('site-code')

        return DatumMapping(topic, species, site_code)


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, topic, species, site_code=None):
        """
        Constructor
        """
        self.__topic = topic                                        # string
        self.__species = species                                    # string
        self.__site_code = site_code                                # string


    # ----------------------------------------------------------------------------------------------------------------

    def as_json(self):
        jdict = OrderedDict()

        jdict['topic'] = self.topic
        jdict['species'] = self.species
        jdict['site-code'] = self.site_code

        return jdict


    # ----------------------------------------------------------------------------------------------------------------

    def aqcsv_record(self, datum: PathDict):
        # parameter_code...
        aqcsv_source = self.aqcsv_source(datum)

        if aqcsv_source is None:
            return None

        parameter_code = aqcsv_source.parameter_code

        # site_code / poc...
        if self.__site_code is not None:
            code = self.__site_code
            poc = None

        else:
            site_conf = self.site_conf(datum)

            if site_conf is None:
                return None

            code = site_conf.site.as_code()
            poc = site_conf.poc(parameter_code)

        # datetime_code...
        aqcsv_rec = self.aqcsv_rec(datum)

        # position...
        gps = self.gps(datum)

        if gps is not None:
            lat = gps.pos.lat
            lon = gps.pos.lng
            gis_datum = AQCSVRecord.GIS_DATUM
            elev = round(gps.elv)

        else:
            lat = None
            lon = None
            gis_datum = None
            elev = None

        # record...
        record = AQCSVRecord(
            site_code=code,

            data_status=AQCSVRecord.STATUS_FINAL,
            action_code=AQCSVRecord.ACTION_DEFAULT,

            datetime_code=aqcsv_rec.as_json(),

            parameter_code=parameter_code,

            duration=self.duration(datum),
            frequency=0,

            value=self.value(datum),
            unit_code=aqcsv_source.unit_code,

            qc_code=aqcsv_source.qc_code,
            poc=poc,

            lat=lat,
            lon=lon,
            gis_datum=gis_datum,
            elev=elev,

            method_code=aqcsv_source.method_code,
            mpc_code=aqcsv_source.mpc_code,
            mpc_value=aqcsv_source.mpc_value,

            uncertainty=None,
            qualifiers=None)

        return record


    # ----------------------------------------------------------------------------------------------------------------
    # datum fields...

    @classmethod
    def datum_tag(cls, datum: PathDict):
        return datum.node('status.tag')


    @classmethod
    def site_conf(cls, datum: PathDict):
        jdict = datum.node('status.val.airnow')

        return AirNowSiteConf.construct_from_jdict(jdict)


    @classmethod
    def gps(cls, datum: PathDict):
        jdict = datum.node('status.val.gps')

        return GPSDatum.construct_from_jdict(jdict)


    @classmethod
    def timezone(cls, datum: PathDict):
        jdict = datum.node('status.val.tz')

        return Timezone.construct_from_jdict(jdict)


    # ----------------------------------------------------------------------------------------------------------------
    # status fields...

    def aqcsv_rec(self, datum: PathDict):
        localised = LocalizedDatetime.construct_from_jdict(datum.node('rec'))
        timezone = self.timezone(datum)

        return AQCSVDatetime(localised.datetime, timezone.zone)


    def status_tag(self, datum: PathDict):
        tag_path = '.'.join([self.topic, 'tag'])

        return datum.node(tag_path)


    def aqcsv_source(self, datum: PathDict):
        pk = (self.topic, self.species, self.source(datum))

        return SourceMapping.instance(pk)


    def value(self, datum: PathDict):
        species_path = '.'.join([self.topic, 'val', self.species])

        return datum.node(species_path)


    def source(self, datum: PathDict):
        source_path = '.'.join([self.topic, 'src'])

        return datum.node(source_path)


    def duration(self, datum: PathDict):
        schedule_path = '.'.join(['status.val.sch', self.__SCHEDULES[self.topic]])
        schedule = datum.node(schedule_path)

        return int(schedule['interval']) * int(schedule['tally'])


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def topic(self):
        return self.__topic


    @property
    def species(self):
        return self.__species


    @property
    def site_code(self):
        return self.__site_code


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "DatumMapping:{topic:%s, species:%s, site_code:%s}" % (self.topic, self.species, self.site_code)