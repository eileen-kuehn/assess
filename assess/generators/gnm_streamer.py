"""
Generators for event streams for GNM monitoring files
"""
import csv
import heapq
import collections
import bisect

from assess.events.events import ProcessStartEvent, ProcessExitEvent


class CSVStreamer(object):
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

	def __init__(self, csv_path):
		self.path = csv_path

	def __iter__(self):
		exit_events_heap = []  # (event.tme, event); heapq will do some magic on this
		with open(self.path) as csv_file:
			for process in csv.DictReader(csv_file):
				now = float(process['tme'])
				# yield any exit events that should have happened so far
				while exit_events_heap and exit_events_heap[0][0] < now:
					yield heapq.heappop(exit_events_heap)[1]
				# create the events for the current process
				process = self._convert_types(process)
				start_event = ProcessStartEvent(**process)
				process['tme'], process['start_tme'] = process['exit_tme'], process['tme']
				exit_event = ProcessExitEvent(**process)
				# process starts NOW, exists LATER
				yield start_event
				heapq.heappush(exit_events_heap, (exit_event.tme, exit_event))
		while exit_events_heap:
			yield heapq.heappop(exit_events_heap)[1]

	def iter(self):
		exit_event_queue = []  # rightmost elements popped EARLIER
		events = 0  # used to push parent events at same tme to the left
		with open(self.path) as csv_file:
			for process in csv.DictReader(csv_file):
				now = float(process['tme'])
				events += 1
				# yield any exit events that should have happened so far
				while exit_event_queue and exit_event_queue[-1][0] > -now:
					yield exit_event_queue.pop()[2]
				# create the events for the current process
				process = self._convert_types(process)
				start_event = ProcessStartEvent(**process)
				process['tme'], process['start_tme'] = process['exit_tme'], process['tme']
				exit_event = ProcessExitEvent(**process)
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

