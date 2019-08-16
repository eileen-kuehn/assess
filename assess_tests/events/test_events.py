import unittest

from assess.events.events import ProcessStartEvent, Event, ProcessExitEvent, \
    TrafficEvent, ParameterEvent
from assess.prototypes.simpleprototypes import Prototype


class TestEventFunctionality(unittest.TestCase):
    def test_creation(self):
        event = Event.start(0, 0, 1)
        self.assertEqual(type(event), ProcessStartEvent)

        event_2 = Event.exit(1, 0, 1, 0)
        self.assertEqual(type(event_2), ProcessExitEvent)
        self.assertEqual(event_2.start_tme, 0)

        event_3 = Event.add(1, 0, 1, .5)
        self.assertEqual(type(event_3), TrafficEvent)
        self.assertEqual(event_3.value, .5)

    def test_manual_creation(self):
        start = ProcessStartEvent(0, 0, 0)
        start.pid = 2
        start.ppid = 1
        start.tme = 1
        self.assertEqual(start, Event.start(1, 2, 1))

        exit = ProcessExitEvent(0, 0, 0, 0)
        exit.pid = 2
        exit.ppid = 1
        exit.tme = 1
        exit.start_tme = 0
        exit.value = 1
        self.assertEqual(exit, Event.exit(1, 2, 1, 0))

        traffic = TrafficEvent(0, 0, 0, 0)
        traffic.pid = 2
        traffic.ppid = 1
        traffic.tme = 1
        traffic.value = 5
        self.assertEqual(traffic.value, 5)
        self.assertEqual(traffic, Event.add(1, 2, 1, 5))

    def test_number_of_events(self):
        tree = Prototype()
        root = tree.add_node("root", pid=1, ppid=0, tme=0, exit_tme=0, param=2)
        for i in range(5):
            root.add_node("child_%d" % i, pid=i+2, ppid=1, tme=0, exit_tme=0, param=i*2)
        child = next(root.children())
        child.add_node("child", pid=10, ppid=child.pid, tme=0, exit_tme=0, param=5)

        event_count = 0
        for _ in Event.from_tree(tree, supported={
            ProcessStartEvent: True,
            ProcessExitEvent: False,
            ParameterEvent: False
        }):
            event_count += 1
        self.assertEqual(7, event_count)

        event_count = 0
        for _ in Event.from_tree(tree, supported={
            ProcessStartEvent: True,
            ProcessExitEvent: True,
            ParameterEvent: False
        }):
            event_count += 1
        self.assertEqual(14, event_count)

        event_count = 0
        for _ in Event.from_tree(tree, supported={
            ProcessStartEvent: True,
            ProcessExitEvent: True,
            ParameterEvent: True
        }):
            event_count += 1
        self.assertEqual(21, event_count)

    def test_event_order(self):
        tree = Prototype()
        root = tree.add_node("root", pid=1, ppid=0, tme=0, exit_tme=0, param=2)
        for i in range(5):
            root.add_node("child_%d" % i, pid=i + 2, ppid=1, tme=0, exit_tme=0,
                          param=i * 2)
        child = next(root.children())
        child.add_node("child", pid=8, ppid=child.pid, tme=0, exit_tme=0, param=5)

        nodes = []
        for event in tree.event_iter(supported={
            ProcessStartEvent: True,
            ProcessExitEvent: True,
            ParameterEvent: True
        }):
            print(event)
            if type(event) == ProcessStartEvent:
                if event.ppid != 0:
                    self.assertTrue(event.ppid in nodes)
                nodes.append(event.pid)
            elif type(event) == ProcessExitEvent:
                self.assertTrue(event.pid in nodes)
                nodes.remove(event.pid)
            elif type(event) == ParameterEvent:
                self.assertTrue(event.pid in nodes)
