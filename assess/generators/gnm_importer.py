"""
Generators for event streams for GNM monitoring files
"""
import random
import os
import logging
import filelock
try:
    import cPickle as pickle
except ImportError:
    import pickle

from gnmutils.sources.filedatasource import FileDataSource
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
        'ext_in_volume': float,
        'uid': int,
        'pid': int,
        'gpid': int,
        'ppid': int,
        'signal': int,
        'error_code': int,
        'valid': int,
    }


class PrototypeCache(object):
    """
    Cache for Prototypes built from a DataSource

    :param path: path to job data
    :param data_source: the DataSource to digest job data

    This class is meant for use in iteration or conversion to a list:

    ```python
    for prototype in PrototypeCache('foo.csv'):
        yield prototype
    ```

    The following environment variables may be set to control the cache:

    `DISS_PROTOTYPE_CACHE_REFRESH`
      Ignore all existing caches and recreate them.

    `DISS_PROTOTYPE_CACHE_PRELOADED_ONLY`
      Only use prototypes that have already been cached
    """
    def __init__(self, path, data_source=None):
        self.path = path
        self.data_source = data_source if data_source is not None else FileDataSource()
        self._logger = logging.getLogger('cache.prototypes')
        self.force_refresh = bool(os.environ.get(
            'DISS_PROTOTYPE_CACHE_REFRESH', False))
        if self.force_refresh:
            self._logger.warning(
                'Forcefully refreshing caches '
                '(enabled via $DISS_PROTOTYPE_CACHE_REFRESH)')
        self.preloaded_only = bool(os.environ.get(
            'DISS_PROTOTYPE_CACHE_PRELOADED_ONLY', False))
        if self.preloaded_only:
            self._logger.warning(
                'Only working with preloaded caches '
                '(enabled via $DISS_PROTOTYPE_CACHE_PRELOADED_ONLY)')

    def __iter__(self):
        if os.path.isdir(self.path):
            return self._prototypes_from_dir(self.path)
        elif self.path.endswith(".pkl"):
            return self._prototypes_from_pickle(self.path)
        else:
            return self._prototypes_from_csv(self.path)

    @staticmethod
    def _cache_path(real_path):
        if os.path.isdir(real_path):
            return os.path.join(real_path, 'prototypes.pkl')
        else:
            base_path, _ = os.path.splitext(real_path)
            return base_path + '_prototypes.pkl'

    def _prototypes_from_pickle(self, pkl_path):
        cache_path = self._cache_path(pkl_path)
        try:
            if self.force_refresh:
                raise OSError
            with open(cache_path, 'rb') as cache_pkl:
                prototypes = pickle.load(cache_pkl)
        except (OSError, IOError, EOFError):
            if self.preloaded_only:
                yield None
            # serialize pickle creation in case multiple processes use the
            # same prototype
            cache_prototype_lock = filelock.FileLock(
                os.path.splitext(cache_path)[0] + '.lock')
            try:
                # try to become the writer and create the pickle
                with cache_prototype_lock.acquire(timeout=0):
                    # clean up broken pickles
                    if os.path.exists(cache_path):
                        os.unlink(cache_path)
                        self._logger.warning(
                            'Refreshing existing cache %r', cache_path)
                    data_source = self.data_source
                    prototypes = None
                    with open(pkl_path, "rb") as pkl_path:
                        prototypes = [pickle.load(pkl_path)]
                    if prototypes:
                        with open(cache_path, 'wb') as cache_pkl:
                            pickle.dump(prototypes, cache_pkl, pickle.HIGHEST_PROTOCOL)
            except filelock.Timeout:
                # we are NOT the writer - acquire the lock to see when the
                # writer is done
                with cache_prototype_lock:
                    with open(cache_path, 'rb') as cache_pkl:
                        prototypes = pickle.load(cache_pkl)
        for prototype in prototypes:
            yield prototype

    def _prototypes_from_csv(self, csv_path):
        # For each individual CSV, we store *all* its content to one pkl.
        # That content may be multiple prototypes, so we yield it!
        cache_path = self._cache_path(csv_path)
        try:
            if self.force_refresh:
                raise OSError
            with open(cache_path, 'rb') as cache_pkl:
                prototypes = pickle.load(cache_pkl)
        except (OSError, IOError, EOFError):
            if self.preloaded_only:
                yield None
            # serialize pickle creation in case multiple processes use the
            # same prototype
            cache_prototype_lock = filelock.FileLock(
                os.path.splitext(cache_path)[0] + '.lock')
            try:
                # try to become the writer and create the pickle
                with cache_prototype_lock.acquire(timeout=0):
                    # clean up broken pickles
                    if os.path.exists(cache_path):
                        os.unlink(cache_path)
                        self._logger.warning(
                            'Refreshing existing cache %r', cache_path)
                    data_source = self.data_source
                    prototypes = []
                    for job in data_source.jobs(path=csv_path):
                        job.prepare_traffic()
                        prototype = Prototype.from_job(job)
                        prototypes.append(prototype)
                    if prototypes:
                        with open(cache_path, 'wb') as cache_pkl:
                            pickle.dump(prototypes, cache_pkl, pickle.HIGHEST_PROTOCOL)
            except filelock.Timeout:
                # we are NOT the writer - acquire the lock to see when the
                # writer is done
                with cache_prototype_lock:
                    with open(cache_path, 'rb') as cache_pkl:
                        prototypes = pickle.load(cache_pkl)
        for prototype in prototypes:
            yield prototype

    def _prototypes_from_dir(self, dir_path):
        # For each directory of CSVs, we store a header of files and
        # individual, per-file pkls.
        # Since the source will do the directory by itself, cached and uncached
        # structure behave differently here!
        cache_path = self._cache_path(dir_path)
        try:
            if self.force_refresh:
                raise OSError
            # get list of files
            with open(cache_path, 'rb') as cache_pkl:
                job_csv_paths = pickle.load(cache_pkl)
            # get job files individually to allow refreshing any
            for job_csv_path in job_csv_paths:
                for prototype in self._prototypes_from_csv(job_csv_path):
                    yield prototype
        except (OSError, IOError, EOFError):
            dir_prototype_lock = filelock.FileLock(
                os.path.splitext(cache_path)[0] + '.lock')
            try:
                with dir_prototype_lock.acquire(timeout=0):
                    # clean up broken pickles
                    if os.path.exists(cache_path):
                        os.unlink(cache_path)
                        self._logger.warning(
                            'Refreshing existing cache %r', cache_path)
            except filelock.Timeout:
                pass
            data_source = self.data_source
            job_files = []
            for job in data_source.jobs(path=dir_path):
                job.prepare_traffic()
                prototype = Prototype.from_job(job)
                yield prototype
                assert job.path not in job_files, \
                    "Job file may not contain multiple jobs (%r)" % job.path
                job_cache_path = self._cache_path(job.path)
                cache_prototype_lock = filelock.FileLock(os.path.splitext(
                    job_cache_path)[0] + '.lock')
                try:
                    with cache_prototype_lock.acquire(timeout=0):
                        # store the job individually, just remember its file
                        with open(job_cache_path, 'wb') as job_cache_pkl:
                            pickle.dump(
                                [prototype], job_cache_pkl, pickle.HIGHEST_PROTOCOL)
                except filelock.Timeout:
                    pass
                job_files.append(job.path)
            try:
                with dir_prototype_lock.acquire(timeout=0):
                    with open(cache_path, 'wb') as cache_pkl:
                        pickle.dump(job_files, cache_pkl, pickle.HIGHEST_PROTOCOL)
            except filelock.Timeout:
                pass


