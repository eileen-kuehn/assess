from assess.events.events import ProcessStartEvent, ProcessExitEvent, TrafficEvent


class EventGenerator(object):
    def __init__(self, streamer=None, supported=None):
        self._streamer = streamer
        if supported is None:
            supported = getattr(streamer, "supported", {
                ProcessStartEvent: True,
                ProcessExitEvent: True,
                TrafficEvent: True
            })
        self._supported = supported

    def event_iter(self):
        pass

    def __iter__(self):
        return self.event_iter()

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self._streamer)


class NodeGenerator(object):
    def __init__(self, streamer=None):
        self._streamer = streamer

    def node_iter(self):
        pass

    def __iter__(self):
        return self.node_iter()
