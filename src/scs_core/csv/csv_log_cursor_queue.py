"""
Created on 20 Jan 2020

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import json

from collections import OrderedDict

from scs_core.csv.csv_log import CSVLog, CSVLogFile
from scs_core.csv.csv_reader import CSVReader, CSVReaderException

from scs_core.data.json import JSONable
from scs_core.data.localized_datetime import LocalizedDatetime

from scs_core.sys.filesystem import Filesystem


# --------------------------------------------------------------------------------------------------------------------

class CSVLogCursorQueue(JSONable):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    @classmethod
    def construct_for_log(cls, log: CSVLog, rec_field):                         # these cursors are NOT live
        queue = OrderedDict()

        if log.timeline_start is not None:
            for directory_path in cls.__directory_paths(log):
                for log_file in cls.__log_files(log, directory_path):
                    cursor = CSVLogCursor.construct_for_log_file(log, log_file, rec_field)

                    if cursor is not None:
                        queue[cursor.file_path] = cursor

        return cls(queue)


    @staticmethod
    def __directory_paths(log: CSVLog):
        from_directory = CSVLog.directory_name(log.timeline_start)

        root_directory = Filesystem.ls(log.root_path)

        if root_directory is None:
            raise RuntimeError("inaccessible log root directory: %s" % log.root_path)

        for directory in root_directory:
            if directory.name < from_directory:
                continue

            yield directory.path()


    @staticmethod
    def __log_files(log: CSVLog, directory_path):
        for file in Filesystem.ls(directory_path):
            log_file = CSVLogFile.construct(file)

            if log_file.tag != log.tag:
                continue

            if log_file.topic_name != log.topic_name:
                continue

            if log_file.created_datetime.date() < log.timeline_start.date():
                continue

            yield log_file


    # ----------------------------------------------------------------------------------------------------------------

    @classmethod
    def construct_from_jdict(cls, jdict):
        if not jdict:
            return None

        queue = OrderedDict()

        for cursor_jdict in jdict.get('queue'):
            cursor = CSVLogCursor.construct_from_jdict(cursor_jdict)
            queue[cursor.file_path] = cursor

        return cls(queue)


    # ----------------------------------------------------------------------------------------------------------------
    #

    def __init__(self, queue=None):
        """
        Constructor
        """
        self.__queue = OrderedDict() if queue is None else queue        # OrderedDict of CSVLogCursor


    def __len__(self):
        return len(self.__queue)


    # ----------------------------------------------------------------------------------------------------------------

    def as_json(self):
        jdict = OrderedDict()

        jdict['queue'] = [cursor.as_json() for cursor in self.__queue.values()]

        return jdict


    # ----------------------------------------------------------------------------------------------------------------

    def include(self, file_path, is_live):
        if file_path is None:
            return

        if file_path in self.__queue.keys():
            return                                          # assume that the cursor is already live

        if is_live:
            for key in self.__queue.keys():
                self.__queue[key].is_live = False           # there shall only be one live file

        self.__queue[file_path] = CSVLogCursor(file_path, 0, is_live)


    def next(self):
        return next(iter(self.__queue.values()), None)      # the first item is the oldest item


    def remove(self, file_path):
        try:
            del self.__queue[file_path]
        except KeyError:
            pass


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        queue = '[' + ', '.join(str(cursor) for cursor in self.__queue.values()) + ']'

        return "CSVLogCursorQueue:{queue:%s}" %  queue


# --------------------------------------------------------------------------------------------------------------------

class CSVLogCursor(JSONable):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    @classmethod
    def construct_for_log_file(cls, log: CSVLog, log_file, rec_field):          # this cursor is NOT live
        reader = None
        row_number = 0

        try:
            reader = CSVReader.construct_for_file(log_file.path(), numeric_cast=False)

            for row in reader.rows():
                try:
                    datum = json.loads(row, object_pairs_hook=OrderedDict)
                except ValueError:
                    continue

                if rec_field not in datum:
                    raise KeyError(rec_field)

                rec = LocalizedDatetime.construct_from_iso8601(datum[rec_field])

                if rec is None:
                    raise ValueError(datum[rec_field])

                if rec.datetime > log.timeline_start:
                    return cls(log_file.path(), row_number, False)

                row_number += 1

            return None

        except CSVReaderException:
            return None

        finally:
            if reader is not None:
                reader.close()


    # ----------------------------------------------------------------------------------------------------------------

    @classmethod
    def construct_from_jdict(cls, jdict):
        if not jdict:
            return None

        file_path = jdict.get('file-path')
        row = jdict.get('row')
        is_live = jdict.get('is-live')

        return cls(file_path, row, is_live)


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, file_path, row, is_live):
        """
        Constructor
        """
        self.__file_path = file_path                            # string
        self.__row = int(row)                                   # int
        self.__is_live = bool(is_live)                          # bool


    def __eq__(self, other):
        return self.file_path == other.file_path


    # ----------------------------------------------------------------------------------------------------------------

    def as_json(self):
        jdict = OrderedDict()

        jdict['file-path'] = self.file_path
        jdict['row'] = self.row
        jdict['is-live'] = self.is_live

        return jdict


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def file_path(self):
        return self.__file_path


    @property
    def row(self):
        return self.__row


    @property
    def is_live(self):
        return self.__is_live


    @is_live.setter
    def is_live(self, is_live):
        self.__is_live = is_live


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "CSVLogCursor:{file_path:%s, row:%s, is_live:%s}" %  \
               (self.file_path, self.row, self.is_live)