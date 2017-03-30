"""
Module implement the general TreeDistanceAlgorithm that is the base for working with dynamic trees
whilst calculating distances.
"""
from assess.prototypes.simpleprototypes import Tree
from assess.algorithms.signatures.signatures import Signature
from assess.algorithms.signatures.ensemblesignature import EnsembleSignature
from assess.events.events import ProcessStartEvent, ProcessExitEvent, TrafficEvent
from assess.exceptions.exceptions import EventNotSupportedException, TreeNotStartedException

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
    def __init__(self, signature=Signature(), cache_statistics=None):
        if not isinstance(signature, EnsembleSignature):
            self._signature = EnsembleSignature(signatures=[signature])
        else:
            self._signature = signature
        # signature caches
        self._cache_statistics = cache_statistics
        self._signature_prototypes = self._signature.prototype_signature_cache_class(
            statistics_cls=self._cache_statistics)
        self._distance = None

        self._prototypes = []
        self._tree = None
        self._tree_dict = ObjectCache()

        self._event_counter = 0
        self.supported = {ProcessStartEvent: True, ProcessExitEvent: False, TrafficEvent: False}
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
        # clean old prototypes first...
        self._signature_prototypes = self._signature.prototype_signature_cache_class(
            statistics_cls=self._cache_statistics, supported=self.supported)
        for prototype in value:
            # store links to nodes based on node_ids into dictionary
            prototype.to_prototype(
                signature=self.signature,
                start_support=self.supported[ProcessStartEvent],
                exit_support=self.supported[ProcessExitEvent],
                traffic_support=self.supported[TrafficEvent],
                cache=self._signature_prototypes
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
        # FIXME: here might be another implementation
        if isinstance(signature_prototypes, list):
            self._signature_prototypes = self._signature.prototype_signature_cache_class.\
                from_prototype_signature_caches(signature_prototypes)
        else:
            self._signature_prototypes = signature_prototypes
        self._prototypes = prototypes

    def tree_node_counts(self, signature=False):
        """
        Returns the list of count of nodes for monitoring tree per prototype. If signature is True,
        the count of nodes based on signature is used. Signature defaults to False.

        Format is like this: [ve1, ..., ven]

        :param signature: Determines if node count depends on signature, defaults to False
        :return: List of counts for monitoring tree per prototype
        """
        if signature:
            try:
                return self.distance.node_count()
            except AttributeError:
                try:
                    count = self._tree.node_count()
                except AttributeError:
                    count = 0
        else:
            try:
                count = self._tree.node_count()
            except AttributeError:
                count = 0
        return [count for _ in range(self._signature.count)] if count > 0 else []

    def prototype_node_counts(self, signature=False):
        """
        Returns the count of nodes per prototype tree. If signature is True, the count for converted
        prototypes based on given signature is returned. Signature defaults to False.

        Format is like this: [[e1p1, ... e1pn], ..., [enp1, ..., enpn]]

        :param signature: Determines if node count depends on signature, defaults to False
        :return: List of counts for prototypes
        """
        if signature:
            return [list(element) for element in zip(
                *[self._signature_prototypes.node_count(prototype=prototype) for
                  prototype in self._prototypes])]
        try:
            return [[prototype.node_count() for prototype in self._prototypes] for _ in
                    range(self._signature.count)]
        except AttributeError:
            # working a Cluster Representative
            # TODO: clean this up a bit...
            pass
        return None

    def tree_event_counts(self):
        try:
            event_counts = self.distance.node_count()
        except AttributeError:
            try:
                event_counts = self._tree.node_count()
            except AttributeError:
                event_counts = 0
        return [event_counts for _ in range(self._signature.count)] if event_counts > 0 else []

    def prototype_event_counts(self, by_event=False):
        """
        Method returns a list containing the events per prototype.

        Format is like this: [[e1p1, ..., e1pn], ..., [enp1, ..., enpn]]

        :return: List of event counts per prototype
        """
        try:
            event_counts = self.distance.node_count(prototypes=self._prototypes,
                                                    signature_prototypes=self._signature_prototypes,
                                                    by_event=by_event)
        except AttributeError:
            return self._prototype_event_counts()
        return [list(element) for element in zip(*event_counts)]

    def node_counts(self):
        return self._node_count()

    def event_counts(self, by_event=False):
        """
        Method returns a list containing the current events considered from the monitoring tree by
        prototype.

        Returned format looks like: [[e1p1, ..., e1pn], ..., [enp1, ..., enpn]]

        :return: List of monitoring tree event counts per prototype
        """
        return self._event_count(by_event=by_event)

    def start_tree(self, maxlen=None, **kwargs):
        """
        Method that should be called before a new event stream is started. It takes care on
        initialising things.

        :param maxlen: How many prototypes are considered for distance measurement.
        """
        self._tree = Tree()
        self._tree_dict = ObjectCache()
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

        Format that can be expected: [[v1p1e1, ..., vnpne1], ..., [v1p1en, ..., vnpnen]]

        Attention: This format is put into a list, because of empty nodes that might be required to
        put into the current tree.

        :param event: The event to be added to the current distance measurement.
        :param kwargs:
        :return: Returns the current distances after the event has been applied.
        """
        result = []
        # TODO: why are we actually still getting EmptyProcessEvent instances here?
        self._event_counter += 1
        if isinstance(event, ProcessStartEvent):
            if self.supported.get(ProcessStartEvent, False):
                # create node
                node, parent = self.create_node(event, **kwargs)
                signature = self.create_signature(node, parent)
                # added to keep information related signature for event
                event.signature = signature
                result.append(self.update_distance(event, signature, **kwargs))
        elif isinstance(event, ProcessExitEvent):
            # finish node to take care on empty nodes
            node, parent = self.finish_node(event, **kwargs)
            signatures = self._signature.finish_node(node)
            event.signature = []
            for signature in signatures:
                if self.supported.get(ProcessStartEvent, False):
                    start_event = ProcessStartEvent(event.tme, 0, event.pid)
                    start_event.signature = signature
                    result.append(self.update_distance(start_event, signature, **kwargs))
                    event.signature.append(signature)
                if self.supported.get(ProcessExitEvent, False):
                    exit_event = ProcessExitEvent(event.tme, 0, event.pid, event.tme)
                    exit_event.signature = signature
                    result.append(self.update_distance(exit_event, signature, **kwargs))
                    event.signature.append(signature)

            if self.supported.get(ProcessExitEvent, False):
                signature = self.create_signature(node, parent)
                # added to keep information related signature for event
                event.signature.append(signature)
                result.append(self.update_distance(event, signature, **kwargs))
        elif isinstance(event, TrafficEvent):
            if self.supported.get(TrafficEvent, False):
                # create or reuse node
                node, parent = self.create_or_reuse_node(event, **kwargs)
                signature = self.create_signature(node, parent)
                # added to keep information related signature for event
                event.signature = signature
                result.append(self.update_distance(event, signature, **kwargs))
            else:
                raise EventNotSupportedException(event)
        else:
            raise EventNotSupportedException(event)
        return result

    def _node_count(self):
        return NotImplemented

    def _event_count(self, by_event=False):
        """
        Method returns the current event count of the monitoring tree.

        :return: Event count of monitoring tree
        """
        count = self.tree_event_counts()
        return [count for _ in range(len(self._prototypes))]

    def _prototype_event_counts(self):
        """
        Method returns the current event count per prototype.

        List format is like this: [p1, ..., pn]

        :return: List of event counts per prototoype
        """
        return [[prototype.node_count() for prototype in self._prototypes] for _ in range(
            self._signature.count)]

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
        try:
            node = self._tree.add_node(
                event.name,
                parent=parent,
                tme=event.tme,
                pid=event.pid,
                ppid=event.ppid
            )
        except AttributeError:
            raise TreeNotStartedException()
        self._tree_dict.add_data(data=node, key=event.pid, value=event.tme)
        return node, parent

    def create_or_reuse_node(self, event, **kwargs):
        """
        Method to create a new node or reuse an existing node in the monitoring tree based on event
        data that was received.

        :param event: Event that was received
        :param kwargs: Additional parameters
        :return: Tuple of created node and its parent
        """
        try:
            parent = self._tree_dict.get_data(value=event.tme, key=event.ppid)
            while parent.ppid == event.pid:
                parent = parent.parent()
        except DataNotInCacheException:
            parent = None
        try:
            for child in parent.children():
                if child.name == event.name:
                    # node does already exist and does not have to be created, reuse
                    node = child
                    break
            else:
                node = self._tree.add_node(
                    event.name,
                    parent=parent,
                    tme=event.tme,
                    pid=event.pid,
                    ppid=event.ppid
                )
                # nodes don't have to be remembered to be loaded from cache, so skip this
        except AttributeError:
            raise TreeNotStartedException()
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
        except AttributeError:
            raise TreeNotStartedException()
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
        return "%s (cache_statistics=%s, supported=%s)" % \
               (self.__class__.__name__, self._cache_statistics.__name__ if self._cache_statistics
                else None, [key.__name__ for key, value in self.supported.items() if value])

    def __getstate__(self):
        obj_dict = self.__dict__.copy()
        obj_dict["_prototypes"] = []
        obj_dict["_signature_prototypes"] = type(self._signature_prototypes)()
        obj_dict["_tree"] = Tree()
        obj_dict["_tree_dict"] = type(self._tree_dict)()
        return obj_dict
