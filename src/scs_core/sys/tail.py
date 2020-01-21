"""
Created on 20 Jan 2020

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)


https://stackoverflow.com/questions/16175745/read-new-line-with-pynotify
https://www.linode.com/docs/development/monitor-filesystem-events-with-pyinotify/
"""

from pyinotify import EventsCodes, Notifier, ProcessEvent, WatchManager


# --------------------------------------------------------------------------------------------------------------------

class Tail(object):
    """
    classdocs
    """

    DEFAULT_TIMEOUT =   2000        # TODO: 120000              # 2 minutes in milliseconds

    # ----------------------------------------------------------------------------------------------------------------

    __IN_MODIFY =       EventsCodes.FLAG_COLLECTIONS['OP_FLAGS']['IN_MODIFY']
    __IN_CLOSE_WRITE =  EventsCodes.FLAG_COLLECTIONS['OP_FLAGS']['IN_CLOSE_WRITE']

    __IN_EVENTS =       __IN_MODIFY | __IN_CLOSE_WRITE


    # ----------------------------------------------------------------------------------------------------------------

    @classmethod
    def construct(cls, path, timeout=None):
        handler = TailEventHandler(path)

        watch_manager = WatchManager()
        watch_manager.add_watch(path, cls.__IN_EVENTS)

        notifier_timeout = cls.DEFAULT_TIMEOUT if timeout is None else timeout
        notifier = TailNotifier(watch_manager, default_proc_fun=handler, timeout=notifier_timeout)

        return cls(notifier, handler)


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, notifier, handler):
        """
        Constructor
        """
        self.__notifier = notifier                              # TailNotifier
        self.__handler = handler                                # TailEventHandler


    def __iter__(self):
        return self.readlines()


    # ----------------------------------------------------------------------------------------------------------------

    def open(self):
        self.__handler.open_file()


    def close(self):
        self.__handler.close_file()


    def readlines(self):
        # existing lines...
        for line in self.__handler.readlines():
            yield line

        # new lines...
        for line in self.__notifier.loop(self.__handler.readlines):
            yield line

        raise StopIteration()


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "Tail:{handler:%s}" %  self.__handler


# --------------------------------------------------------------------------------------------------------------------

class TailEventHandler(ProcessEvent):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, path):
        """
        Constructor
        """
        super().__init__()

        self.__path = path

        self.__file = None
        self.__terminate = False


    # ----------------------------------------------------------------------------------------------------------------

    def open_file(self):
        self.__file = open(self.__path)


    def close_file(self):
        if self.__file is None:
            return

        self.__file.close()
        self.__file = None


    def readlines(self, _notifier=None):
        if self.__terminate:
            return False

        for line in self.__file.readlines():
            yield line.strip()


    # ----------------------------------------------------------------------------------------------------------------

    # noinspection PyPep8Naming

    def process_IN_MODIFY(self, _event):
        pass


    # noinspection PyPep8Naming

    def process_IN_CLOSE_WRITE(self, _event):
        self.__terminate = True


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "TailEventHandler:{path:%s, terminate:%s}" % (self.__path, self.__terminate)


# --------------------------------------------------------------------------------------------------------------------

class TailNotifier(Notifier):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, watch_manager, default_proc_fun=None, read_freq=0, threshold=0, timeout=None):
        super().__init__(watch_manager, default_proc_fun, read_freq, threshold, timeout)


    # ----------------------------------------------------------------------------------------------------------------

    def loop(self, callback=None, _daemonize=False, **_args):
        try:
            while True:
                self.process_events()

                response = callback(self)

                if response is False:
                    break                               # file closed

                for line in response:
                    yield line

                if not self.check_events():
                    break                               # timeout

                self.read_events()

        except (BrokenPipeError, KeyboardInterrupt, SystemExit):
            pass

        finally:
            self.stop()