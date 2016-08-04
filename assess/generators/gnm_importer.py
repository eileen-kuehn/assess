"""
Generators for event streams for GNM monitoring files
"""
import random
import csv

from gnmutils.objectcache import ObjectCache
from gnmutils.sources.filedatasource import FileDataSource
from gnmutils.exceptions import DataNotInCacheException

from assess.prototypes.simpleprototypes import Prototype
from assess.generators.event_generator import EventGenerator, NodeGenerator


class GNMImporter(object):
    """
    The GNMImporter defines the default key types for GNM application.
    """
    default_key_type = {
        'tme': float,
        'exit_tme': float,
        'tree_depth': int,
        'int_out_volume': float,
        'int_in_volume': float,
        'ext_out_volume': float,
        'ext_in_volume' : float,
        'uid': int,
        'pid': int,
        'gpid': int,
        'ppid': int,
        'signal': int,
        'error_code': int,
        'valid': int,
    }


class CSVTreeBuilder(GNMImporter):
    """
    The CSVTreeBuilder builds a monitoring tree from actual GNM log files.
    """
    @staticmethod
    def build(csv_path):
        """
        Method build the actual prototype tree from a log file.

        :param csv_path: Path to GNM log file
        :return: Prototype tree
        """
        process_cache = ObjectCache()
        result = Prototype()

        with open(csv_path) as csv_file:
            for process in csv.DictReader(row for row in csv_file if not row.startswith('#')):
                try:
                    parent = process_cache.get_data(
                        value=process.get("tme", 0),
                        key=process.get("ppid", 0),
                        validate_range=True
                    )
                except DataNotInCacheException:
                    if result.root() is not None and \
                            (int(process.get("tme")) < int(result.root().tme) or
                                int(process.get("exit_tme")) > int(result.root().exit_tme)):
                    #if int(process.get("uid", 0)) == 0 and result.root() is not None:
                        continue
                    parent = None
                node = result.add_node(
                    process.get("name", "."),
                    parent=parent,
                    tme=process.get("tme", 0),
                    exit_tme=process.get("exit_tme", 0),
                    pid=process.get("pid", 0),
                    ppid=process.get("ppid", 0)
                )
                process_cache.add_data(
                    data=node,
                    key=process.get("pid", 0),
                    value=process.get("tme", 0)
                )
        return result


class GNMCSVEventStreamer(NodeGenerator, EventGenerator):
    """
    Generator for event stream from GNM csv files

    :param csv_path: path to a csv file
    :type csv_path: str or unicode
    """
    def __init__(self, csv_path, streamer=None):
        NodeGenerator.__init__(self, streamer=streamer)
        self.path = csv_path

    def node_iter(self):
        for job in self._jobs():
            return job.node_iter()

    def event_iter(self):
        for job in self._jobs():
            return job.event_iter()

    def _jobs(self):
        data_source = FileDataSource()
        for job in data_source.jobs(path=self.path):
            job.prepare_traffic()
            prototype = Prototype.from_job(job)
            yield prototype


class EventStreamer(EventGenerator):
    def event_iter(self):
        return self._streamer.event_iter()


