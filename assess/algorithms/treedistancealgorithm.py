from assess.prototypes.simpleprototypes import Tree


class TreeDistanceAlgorithm(object):
    def __init__(self):
        self._prototypes = []
        self._tree = Tree()

    @property
    def prototypes(self):
        return self._prototypes

    @prototypes.setter
    def prototypes(self, value=None):
        self._prototypes = value

    def add_event(self, event, **kwargs):
        return self._add_event(event, **kwargs)

    def _add_event(self, event, **kwargs):
        raise NotImplementedError
