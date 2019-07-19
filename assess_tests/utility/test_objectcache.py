import unittest

from assess.utility.objectcache import ObjectCache
from assess.exceptions.exceptions import DataNotInCacheException


class Process(object):
    def __init__(self, tme=None, pid=None, name=None):
        self.tme = tme
        self.pid = pid
        self.name = name


class TestObjectCacheFunctions(unittest.TestCase):
    def setUp(self):
        self.objectCache = ObjectCache()

    def test_setUp(self):
        self.assertEqual(len(self.objectCache.object_cache), 0, "object cache not empty")
        self.assertEqual(len(self.objectCache.faulty_nodes), 0, "object cache not empty")
        self.assertEqual(len(self.objectCache.unfound), 0, "object cache not empty")

    def test_insertRemove(self):
        process = Process(tme=1, pid=2)
        process2 = Process(tme=2, pid=2)
        process3 = Process(tme=0, pid=2)
        process4 = Process(tme=0, pid=3)

        self.assertEqual(len(self.objectCache.object_cache), 0, "object cache not empty")
        self.objectCache.add_data(data=process)
        self.assertEqual(len(self.objectCache.object_cache), 1,
                         "object cache should contain one process")

        loadedProcess = self.objectCache.get_data(value=process.tme, key=process.pid)
        self.assertIsNotNone(loadedProcess, "No object loaded from cache")
        self.assertEqual(process, loadedProcess, "objects should be identical")
        self.objectCache.remove_data(data=process)
        self.assertEqual(len(self.objectCache.object_cache), 0, "object cache not empty")

        self.objectCache.add_data(data=process)
        self.objectCache.add_data(data=process2)
        self.objectCache.add_data(data=process3)
        self.objectCache.add_data(data=process4)
        self.assertEqual(len(self.objectCache.object_cache), 2,
                         "object cache should contain two different categories")
        loadedProcess = self.objectCache.get_data(value=process2.tme, key=process2.pid)
        self.assertEqual(process2, loadedProcess, "objects should be identical")
        loadedProcess = self.objectCache.get_data(value=process3.tme, key=process3.pid)
        self.assertEqual(process3, loadedProcess, "objects should be identical")
        loadedProcess = self.objectCache.get_data(value=process.tme, key=process.pid)
        self.assertEqual(process, loadedProcess, "objects should be identical")
        loadedProcess = self.objectCache.get_data(value=process4.tme, key=process4.pid)
        self.assertEqual(process4, loadedProcess, "objects should be identical")

    def test_removeObject(self):
        process = Process(tme=1, pid=2)

        self.objectCache.add_data(data=process)

        self.assertEqual(len(self.objectCache.object_cache), 1,
                         "object cache should not be empty")
        self.objectCache.remove_data(data=process)
        self.assertEqual(len(self.objectCache.object_cache), 0,
                         "object cache should be empty")

    def test_clear(self):
        process = Process(tme=1, pid=2)
        process2 = Process(tme=2, pid=2)
        process3 = Process(tme=0, pid=2)
        process4 = Process(tme=0, pid=3)

        self.objectCache.add_data(data=process)
        self.objectCache.add_data(data=process2)
        self.objectCache.add_data(data=process3)
        self.objectCache.add_data(data=process4)

        self.assertEqual(len(self.objectCache.object_cache), 2,
                         "object cache should contain two different categories")
        self.assertEqual(len(self.objectCache.faulty_nodes), 0,
                         "object cache should not have faulty nodes")
        self.assertEqual(len(self.objectCache.unfound), 0,
                         "object cache should not have unfound nodes")

        self.objectCache.unfound.add(process)
        self.objectCache.clear()

        self.assertEqual(len(self.objectCache.object_cache), 0,
                         "object cache should be empty")
        self.assertEqual(len(self.objectCache.faulty_nodes), 0,
                         "faulty nodes should be empty")
        self.assertEqual(len(self.objectCache.unfound), 0, "unfound should be empty")

    def test_update(self):
        process = Process(tme=1, pid=2)
        self.objectCache.add_data(data=process)

        theProcess = self.objectCache.get_data(value=process.tme, key=process.pid)
        theProcess.name = "test"
        newProcess = self.objectCache.get_data(value=process.tme, key=process.pid)
        self.assertEqual("test", newProcess.name, "name is not identical")

    def test_updateIndex(self):
        process = Process(tme=1, pid=2, name="old")
        process2 = Process(tme=1, pid=2, name="new")

        self.objectCache.add_data(data=process)

        index = self.objectCache.data_index(value=process.tme, key=process.pid)
        self.objectCache.object_cache[process.pid][index] = process2

        newProcess = self.objectCache.get_data(value=process.tme, key=process.pid)
        self.assertEqual(process2.name, newProcess.name)

    def test_getNullObject(self):
        with self.assertRaises(DataNotInCacheException):
            self.objectCache.get_data(value=1, key=1)


if __name__ == '__main__':
    unittest.main()