class EventStreamPruner(EventGenerator, NodeGenerator):
    """
    Remove individual nodes from a node stream
    """
    def __init__(self, signature, chance=0.0, streamer=None):
        EventGenerator.__init__(self, streamer=streamer)
        self.signature = signature
        self.chance = chance
        self._kept = {}  # signature => kept: bool
        self._tree = None

    def event_iter(self):
        return self._get_tree().event_iter()

    def node_iter(self):
        return self._get_tree().node_iter()

    def _get_tree(self):
        if self._tree is None:
            tree = Prototype()
            for node in self._streamer.node_iter():
                keep_node = self._validate_node(node)
                if keep_node:
                    parent = node.parent()
                    while parent is not None and \
                            not self._kept[self.signature.get_signature(parent, parent.parent())]:
                        parent = parent.parent()
                    if parent is not None or tree.root() is None:
                        node_dict = node.dao().copy()
                        try:
                            node_dict["ppid"] = parent.pid
                        except AttributeError:
                            pass
                        tree.add_node(parent=parent, **node_dict)
            self._tree = tree
        return self._tree

    def _validate_node(self, node):
        """
        Hook for checking and modifying a node

        This hook serves two functions:

        - It may *veto* a node by returning `False`.
        - It may *modify* a node inplace.

        :param node:
        :return: whether the node gets passed on
        """
        parent = node.parent()
        process_signature = self.signature.get_signature(node, parent)
        if parent is None:
            # never prune root node to avoid bias
            return self._kept.setdefault(process_signature, True)
        # always repeat per-signature decisions
        try:
            return self._kept[process_signature]
        # no decision yet, do it now
        except KeyError:
            self._kept[process_signature] = (random.random() > self.chance)
            return self._kept[process_signature]

    def __repr__(self):
        return "%s (prune_chance=%s, pruned=%s, tested=%s)" % (
            self.__class__.__name__,
            self.chance,
            len(self._kept) - sum(self._kept.values()),
            len(self._kept)
        )


class EventStreamBranchPruner(EventStreamPruner):
    """
    Remove individual branches from a stream
    """
    def _validate_node(self, node):
        parent = node.parent()
        process_signature = self.signature.get_signature(node, parent)
        if parent is None:
            # never prune root node to avoid bias
            return self._kept.setdefault(process_signature, True)
        # check if *this* node has been pruned
        try:
            return self._kept[process_signature]
        except KeyError:
            # see if *parent/branch* has been pruned already
            keep_this = self._kept[self.signature.get_signature(parent, parent.parent())]
            # if parent/branch is kept, this child *may* be pruned, otherwise it *must* be pruned
            self._kept[process_signature] = False if not keep_this else \
                (random.random() > self.chance)
            return self._kept[process_signature]


class EventStreamDuplicator(EventStreamPruner):
    """
    Duplicate individual nodes from a node stream
    """
    def __init__(self, signature, chance=0.0, streamer=None):
        super(EventStreamDuplicator, self).__init__(signature=signature, chance=chance,
                                                    streamer=streamer)

    def _get_tree(self):
        if self._tree is None:
            tree = Prototype()
            for node in self._streamer.node_iter():
                node_dict = node.dao().copy()
                parent = node.parent()
                duplicate_node = self._validate_node(node)
                if duplicate_node:
                    if parent is not None:
                        duplicate_dict = node_dict.copy()
                        duplicate_dict["exit_tme"] = duplicate_dict["tme"]
                        tree.add_node(parent=parent, **node_dict)
                tree.add_node(parent=parent, **node_dict)
            self._tree = tree
        return self._tree

    def _validate_node(self, node):
        # swap base class replacement with duplication
        return not super(EventStreamDuplicator, self)._validate_node(node)


class EventStreamRelabelerMixin(object):
    def __init__(
            self,  # type: EventStreamer | EventStreamRelabelerMixin
            signature, chance=0.0, streamer=None, label_generator=lambda name: name + '_relabel'):
        super(EventStreamRelabelerMixin, self).__init__(
            signature=signature, chance=chance, streamer=streamer
        )
        self.label_generator = label_generator

    def _validate_node(
            self,  # type: EventStreamer | EventStreamRelabelerMixin
            node):
        # swap base class replacement with renaming
        if not super(EventStreamRelabelerMixin, self)._validate_node(node):
            node.name = self.label_generator(node.name)
        return True  # accept all nodes


class EventStreamRelabeler(EventStreamRelabelerMixin, EventStreamPruner):
    """
    Relabel individual nodes from a stream
    """
    pass


class EventStreamBranchRelabeler(EventStreamRelabelerMixin, EventStreamBranchPruner):
    """
    Relabel individual nodes and their children from a stream
    """
    pass
