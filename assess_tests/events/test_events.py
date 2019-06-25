import unittest

from assess.events.events import *


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
