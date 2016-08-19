"""
Module implement the general TreeDistanceAlgorithm that is the base for working with dynamic trees
whilst calculating distances.
"""
from assess.prototypes.simpleprototypes import Tree
from assess.algorithms.signatures.signatures import Signature
from assess.algorithms.signatures.signaturecache import PrototypeSignatureCache, SignatureCache
from assess.events.events import ProcessStartEvent, ProcessExitEvent, TrafficEvent
from assess.exceptions.exceptions import EventNotSupportedException

from gnmutils.objectcache import ObjectCache
from gnmutils.exceptions import DataNotInCacheException


class TreeDistanceAlgorithm(object):
    """
    The class TreeDistanceAlgorithm creates the API for different algorithms calculating the
    distance between trees. The most important methods to consider for implementation of a new
    distance algorithm are
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
        self._event_counter = 0
        self.supported = {ProcessStartEvent: False, ProcessExitEvent: False, TrafficEvent: False}

        self._tree = Tree()
        self._signature_tree = SignatureCache()
        self._tree_dict = ObjectCache()
        self._maxlen = None

    @property
    def signature(self):
        """
        Property to access the signature that is used by TreeDistanceAlgorithm.

        :return: Current signature
        """
        return self._signature

    @property
    def tree(self):
        """
        Property to access the tree that is cached within the TreeDistanceAlgorithm.

        :return: Current tree
        """
        return self._tree

    @property
    def prototypes(self):
        """
        Property that gives access to the prototypes being used for distance calculations.

        :return: List of prototoypes
        """
        return self._prototypes[:self._maxlen]

    @prototypes.setter
    def prototypes(self, value=None):
        """
        Setter method to set the current list of prototypes to be used for distance measurements.

        :param value: List of prototypes
        """
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
        """
        Method that returns the signatures of the current prototypes being used for distance
        measurements.

        :return: Signatures for all protototypes
        """
        return self._signature_prototypes

    def cluster_representatives(self, signature_prototypes=None, prototypes=None):
        """
        Method that sets the signatures and cluster names for cluster represenatives to check.

        :param signature_prototypes: Signature for all cluster representatives
        :param prototypes: Cluster name per cluster representative
        """
        self._signature_prototypes = signature_prototypes
        self._prototypes = prototypes

    @property
    def signature_tree(self):
        """
        Method that returns the signatures of the current monitoring tree.

        :return: Signatures of monitoring tree
        """
        return self._signature_tree

    def tree_node_counts(self, signature=False):
        """
        Returns the list of count of nodes for monitoring tree per prototype. If signature is True,
        the count of nodes based on signature is used. Signature defaults to False.

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
        Returns the count of nodes per prototype tree. If signature is True, the count for converted
        prototypes based on given signature is returned. Signature defaults to False.

        :param signature: Determines if node count depends on signature, defaults to False
        :return: List of counts for prototypes
        """
        if signature:
            return [self._signature_prototypes.node_count(prototype=prototype)
                    for prototype in self._prototypes]
        try:
            return [prototype.node_count() for prototype in self._prototypes]
        except AttributeError:
            # working a Cluster Representative
            # TODO: clean this up a bit...
            pass
        return None

    def prototype_event_counts(self):
        """
        Method returns a list containing the events per prototype.

        :return: List of event counts per prototype
        """
        return self._prototype_event_counts()

    def event_counts(self):
        """
        Method returns a list containing the current events considered from the monitoring tree by
        prototype.

        :return: List of monitoring tree event counts per prototype
        """
        count = self._event_count()
        return [count for _ in range(len(self._prototypes))]

    def start_tree(self, maxlen=None, **kwargs):
        """
        Method that should be called before a new event stream is started. It takes care on
        initialising things.

        :param maxlen: How many prototypes are considered for distance measurement.
        """
        self._tree = Tree()
        self._tree_dict = ObjectCache()
        self._signature_tree = SignatureCache()
        self._event_counter = 0
        assert maxlen is None or maxlen <= len(self._prototypes)
        self._maxlen = maxlen

    def finish_tree(self):
        """
        Method that should be called after the event stream has been finished. Some of the
        algorithms might rely on this method to be called.

        :return: Returns final distance after all events have been applied.
        """
        return None

    def add_events(self, eventgenerator, **kwargs):
        """
        Convenience method that takes an event generator and calls method add_event for each event
        that is yielded.

        :param eventgenerator: Event generator yielding events.
        :param kwargs:
        :return: Returns final distances after all events have been applied.
        """
        for event in eventgenerator:
            result = self.add_event(event, **kwargs)
        return result

    def add_event(self, event, **kwargs):
        """
        Method to add an event. For each event the actual distance from the stream object to
        different prototypes are calculated. The calculated distance is returned.

        :param event: The event to be added to the current distance measurement.
        :param kwargs:
        :return: Returns the current distances after the event has been applied.
        """
        self._event_counter += 1
        if isinstance(event, ProcessStartEvent):
            if self.supported.get(ProcessStartEvent, False):
                # create node
                node, parent = self.create_node(event, **kwargs)
                signature = self.create_signature(node, parent)
                # added to keep information related signature for event
                event.signature = signature
                self._signature_tree.add_signature(signature=signature)
                return self.update_distance(event, signature, **kwargs)
        elif isinstance(event, ProcessExitEvent):
            if self.supported.get(ProcessExitEvent, False):
                # finish node
                node, parent = self.finish_node(event, **kwargs)
                signature = self.create_signature(node, parent)
                # added to keep information related signature for event
                event.signature = signature
                return self.update_distance(event, signature, **kwargs)
        elif isinstance(event, TrafficEvent):
            if self.supported.get(TrafficEvent, False) or True:
                # add traffic
                raise EventNotSupportedException(event)
        else:
            raise EventNotSupportedException(event)

    def _event_count(self):
        """
        Method returns the current event count of the monitoring tree.

        :return: Event count of monitoring tree
        """
        return self._tree.node_count()

    def _prototype_event_counts(self):
        """
        Method returns the current event count per prototype.

        :return: List of event counts per prototoype
        """
        return [prototype.node_count() for prototype in self._prototypes]

    def create_node(self, event, **kwargs):
        """
        Method to create a new node in the monitoring tree based on event data that was received.

        :param event: Event that was received
        :param kwargs: Additional parameters
        :return: Tuple of created node and its parent
        """
        try:
            parent = self._tree_dict.get_data(value=event.tme, key=event.ppid)
        except DataNotInCacheException:
            parent = None
        node = self._tree.add_node(
            event.name,
            parent=parent,
            tme=event.tme,
            pid=event.pid,
            ppid=event.ppid
        )
        self._tree_dict.add_data(data=node, key=event.pid, value=event.tme)
        return node, parent

    def finish_node(self, event, **kwargs):
        """
        Method that finishs a node based on exit event.

        :param event: Event that was received
        :param kwargs: Additional parameters
        :return: Tuple of finished node and its parent
        """
        try:
            parent = self._tree_dict.get_data(value=event.tme, key=event.ppid)
        except DataNotInCacheException:
            parent = None
        node = self._tree_dict.get_data(value=event.tme, key=event.pid)
        return node, parent

    def create_signature(self, node, parent):
        """
        Method to create the signature of a node whilst considering its parent.

        :param node: The node to create the signature for
        :param parent: The nodes parent
        :return: Calculated signature
        """
        return self._signature.get_signature(node, parent)

    def update_distance(self, event, signature, **kwargs):
        """
        Method to update the current distance based on the received event and the associated
        signature.

        :param event: Event that was received
        :param signature: Associated signature
        :param kwargs: Additional parameters
        :return: Updated distances
        """
        return self._update_distances(event, signature, **kwargs)

    def _update_distances(self, event, signature, **kwargs):
        """
        Method to be overwritten to update distances.

        :param event: Event that was received
        :param signature: Associated signature
        :param kwargs: Additional parameters
        :return: Updated distances
        """
        raise NotImplementedError

    def __repr__(self):
        return self.__class__.__name__

    def __getstate__(self):
        obj_dict = self.__dict__.copy()
        obj_dict["_prototypes"] = []
        obj_dict["_signature_prototypes"] = PrototypeSignatureCache()
        obj_dict["_tree"] = Tree()
        obj_dict["_signature_tree"] = SignatureCache()
        obj_dict["_tree_dict"] = ObjectCache()
        return obj_dict
