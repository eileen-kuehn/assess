import os

import assess_tests

from assess.generators.gnm_importer import CSVTreeBuilder
from assess.prototypes.simpleprototypes import Prototype, Tree


def simple_prototype():
    prototype_tree = Prototype()
    root = prototype_tree.add_node("root", tme=0, exit_tme=3, pid=1, ppid=0)
    root.add_node("test", tme=0, exit_tme=1, pid=2, ppid=1)
    root.add_node("muh", tme=0, exit_tme=2, pid=3, ppid=1)
    root.add_node("test", tme=1, exit_tme=2, pid=4, ppid=1)
    root.add_node("muh", tme=1, exit_tme=3, pid=5, ppid=1)
    return prototype_tree


def simple_monitoring_tree():
    test_tree = Prototype()
    tree_root = test_tree.add_node("root", tme=0, exit_tme=3, pid=1, ppid=0, traffic=[])
    tree_root.add_node("test", tme=0, exit_tme=1, pid=2, ppid=1, traffic=[])
    tree_root.add_node("test", tme=1, exit_tme=2, pid=3, ppid=1, traffic=[])
    tree_root.add_node("muh", tme=1, exit_tme=3, pid=4, ppid=1, traffic=[])
    return test_tree


def simple_unique_node_tree():
    test_tree = Prototype()
    tree_root = test_tree.add_node("root", tme=0, exit_tme=3, pid=1, ppid=0)
    tree_root.add_node("bla", tme=0, exit_tme=1, pid=2, ppid=1)
    tree_root.add_node("test", tme=1, exit_tme=2, pid=3, ppid=1)
    tree_root.add_node("muh", tme=1, exit_tme=3, pid=4, ppid=1)
    return test_tree


def simple_repeated_monitoring_tree():
    test_tree = Tree()
    tree_root = test_tree.add_node("root", tme=0, exit_tme=3, pid=1, ppid=0)
    tree_root.add_node("test", tme=0, exit_tme=1, pid=2, ppid=1)
    tree_root.add_node("test", tme=0, exit_tme=1, pid=5, ppid=1)
    tree_root.add_node("test", tme=0, exit_tme=1, pid=6, ppid=1)
    tree_root.add_node("test", tme=0, exit_tme=1, pid=7, ppid=1)
    tree_root.add_node("test", tme=1, exit_tme=2, pid=3, ppid=1)
    tree_root.add_node("muh", tme=1, exit_tme=3, pid=4, ppid=1)
    return test_tree


def simple_additional_monitoring_tree():
    test_tree = Prototype()
    tree_root = test_tree.add_node("root", tme=0, exit_tme=3, pid=1, ppid=0)
    tree_root.add_node("hello", tme=0, exit_tme=2, pid=2, ppid=1)
    tree_root.add_node("yes", tme=0, exit_tme=1, pid=3, ppid=1)
    tree_root.add_node("test", tme=0, exit_tme=1, pid=4, ppid=1)
    tree_root.add_node("muh", tme=0, exit_tme=2, pid=5, ppid=1)
    tree_root.add_node("test", tme=1, exit_tme=3, pid=6, ppid=1)
    return test_tree


def real_tree(path=None, absolute=False):
    if path is None:
        path = "data/c01-007-102/1/1-process.csv"
    csv_builder = CSVTreeBuilder()
    if absolute:
        return csv_builder.build(path)
    return csv_builder.build(
        os.path.join(os.path.dirname(assess_tests.__file__), path)
    )
