class Decorator(object):
    def __init__(self):
        self._algorithm = None
        self.decorator = None

    @property
    def algorithm(self):
        return self.algorithm

    @algorithm.setter
    def algorithm(self, value):
        if self.decorator is not None:
            self.decorator.algorithm = value
        self._algorithm = value

    def add_event(self, event, **kwargs):
        self._algorithm.add_event(event, **kwargs)
