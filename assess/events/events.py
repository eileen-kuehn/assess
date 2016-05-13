"""
Module implements the different kind of events that are supported in dynamic process trees.
"""


class Event(object):
    """
    Base event class that offers convenience methods to create single events.
    """
    def __init__(self, tme, pid, ppid, **kwargs):
        self._tme = tme
        self._pid = pid
        self._ppid = ppid
        for key in kwargs.keys():
            self.__setattr__(key, kwargs[key])

    @staticmethod
    def from_tree(tree):
        """
        Method that returns a event generator based on a given tree.

        :param tree: Tree the generator is based on
        :return: Tree event generator
        """
        for node in tree.nodes(depth_first=False):
            # TODO: how to pass on complete dict?
            yield ProcessStartEvent(tme=node.tme, pid=node.pid, ppid=node.ppid, name=node.name)

    @staticmethod
    def start(tme, pid, ppid, **kwargs):
        """
        Method that returns a ProcessStartEvent by given parameters.

        :param tme: The tme when the process was started
        :param pid: The pid of the process
        :param ppid: The pid of the parent process
        :param kwargs: Additional parameters
        :return: Created start event
        """
        # TODO: handle different parameters from process
        return ProcessStartEvent(tme, pid, ppid, **kwargs)

    @staticmethod
    def exit(tme, pid, ppid, start_tme, **kwargs):
        """
        Method that returns a ProcessExitEvent by given parameters.

        :param tme: The tme when the process was exited
        :param pid: The pid of the process
        :param ppid: The pid of the parent process
        :param start_tme: The start tme of the process
        :param kwargs: Additional parameters
        :return: Created exit event
        """
        # TODO: handle different parameters from process
        return ProcessExitEvent(tme, pid, ppid, start_tme, **kwargs)

    @property
    def tme(self):
        """
        Property method to access the tme of the event.

        :return: Timestamp of the event
        """
        return self._tme

    @tme.setter
    def tme(self, value=None):
        """
        Setter method to set the tme of the event.

        :param value: Value to be set for tme
        """
        self._tme = value

    @property
    def pid(self):
        """
        Parameter to get the pid of the event.

        :return: Events pid
        """
        return self._pid

    @pid.setter
    def pid(self, value=None):
        """
        Setter method to set the pid of the event.

        :param value: Value to be set for pid
        """
        self._pid = value

    @property
    def ppid(self):
        """
        Parameter to get the ppid of the event.

        :return: Events ppid
        """
        return self._ppid

    @ppid.setter
    def ppid(self, value=None):
        """
        Setter method to set the ppid of the event.

        :param value: Value to be set for ppid
        """
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
    """
    Class that represents a start event.
    """
    def __init__(self, tme, pid, ppid, **kwargs):
        Event.__init__(self, tme, pid, ppid, **kwargs)


class ProcessExitEvent(Event):
    """
    Class that represents an exit event.
    """
    def __init__(self, tme, pid, ppid, start_tme, **kwargs):
        Event.__init__(self, tme, pid, ppid, start_tme=start_tme, **kwargs)


class TrafficEvent(Event):
    """
    Class that represents a traffic event.
    """
    def __init__(self, tme, pid, ppid, value, **kwargs):
        Event.__init__(self, tme, pid, ppid, **kwargs)
        self._value = value

    @property
    def value(self):
        """
        Method to get the amount of traffic related to the event.

        :return: Traffic amount
        """
        return self._value

    @value.setter
    def value(self, value=None):
        """
        Setter to set the amount of traffic for the event.

        :param value: Traffic amount to be set 
        """
        self._value = value
