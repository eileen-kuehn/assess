from collections import Counter, deque


NODEFAULT = object()


class FrequencyCacheMap(object):
    def __init__(self, maxlen: int=None, metadata_ratio: float=1.5):
        """
        :param maxlen: Maximum length or None if unbounded
        :param metadata_ratio: Ratio of metadata to content length or None if unbounded
        """
        if metadata_ratio is not None and metadata_ratio < 1.0:
            raise ValueError("Metadata must be as large as content size or unbound")
        self._cache_map = dict()
        self._meta_map = Counter()
        self._max_len = maxlen
        if self._max_len is not None and metadata_ratio is not None:
            self._meta_len = int(self._max_len * metadata_ratio)
        else:
            self._meta_len = None
        self._lru_deque = deque(maxlen=self._meta_len)

    def score(self, key):
        """
        Returns the score of a given key. Default to 0 if key does not exist.

        :param key: key to fetch the score for
        :return: score assigned to key, else 0
        """
        return self._meta_map[key]

    def pop(self, key, default=NODEFAULT):
        """
        If key is in the dictionary, remove it and return its value,
        else return default.
        If default is not given and key is not in the dictionary,
        a :py:exc:`KeyError` is raised.

        :param key: key to remove and return the value for
        :param default: default value that is returned, when key does not exist
        :return: value for given key, if existent
        """
        try:
            value = self[key]
            del self[key]
        except KeyError:
            if default is NODEFAULT:
                raise
            value = default
        return value

    def popitem(self):
        """
        REmove and return an arbitrary `(key, value)` from the dictionary.
        This method is useful to destructively iterate over the CacheMap.
        If CacheMap is empty, `popitem` raises a :py:exc:`KeyError`.

        :return: arbitrary (key, value) pair
        """
        try:
            key, value = next(self.iteritems())
            del self[key]
            return key, value
        except KeyError:
            raise

    def clear(self):
        """
        Remove all items (inclusive scores) from CacheMap
        """
        self._cache_map.clear()
        self._meta_map.clear()
        self._lru_deque.clear()

    def update(self, other):
        """
        Update the existing CacheMap with other CacheMap, or dict, overwriting
        existing keys, values, and scores and adding additional ones.

        :param other: CacheMap or dict used for update
        """
        try:
            for key, value, score in other.iterscoreditems():
                self._update_item(key, value, score)
        except AttributeError:
            for key, value in other.iteritems():
                self[key] = value

    def setdefault(self, key, default=None):
        """
        If *key* is in the CacheMap, return its value. If not, insert *key* with value
        of default and return default. If default is not given, it defaults to None.

        :param key: key to fetch the value for, else default is inserted and returned
        :param default: default value if key does not exist, else None
        :return: value for key, else default
        """
        try:
            return self[key]
        except KeyError:
            self[key] = default
            return default

    def keys(self):
        """
        Returns a copy of the CacheMap's list of keys

        :return: list of keys
        """
        return list(iter(self))

    def items(self):
        """
        Returns a copy of the CacheMap's list of items

        :return: list of items
        """
        return list(self.iteritems())

    def values(self):
        """
        Returns a copy of the CacheMap's list of values

        :return: list of values
        """
        return list(self.itervalues())

    def get(self, key, default=None):
        """
        Return the value for a given key if it exists, else default.
        If default is not given, it defaults to `None`.

        :param key: key to fetch the value for
        :param default: default to return if key does not exist, else `None`
        :return: value assigned to key, else default
        """
        try:
            return self[key]
        except KeyError:
            return default

    def iter(self):
        """
        Returns an iterator for the keys of CacheMap.

        :return: iterator over keys
        """
        return self.iterkeys()

    def iterkeys(self):
        """
        Returns an iterator over the keys of CacheMap.

        :return: iterator over keys
        """
        return iter(self)

    def iteritems(self):
        """
        Returns an iterator over the items given as (key, value) pair.

        :return: iterator over items
        """
        try:
            for item_key in self:
                yield (item_key, self[item_key])
        except KeyError:
            raise RuntimeError("dictionary changed during iteration")

    def iterscoreditems(self):
        """
        Returns an iterator over the scored items given as (key, value, score) tuple.

        :return: iterator over scored items
        """
        try:
            for item_key in self:
                yield (item_key, self[item_key], self.score(item_key))
        except KeyError:
            raise RuntimeError("dictionary changed during iteration")

    def itervalues(self):
        """
        Returns an iterator over values.

        :return: iterator over values
        """
        try:
            for item_key in self:
                yield self[item_key]
        except KeyError:
            raise RuntimeError("dictionary changed during iteration")

    def __contains__(self, key):
        """
        Check if key is contained in keys of CacheMap.

        :see: collections.Container
        :param key: key to check for existence
        :return: True if existent, else False
        """
        return key in self._cache_map

    def __getitem__(self, key):
        """
        Get value for a given key. Raises :py:exc:`KeyError` if key does not exist

        :see: collections.Mapping
        :param key: key to fetch value for
        :return: value for key
        """
        return self._cache_map[key]

    def __setitem__(self, key, value):
        """
        Set a given value for key. If key does already exist, value is overwritten
        and the frequency score is adapted.

        :see: collections.MutableMapping
        :param key: key to use for given value
        :param value: value to set for given key
        """
        self._prepare_metadata(key=key)
        self._add_to_cache(key=key, value=value)

    def __delitem__(self, key):
        """
        Delete a given key from CacheMap.

        :see: collections.MutableMapping
        :param key: key to delete from CacheMap

        :note: Everything for key is deleted, including its score and statistics.
        """
        del self._cache_map[key]
        del self._meta_map[key]
        self._lru_deque.remove(key)

    def __iter__(self):
        """
        :see: collections.Iterable
        :return: iterator over keys of CacheMap
        """
        return iter(self._cache_map)

    def __len__(self):
        """
        Returns length of CacheMap.

        :see: collections.Sized
        :return: length of CacheMap
        """
        return len(self._cache_map)

    def __eq__(self, other):
        """
        Comparison if other CacheMap or dict is equal to CacheMap.

        :see: collections.Mapping
        :param other: CacheMap or dict to test equivalence
        :return: True if equal, else False
        """
        try:
            return self._cache_map == other._cache_map and \
                   self._meta_map == other._meta_map and \
                   self._lru_deque == other._lru_deque
        except AttributeError:
            return self._cache_map == other

    def __ne__(self, other):
        """
        Comparison if other CacheMap or dict is unequal to CacheMap.

        :see: collections.Mapping
        :param other: CacheMap or dict to test inequality
        :return: True if unequal, else False
        """
        return not self == other

    def _prepare_metadata(self, key=None, regulate_score: bool = True):
        if key in self._lru_deque:
            self._lru_deque.remove(key)
        else:
            if self._meta_len is not None and len(self._lru_deque) >= self._meta_len:
                removable_key = self._lru_deque.pop()
                if regulate_score:
                    value = self._meta_map[removable_key]
                    for a_key in self._meta_map:
                        # TODO: keep the -1 here or not?
                        self._meta_map[a_key] -= value - 1
                try:
                    del self._meta_map[removable_key]
                    del self._cache_map[removable_key]
                except KeyError:
                    pass
        self._lru_deque.appendleft(key)

    def _update_item(self, key=None, value=None, score=None):
        self._prepare_metadata(key=key, regulate_score=False)
        self._add_to_cache(key=key, value=value)
        self._meta_map[key] = score

    def _add_to_cache(self, key=None, value=None):
        if self._max_len is None or len(self._cache_map) < self._max_len or key in self.keys():
            self._cache_map[key] = value
        else:
            current_score = (self._meta_map[key] + 1) * len(self._lru_deque)
            replaceable_item = None
            for index, item in enumerate(reversed(self._lru_deque)):
                possible_score = (index + 1) * self._meta_map[item]
                if item in self._cache_map and possible_score < current_score:
                    replaceable_item = item
                    current_score = possible_score
            if replaceable_item is not None:
                del self._cache_map[replaceable_item]
                self._cache_map[key] = value
        self._meta_map[key] += 1
