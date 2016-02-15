from assess.prototypes.simpleprototypes import Tree
from assess.algorithms.signatures.signatures import Signature


class TreeDistanceAlgorithm(object):
    def __init__(self, signature=Signature()):
        self._signature = signature
        self._prototypes = []
        self._tree = Tree()

    @property
    def prototypes(self):
        return self._prototypes

    @prototypes.setter
    def prototypes(self, value=None):
        self._prototypes = value

    def prototypes_converted_for_algorithm(self):
        return self._prototypes

    def add_event(self, event, **kwargs):
        return self._add_event(event, **kwargs)

    def _add_event(self, event, **kwargs):
        raise NotImplementedError
