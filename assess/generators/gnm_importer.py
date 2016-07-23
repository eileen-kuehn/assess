"""
Generators for event streams for GNM monitoring files
"""
import random
import csv
import bisect

from gnmutils.objectcache import ObjectCache
from gnmutils.sources.filedatasource import FileDataSource
from gnmutils.exceptions import DataNotInCacheException, ObjectIsRootException

from assess.events.events import Event
from assess.prototypes.simpleprototypes import Prototype


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


class CSVEventStreamer(GNMImporter):
    """
    Generator for event stream from GNM csv files

    :param csv_path: path to a csv file
    :type csv_path: str or unicode
    """
    def __init__(self, csv_path):
        self.path = csv_path

    def __iter__(self):
        exit_event_queue = []  # (-tme, #events, event); rightmost popped FIRST
        events = 0  # used to push parent events at same tme to the left

        data_source = FileDataSource()
        for job in data_source.jobs(path=self.path):
            job.prepare_traffic()
            for process in job.processes_in_order():
                if not self._validate_process(process=process, job=job):
                    continue
                now = process.tme
                events += 1

                # yield any exit events that should have happened so far
                while exit_event_queue and exit_event_queue[-1][0] >= -now:
                    yield exit_event_queue.pop()[2]
                # create the events for the current process
                start_event, exit_event, traffic_events = Event.events_from_process(process)
                # process starts NOW, exits LATER
                yield start_event
                bisect.insort_right(exit_event_queue, (-exit_event.tme, events, exit_event))
                for traffic in traffic_events:
                    bisect.insort_right(exit_event_queue, (-(traffic.tme + 20), events, traffic))
        while exit_event_queue:
            yield exit_event_queue.pop()[2]

    def _convert_types(self, row):
        """Convert all known items of a row to their appropriate types"""
        for key, value in row.iteritems():
            try:
                row[key] = self.default_key_type[key](value)
            except ValueError:
                if not value:  # empty string -> type default
                    row[key] = self.default_key_type[key]()
                else:
                    raise
            except KeyError:
                pass
        return row

    def _validate_process(self, process, job):
        """Test if process is appropriate to pass on"""
        return True


class CSVEventStreamPruner(CSVEventStreamer):
    def __init__(self, csv_path, signature, prune_chance=0.0):
        CSVEventStreamer.__init__(self, csv_path)
        self.signature = signature
        self.prune_chance = prune_chance
        self._kept = {}  # signature => pruned: bool

    def _validate_process(self, process, job):
        try:
            parent = job.parent(process)
        except ObjectIsRootException:
            parent = None
        process_signature = self.signature.get_signature(process, parent)
        # always repeat per-signature decissions
        try:
            return self._kept[process_signature]
        # no decission yet, do it now
        except KeyError:
            self._kept[process_signature] = (random.random() > self.prune_chance)
            return self._kept[process_signature]


class CSVEventStreamBranchPruner(CSVEventStreamPruner):
    def _validate_process(self, process, job):
        try:
            parent = job.parent(process)
        except ObjectIsRootException:
            parent = None
        process_signature = self.signature.get_signature(process, parent)
        # check if *this* node has been pruned
        try:
            return self._kept[process_signature]
        except KeyError:
            # see if *parent/branch* has been pruned already
            keep_this = self._validate_process(parent, job)
            # if parent/branch is kept, this child *may* be pruned, otherwise it *must* be pruned
            self._kept[process_signature] = False if not keep_this else (random.random() > self.prune_chance)
            return self._kept[process_signature]
