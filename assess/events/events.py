"""
Module implements the different kind of events that are supported in dynamic
process trees.
"""
from typing import List, Union


class Event(object):
    """
    Base event class that offers convenience methods to create single events.
    """
    __slots__ = ("tme", "pid", "ppid", "value", "__dict__")

    def __init__(self, tme, pid, ppid, value=None, **kwargs):
        self.tme = tme
        self.pid = pid
        self.ppid = ppid
        self.value = value
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
            yield ProcessStartEvent(
                tme=node.tme,
                pid=node.pid,
                ppid=node.ppid,
                name=node.name
            )

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
        return ProcessStartEvent(tme, pid, ppid, **kwargs)

    @classmethod
    def events_from_node(cls, node):
        """
        Method that returns a available events for a given process.

        :param node: The process to create the events
        :return: tuple of ProcessStartEvent and ProcessExitEvent
        """
        process_dict = vars(node).copy()
        process_exit_dict = vars(node).copy()
        process_exit_dict["start_tme"] = process_exit_dict["tme"]
        process_exit_dict["tme"] = process_exit_dict["exit_tme"]
        process_exit_dict["value"] = process_exit_dict["tme"] - \
            process_exit_dict["start_tme"]

        if "pid" not in process_dict:
            process_dict["pid"] = process_dict.get("node_id", None)
            process_exit_dict["pid"] = process_dict.get("node_id", None)
            if process_dict.get("_parent", None) is not None:
                ppid = process_dict["_parent"].node_id
                process_dict["ppid"] = ppid
                process_exit_dict["ppid"] = ppid
            else:
                process_dict["ppid"] = None
                process_exit_dict["ppid"] = None

        # prepare parameter events
        parameters = node.parameters()
        parameter_event_list: List[Union[TrafficEvent, ParameterEvent]] = []
        for parameter, values in parameters.items():
            # for each of the given parameters an event should be created
            if "traffic" == parameter:
                try:
                    for traffic in values:
                        if traffic.in_rate > 0:
                            parameter_event_list.append(TrafficEvent(
                                **cls.create_traffic(traffic, "in_rate", traffic.in_rate)))
                        if traffic.out_cnt > 0:
                            parameter_event_list.append(TrafficEvent(
                                **cls.create_traffic(traffic, "out_rate", traffic.out_rate)))
                except AttributeError:
                    pass
            else:
                parameter_event_list.append(
                    ParameterEvent(
                        tme=values.tme if hasattr(values, "tme") else process_dict["tme"],
                        pid=process_dict["pid"],
                        ppid=process_dict["pid"],
                        name=parameter,
                        value=values,
                    )
                )

        return ProcessStartEvent(**process_dict), \
            ProcessExitEvent(**process_exit_dict), \
            parameter_event_list

    @staticmethod
    def create_traffic(traffic, variant, value):
        traffic_dict = vars(traffic).copy()
        traffic_dict["ppid"] = traffic_dict["pid"]
        traffic_dict["name"] = "%s_%s" % (traffic_dict["conn_cat"], variant)
        traffic_dict["value"] = value
        traffic_dict["tme"] = traffic_dict.get("tme", 0) + 20
        return traffic_dict

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
        return ProcessExitEvent(
            tme, pid, ppid, start_tme, value=(tme - start_tme), **kwargs)

    @staticmethod
    def add(tme, pid, ppid, value, **kwargs):
        """
        Method that returns a ProcessTrafficEvent by given parameters.

        :param tme: The tme when the traffic was created
        :param pid: Pid of the process
        :param ppid: Pid of the parent process
        :param value: Traffic value
        :param kwargs: Additional parameters
        :return: Created traffic event
        """
        return TrafficEvent(tme, pid, ppid, value, **kwargs)

    def __eq__(self, other):
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return "%s(tme=%.1f, pid=%s, ppid=%s, %s)" % (
            self.__class__.__name__,
            self.tme,
            self.pid,
            self.ppid,
            ', '.join("%s=%r" % (attr, getattr(self, attr)) for attr in vars(self)
                      if attr not in ("tme", "pid", "ppid"))
        )


class EmptyProcessEvent(object):
    """
    Class that represents the event for an empty node
    """
    def __init__(self, **kwargs):
        pass


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

    def __init__(self, tme, pid, ppid, start_tme, value=None, **kwargs):
        Event.__init__(self, tme, pid, ppid, start_tme=start_tme,
                       value=value or (tme - start_tme), **kwargs)
        self._start_tme = start_tme

    @property
    def start_tme(self):
        """
        Method to get the start tme related to the process.

        :return: Start tme
        """
        return self._start_tme

    @start_tme.setter
    def start_tme(self, value=None):
        """
        Setter to set the start tme for the process.

        :param value: Start tme to be set
        """
        self._start_tme = value


class TrafficEvent(Event):
    """
    Class that represents a traffic event.
    """

    def __init__(self, tme, pid, ppid, value, **kwargs):
        Event.__init__(self, tme, pid, ppid, value=value, **kwargs)


class ParameterEvent(Event):
    """
    Class that represents any parameter event.
    """
    def __init__(self, tme, pid, ppid, name, value, **kwargs):
        Event.__init__(self, tme, pid, ppid, value=value, name=name, **kwargs)