class PKLTreeBuilder(GNMImporter):
    """
    The PKLTreeBuilder builds a tree from an explicit pickle dump based on a
    log file.
    """
    @staticmethod
    def build(pkl_path):
        with open(pkl_path, "r") as job_pkl:
            return pickle.load(job_pkl)


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
        for prototype in PrototypeCache(csv_path):
            return prototype


class GNMCSVEventStreamer(NodeGenerator, EventGenerator):
    """
    Generator for event stream from GNM csv files

    :param csv_path: path to a csv file
    :type csv_path: str or unicode
    """
    def __init__(self, csv_path, **kwargs):
        streamer = kwargs.pop("streamer", None)
        supported = kwargs.pop("supported", None)
        NodeGenerator.__init__(self, streamer=streamer)
        EventGenerator.__init__(self, streamer=streamer, supported=supported)
        self.path = csv_path

    def node_iter(self):
        for job in self._jobs():
            return job.node_iter()

    def event_iter(self):
        for job in self._jobs():
            return job.event_iter(supported=self._supported)

    def _jobs(self):
        for prototype in PrototypeCache(self.path):
            yield prototype


class EventStreamer(EventGenerator):
    def event_iter(self):
        return self._streamer.event_iter()


class EventStreamPruner(EventGenerator, NodeGenerator):
    """
    Remove individual nodes from a node stream
    """
    def __init__(self, signature, chance=0.0, streamer=None, seed=None, supported=None):
        EventGenerator.__init__(self, streamer=streamer, supported=supported)
        self.signature = signature
        self.chance = chance
        self._kept = {}  # signature => kept: bool
        self._tree = None
        if seed:
            random.seed(seed)

    def event_iter(self):
        return self._get_tree().event_iter(supported=self._supported)

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
                            not self._kept[self.signature.get_signature(
                                parent, parent.parent())]:
                        parent = parent.parent()
                    if parent is not None or tree.root() is None:
                        node_dict = node.dao().copy()
                        try:
                            node_dict["ppid"] = parent.pid
                        except AttributeError:
                            pass

                        tree.add_node(
                            parent_node_id=parent.node_id
                            if parent is not None else None,
                            **node_dict)
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
            keep_this = self._kept[self.signature.get_signature(
                parent, parent.parent())]
            # if parent/branch is kept, this child *may* be pruned,
            # otherwise it *must* be pruned
            self._kept[process_signature] = False if not keep_this else \
                (random.random() > self.chance)
            return self._kept[process_signature]


class EventStreamDuplicator(EventStreamPruner):
    """
    Duplicate individual nodes from a node stream
    """
    def __init__(self, signature, chance=0.0, streamer=None, seed=None):
        super(EventStreamDuplicator, self).__init__(
            signature=signature,
            chance=chance,
            streamer=streamer,
            seed=seed
        )

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
                        tree.add_node(
                            parent_node_id=parent.node_id
                            if parent is not None else None,
                            **node_dict)
                tree.add_node(
                    parent_node_id=parent.node_id if parent is not None else None,
                    **node_dict)
            self._tree = tree
        return self._tree

    def _validate_node(self, node):
        # swap base class replacement with duplication
        return not super(EventStreamDuplicator, self)._validate_node(node)


class EventStreamRelabelerMixin(object):
    def __init__(
            self,  # type: EventStreamer | EventStreamRelabelerMixin
            signature,
            chance=0.0,
            streamer=None,
            label_generator=lambda name: name + '_relabel',
            seed=None
    ):
        super(EventStreamRelabelerMixin, self).__init__(
            signature=signature, chance=chance, streamer=streamer, seed=seed
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
