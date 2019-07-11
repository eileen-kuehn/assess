import unittest

from assess.utility.frequencycachemap import FrequencyCacheMap


class TestFrequencyCacheMap(unittest.TestCase):
    def test_instantiation(self):
        cache_map = FrequencyCacheMap()
        self.assertIsNotNone(cache_map)
        self.assertIsNotNone(FrequencyCacheMap(None, None))
        self.assertIsNotNone(FrequencyCacheMap(None, 1.5))
        self.assertIsNotNone(FrequencyCacheMap(1.5, None))
        with self.assertRaises(ValueError):
            FrequencyCacheMap(1.5, 0.9)
        with self.assertRaises(ValueError):
            FrequencyCacheMap(None, 0.9)

    def test_adding_elements(self):
        cache_map = FrequencyCacheMap()
        cache_map["key"] = "value"
        self.assertEqual(cache_map.get("key", None), "value")
        self.assertEqual(cache_map["key"], "value")

    def test_deleting_elements(self):
        cache_map = FrequencyCacheMap()
        cache_map["key"] = "value"
        cache_map["key2"] = "value"
        self.assertTrue("key" in cache_map)
        del cache_map["key"]
        self.assertFalse("key" in cache_map)
        self.assertEqual(cache_map.score("key"), 0)

    def test_clearing(self):
        cache_map = FrequencyCacheMap(maxlen=3, metadata_ratio=1.0)
        cache_map["key"] = "value"
        cache_map["key"] = "value"
        cache_map["key2"] = "value"
        cache_map["key3"] = "value"
        cache_map["key4"] = "value"
        cache_map.clear()
        self.assertRaises(KeyError, cache_map.__getitem__, "key")
        self.assertEqual(cache_map.score("key"), 0)
        self.assertEqual(len(cache_map), 0)
        self.assertEqual(len(cache_map._lru_deque), 0)
        self.assertEqual(len(cache_map._meta_map), 0)

    def test_nonexisting_keys(self):
        cache_map = FrequencyCacheMap()
        self.assertIsNone(cache_map.get("key", None))
        self.assertRaises(KeyError, cache_map.__getitem__, "key")
        self.assertIsNone(cache_map.get("key"))
        self.assertIsNotNone(cache_map.get("key", 1))

    def test_score(self):
        cache_map = FrequencyCacheMap()
        self.assertEqual(cache_map.score("key"), 0)
        cache_map["key"] = "value"
        self.assertEqual(cache_map.score("key"), 1)
        self.assertEqual(cache_map["key"], "value")
        cache_map["key"] = "value"
        cache_map["key"] = "value2"
        self.assertEqual(cache_map.score("key"), 3)
        self.assertEqual(cache_map["key"], "value2")

    def test_len(self):
        cache_map = FrequencyCacheMap()
        self.assertEqual(len(cache_map), 0)
        cache_map["key"] = "value"
        cache_map["key"] = "value"
        self.assertEqual(len(cache_map), 1)
        cache_map[1] = "value"
        self.assertEqual(len(cache_map), 2)

    def test_max_len(self):
        cache_map = FrequencyCacheMap(maxlen=3)
        cache_map["key"] = "value"
        cache_map["key"] = "value"
        cache_map["key"] = "value"
        self.assertEqual(len(cache_map), 1)
        cache_map["key2"] = "value"
        self.assertEqual(len(cache_map), 2)
        cache_map["key3"] = "value"
        self.assertEqual(len(cache_map), 3)
        cache_map["key4"] = "value"
        self.assertEqual(len(cache_map), 3)
        cache_map["key4"] = "value"
        self.assertEqual(len(cache_map), 3)
        cache_map["key2"] = "value"
        self.assertEqual(len(cache_map), 3)

    def test_lru_deque_same_length(self):
        cache_map = FrequencyCacheMap(maxlen=3, metadata_ratio=1)
        cache_map["key"] = "value"
        cache_map["key"] = "value"
        self.assertEqual(cache_map.score("key"), 2)
        self.assertTrue("key" in cache_map)
        cache_map["key2"] = "value"
        cache_map["key3"] = "value"
        self.assertTrue("key2" in cache_map)
        self.assertTrue("key3" in cache_map)
        cache_map["key4"] = "value"
        self.assertTrue("key4" in cache_map)
        self.assertFalse("key" in cache_map)
        self.assertEqual(cache_map.score("key"), 0)
        cache_map["key"] = "value"
        self.assertTrue("key" in cache_map)
        self.assertEqual(cache_map.score("key"), 1)

    def test_lru_deque_default_length(self):
        # default metadata ratio
        cache_map = FrequencyCacheMap(maxlen=3)
        cache_map["key"] = "value"
        self.assertEqual(cache_map.score("key"), 1)
        cache_map["key2"] = "value"
        cache_map["key2"] = "value"
        self.assertEqual(cache_map.score("key2"), 2)
        cache_map["key3"] = "value"
        cache_map["key3"] = "value"
        self.assertEqual(cache_map.score("key3"), 2)
        cache_map["key4"] = "value"
        self.assertEqual(cache_map.score("key4"), 1)
        self.assertTrue("key4" in cache_map.keys())
        cache_map["key4"] = "value"
        self.assertEqual(cache_map.score("key4"), 2)
        cache_map["key5"] = "value"
        self.assertEqual(cache_map.score("key5"), 1)
        self.assertTrue("key5" in cache_map.keys())
        cache_map["key5"] = "value"
        self.assertTrue("key5" in cache_map.keys())
        cache_map["key"] = "value"
        self.assertEqual(cache_map.score("key"), 1)
        self.assertTrue("key" in cache_map)

    def test_pop(self):
        cache_map = FrequencyCacheMap(maxlen=3)
        cache_map["key"] = "value"
        cache_map["key2"] = "value"
        self.assertEqual(cache_map.pop("key3", "default"), "default")
        self.assertRaises(KeyError, cache_map.pop, "key3")
        self.assertEqual(cache_map.score("key"), 1)
        self.assertEqual(cache_map.pop("key"), "value")
        self.assertEqual(cache_map.score("key"), 0)
        self.assertEqual(cache_map.pop("key2", "default"), "value")
        self.assertEqual(len(cache_map), 0)

        saved_values = {
            "key": "value",
            "key2": "value2"
        }
        cache_map["key"] = "value"
        cache_map["key2"] = "value2"
        for i in range(len(saved_values)):
            key, value = cache_map.popitem()
            self.assertEqual(saved_values[key], value)
            del saved_values[key]
        self.assertEqual(len(cache_map), 0)
        self.assertEqual(len(saved_values), 0)

    def test_iteration(self):
        cache_map = FrequencyCacheMap()
        cache_map["key"] = "value"
        cache_map["key2"] = "value"

        count = 0
        for key in cache_map:
            count += 1
            self.assertTrue("key" in key)
        self.assertEqual(count, len(cache_map))

    def test_update(self):
        cache_map = FrequencyCacheMap(maxlen=3)
        cache_map["key"] = "value"
        cache_map["key"] = "value"
        cache_map["key2"] = "value"

        second_map = FrequencyCacheMap(maxlen=3)
        second_map["key3"] = "value"
        cache_map.update(second_map)
        self.assertTrue("key3" in cache_map)
        self.assertEqual(cache_map.score("key3"), 1)
        self.assertEqual(cache_map.score("key"), 2)
        self.assertEqual(cache_map.score("key2"), 1)

        cache_map.update(second_map)
        self.assertTrue("key3" in cache_map)
        self.assertEqual(cache_map.score("key3"), 1)
        self.assertEqual(cache_map.score("key"), 2)
        self.assertEqual(cache_map.score("key2"), 1)

        third_map = FrequencyCacheMap(maxlen=3)
        third_map["key"] = "value2"

        cache_map.update(third_map)
        self.assertEqual(cache_map.score("key"), 1)
        self.assertEqual(cache_map["key"], "value2")

        fourth_map = FrequencyCacheMap(maxlen=3)
        fourth_map["key4"] = "value"

        cache_map.update(fourth_map)
        self.assertTrue("key4" in cache_map)
        self.assertFalse("key2" in cache_map)
