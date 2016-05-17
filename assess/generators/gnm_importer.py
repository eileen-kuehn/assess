"""
Generators for event streams for GNM monitoring files
"""
import csv
import bisect

from gnmutils.objectcache import ObjectCache

from assess.events.events import Event, ProcessStartEvent, ProcessExitEvent
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
        process_cache = ObjectCache()
        result = Prototype()

        with open(csv_path) as csv_file:
            for process in csv.DictReader(row for row in csv_file if not row.startswith('#')):
                parent = process_cache.getObject(
                    tme=process.get("tme", 0),
                    pid=process.get("ppid", 0)
                )
                node = result.add_node(
                    process.get("name", "."),
                    parent=parent,
                    tme=process.get("tme", 0),
                    exit_tme=process.get("exit_tme", 0),
                    pid=process.get("pid", 0),
                    ppid=process.get("ppid", 0)
                )
                process_cache.addObject(
                    object=node,
                    pid=process.get("pid", 0),
                    tme=process.get("tme", 0)
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
        with open(self.path) as csv_file:
            for process in csv.DictReader(row for row in csv_file if not row.startswith('#')):
                now = float(process['tme'])
                events += 1
                # yield any exit events that should have happened so far
                while exit_event_queue and exit_event_queue[-1][0] > -now:
                    yield exit_event_queue.pop()[2]
                # create the events for the current process
                process = self._convert_types(process)
                start_event = Event.start(**process)
                #start_event = ProcessStartEvent(**process)
                process['tme'], process['start_tme'] = process['exit_tme'], process['tme']
                exit_event = Event.exit(**process)
                #exit_event = ProcessExitEvent(**process)
                # process starts NOW, exists LATER
                yield start_event
                bisect.insort_right(exit_event_queue, (-exit_event.tme, events, exit_event))
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
