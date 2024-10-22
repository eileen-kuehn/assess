"""
Module implements the different kind of events that are supported in dynamic
process trees.
"""
from typing import List, Dict, Iterator, TypeVar, TYPE_CHECKING

if TYPE_CHECKING:
    from assess.prototypes.simpleprototypes import OrderedTreeNode

E = TypeVar('E')
E_co = TypeVar('E_co', bound='Event', contravariant=True)


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

    @classmethod
    def from_node(cls: E, node: 'OrderedTreeNode') -> Iterator[E]:
        return NotImplemented

    @classmethod
    def from_tree(cls, tree, supported: Dict[E_co, bool] = None) -> Iterator[E_co]:
        """
        Method that returns a event generator based on a given tree.

        :param tree: Tree the generator is based on
        :param supported: Supported event types
        :return: Tree event generator
        """
        # FIXME: exit events are send before the child nodes are processed
        for node in tree.nodes(order_first=True):
            yield from cls.events_from_node(node, supported)

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
    def events_from_node(cls, node, supported: Dict[E_co, bool] = None) -> Iterator[E_co]:
        """
        Method that yields available events for a given node.

        :param node: The node to create the events for
        :return: yields supported event types
        """
        for event_type in event_types:
            if supported.get(event_type, False):
                yield from event_type.from_node(node)

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
        return "%s(tme=%.1f, pid=%s, ppid=%s, value=%s, %s)" % (
            self.__class__.__name__,
            self.tme,
            self.pid,
            self.ppid,
            self.value,
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

    def __init__(self, tme, pid, ppid, value=0, **kwargs):
        Event.__init__(self, tme, pid, ppid, value, **kwargs)

    @classmethod
    def from_node(cls, node):
        event_dict = vars(node).copy()
        if "pid" not in event_dict:
            event_dict["pid"] = event_dict.node_id
            event_dict["ppid"] = event_dict.parent.node_id
        yield cls(**event_dict)


class ProcessExitEvent(Event):
    """
    Class that represents an exit event.
    """

    def __init__(self, tme, pid, ppid, start_tme, value=None, **kwargs):
        Event.__init__(self, tme, pid, ppid, value=value or (tme - start_tme),
                       start_tme=start_tme, **kwargs)
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

    @classmethod
    def from_node(cls, node):
        event_dict = vars(node).copy()
        event_dict["value"] = event_dict["exit_tme"] - event_dict["tme"]
        event_dict["start_tme"] = event_dict["tme"]
        event_dict["tme"] = event_dict["exit_tme"]
        if "pid" not in event_dict:
            event_dict["pid"] = event_dict["node_id"]
            event_dict["ppid"] = event_dict.parent["node_id"]
        yield cls(**event_dict)


class TrafficEvent(Event):
    """
    Class that represents a traffic event.
    """

    def __init__(self, tme, pid, ppid, value, **kwargs):
        Event.__init__(self, tme, pid, ppid, value=value, **kwargs)

    @classmethod
    def from_node(cls, node):
        try:
            for traffic in node.traffic:
                if traffic.in_rate > 0:
                    yield cls(**super().create_traffic(
                        traffic, "in_rate", traffic.in_rate))
                if traffic.out_cnt > 0:
                    yield cls(**super().create_traffic(
                        traffic, "out_rate", traffic.out_rate))
        except AttributeError:
            pass


class ParameterEvent(Event):
    """
    Class that represents any parameter event.
    """
    def __init__(self, tme, pid, ppid, name, value, **kwargs):
        Event.__init__(self, tme, pid, ppid, value=value, name=name, **kwargs)

    @classmethod
    def from_node(cls, node):
        parameters = node.parameters()
        for parameter, values in parameters.items():
            yield cls(
                tme=getattr(values, "tme", node.tme),
                pid=node.pid,
                ppid=node.pid,
                name=parameter,
                value=values
            )


event_types: List[Event] = [ProcessStartEvent, TrafficEvent, ParameterEvent,
                            ProcessExitEvent]
