from assess.prototypes.simpleprototypes import Tree
from assess.algorithms.signatures.signatures import Signature
from assess.algorithms.signatures.signaturecache import PrototypeSignatureCache, SignatureCache

from gnmutils.objectcache import ObjectCache


class TreeDistanceAlgorithm(object):
    """
    The class TreeDistanceAlgorithm creates the API for different algorithms calculating the distance between trees.
    The most important methods to consider for implementation of a new distance algorithm are
    * node_count_for_prototype,
    * prototypes_converted_for_algorithm,
    * start_tree and finish_tree,
    * _add_event, and
    * _update_distance
    """
    def __init__(self, signature=Signature()):
        self._signature = signature
        self._prototypes = []
        self._signature_prototypes = PrototypeSignatureCache()

        self._tree = Tree()
        self._signature_tree = SignatureCache()
        self._tree_dict = ObjectCache()
        self._maxlen = None

    @property
    def tree(self):
        return self._tree

    @property
    def prototypes(self):
        return self._prototypes[:self._maxlen]

    @prototypes.setter
    def prototypes(self, value=None):
        for prototype in value:
            # store links to nodes based on node_ids into dictionary
            for process in prototype.nodes():
                signature = self._signature.get_signature(process, process.parent())
                self._signature_prototypes.add_signature(
                    signature=signature,
                    prototype=prototype,
                    value=(float(process.exit_tme)-float(process.tme))
                )
        self._prototypes = value

    @property
    def signature_prototypes(self):
        return self._signature_prototypes

    @property
    def signature_tree(self):
        return self._signature_tree

    def tree_node_counts(self, signature=False):
        """
        Returns the list of count of nodes for monitoring tree per prototype. If signature is True, the count of
        nodes based on signature is used. Signature defaults to False.
        :param signature: Determines if node count depends on signature, defaults to False
        :return: List of counts for monitoring tree per prototype
        """
        if signature:
            count = self._signature_tree.node_count()
        else:
            count = self._tree.node_count()
        return [count for _ in range(len(self._prototypes))]

    def prototype_node_counts(self, signature=False):
        """
        Returns the count of nodes per prototype tree. If signature is True, the count for converted prototypes
        based on given signature is returned. Signature defaults to False.

        :param signature: Determines if node count depends on signature, defaults to False
        :return: List of counts for prototypes
        """
        if signature:
            return [self._signature_prototypes.node_count(prototype=prototype) for prototype in self._prototypes]
        return [prototype.node_count() for prototype in self._prototypes]

    def prototype_event_counts(self):
        return self._prototype_event_counts()

    def event_counts(self):
        count = self._event_count()
        return [count for _ in range(len(self._prototypes))]

    def start_tree(self, maxlen=None, **kwargs):
        """
        Method that should be called before a new event stream is started. It takes care on initialising things.

        :param maxlen: How many prototypes are considered for distance measurement.
        """
        self._tree = Tree()
        self._tree_dict = ObjectCache()
        self._signature_tree = SignatureCache()
        # TODO: write warning if maxlen is bigger then count of prototypes
        self._maxlen = maxlen

    def finish_tree(self):
        """
        Method that should be called after the event stream has been finished. Some of the algorithms might rely on
        this method to be called.
        :return: Returns final distance after all events have been applied.
        """
        return None

    def add_events(self, eventgenerator, **kwargs):
        """
        Convenience method that takes an event generator and calls method add_event for each event that is yielded.
        :param eventgenerator: Event generator yielding events.
        :param kwargs:
        :return: Returns final distances after all events have been applied.
        """
        for event in eventgenerator:
            result = self.add_event(event, **kwargs)
        return result

    def add_event(self, event, **kwargs):
        """
        Method to add an event. For each event the actual distance from the stream object to different prototypes
        are calculated. The calculated distance is returned.
        :param event: The event to be added to the current distance measurement.
        :param kwargs:
        :return: Returns the current distances after the event has been applied.
        """
        return self._add_event(event, **kwargs)

    def _event_count(self):
        raise NotImplementedError

    def _prototype_event_counts(self):
        raise NotImplementedError

    def _add_event(self, event, **kwargs):
        raise NotImplementedError

    def _create_node(self, event, **kwargs):
        parent = self._tree_dict.getObject(tme=event.tme, pid=event.ppid)
        # TODO: I might directly add this to node, but therefore I need to ensure to use pid, ppid
        node = self._tree.add_node(
            event.name,
            parent=parent,
            tme=event.tme,
            pid=event.pid,
            ppid=event.ppid
        )
        signature = self._signature.get_signature(node, parent)
        self._tree_dict.addObject(node, pid=event.pid, tme=event.tme)
        self._signature_tree.add_signature(signature=signature)
        return signature

    def _finish_node(self, event, **kwargs):
        parent = self._tree_dict.getObject(tme=event.tme, pid=event.ppid)
        node = self._tree_dict.getObject(tme=event.tme, pid=event.pid)
        signature = self._signature.get_signature(node, parent)
        return signature

    def _update_distances(self, **kwargs):
        raise NotImplementedError

    def __repr__(self):
        return self.__class__.__name__
