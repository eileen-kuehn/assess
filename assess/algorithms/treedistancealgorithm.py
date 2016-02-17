from assess.prototypes.simpleprototypes import Tree
from assess.algorithms.signatures.signatures import Signature

from gnmutils.objectcache import ObjectCache


class TreeDistanceAlgorithm(object):
    def __init__(self, signature=Signature()):
        self._signature = signature
        self._prototypes = []

        self._tree = Tree()
        self._tree_dict = ObjectCache()

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

    def _create_node(self, event, **kwargs):
        parent = self._tree_dict.getObject(tme=event.tme, pid=event.ppid)
        node = self._tree.add_node(
            event.name,
            parent=parent,
            tme=event.tme,
            pid=event.pid,
            ppid=event.ppid
        )
        self._signature.prepare_signature(node)
        self._tree_dict.addObject(node, pid=event.pid, tme=event.tme)
        return node

    def _update_distances(self, **kwargs):
        raise NotImplementedError

    def __repr__(self):
        return self.__class__.__name__
