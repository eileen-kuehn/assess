import unittest

from assess.events.events import *


class TestEventFunctionality(unittest.TestCase):
    def test_creation(self):
        event = Event.start(0, 0, 1)
        self.assertEqual(type(event), ProcessStartEvent)

        event_2 = Event.exit(1, 0, 1, 0)
        self.assertEqual(type(event_2), ProcessExitEvent)
