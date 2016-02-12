class Event(object):
    def __init__(self, tme, pid, ppid, **kwargs):
        self._tme = tme
        self._pid = pid
        self._ppid = ppid
        for key in kwargs.keys():
            self.__setattr__(key, kwargs[key])

    @property
    def tme(self):
        return self._tme

    @tme.setter
    def tme(self, value=None):
        self._tme = value

    @property
    def pid(self):
        return self._pid

    @pid.setter
    def pid(self, value=None):
        self._pid = value

    @property
    def ppid(self):
        return self._ppid

    @ppid.setter
    def ppid(self, value=None):
        self._ppid = value

    def __repr__(self):
        return "%s(tme=%.1f, pid=%d, ppid=%d, %s)" % (
            self.__class__.__name__,
            self.tme,
            self.pid,
            self.pid,
            ', '.join("%s=%r" % (attr, getattr(self, attr)) for attr in vars(self))
        )


class ProcessStartEvent(Event):
    def __init__(self, tme, pid, ppid, **kwargs):
        Event.__init__(self, tme, pid, ppid, **kwargs)


class ProcessExitEvent(Event):
    def __init__(self, tme, pid, ppid, start_tme, **kwargs):
        Event.__init__(self, tme, pid, ppid, start_tme=start_tme, **kwargs)


class TrafficEvent(Event):
    def __init__(self, tme, pid, ppid, value, **kwargs):
        Event.__init__(self, tme, pid, ppid, **kwargs)
        self._value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value=None):
        self._value = value
