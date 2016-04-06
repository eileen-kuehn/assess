import string
import random
from assess.prototypes.simpleprototypes import Prototype
from assess.events.events import Event


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


class RandomGenerator(object):
    def __init__(self, prototype_node_count=100, tree_node_count=100, relative_repetition=0, relative_matching=0.5, seed=None):
        self._prototype_node_count = prototype_node_count
        self._tree_node_count = tree_node_count
        self._relative_repetition = relative_repetition
        self._relative_matching = relative_matching
        self._seed = seed
        self._prototype = None
        if seed is not None:
            random.seed(seed)

    @property
    def prototype(self):
        if self._prototype is None:
            prototype = Prototype()
            root = prototype.add_node(name=id_generator(size=6), tme=0, pid=1, ppid=0)
            for i in range(self._prototype_node_count):
                # TODO: check if this is < or <=
                if root.child_count() > 0 and random.random() <= self._relative_repetition:
                    node_name = random.choice(root.children_list())
                    print("picked name")
                else:
                    node_name = id_generator()
                prototype.add_node(name=node_name, parent=root, tme=0, pid=i+2, ppid=1)
            assert prototype.node_count()-1 == self._prototype_node_count
            self._prototype = prototype
        return self._prototype

    def __iter__(self):
        exit_event_queue = []
        root = self._prototype.root()
        picking_list = root.children_list()
        yield Event.start(tme=0, pid=1, ppid=0, name=self._prototype.root().name)
        exit_event_queue.append(Event.exit(tme=0, pid=1, ppid=0, start_tme=0, name=root.name))
        picked = 0
        for i in range(self._tree_node_count):
            if random.random() <= self._relative_matching:
                try:
                    node = random.choice(picking_list)
                    picking_list.remove(node)
                except ValueError:
                    node = random.choice(root.children_list())
                node_name = node.name
                pid = node.pid
                picked += 1
            else:
                node_name = id_generator()
                pid = i+2
            yield Event.start(tme=0, pid=pid, ppid=1, name=node_name)
            exit_event_queue.append(Event.exit(tme=0, pid=i+2, ppid=1, name=node_name, start_tme=0))
        print(picked)
        while exit_event_queue:
            yield exit_event_queue.pop()
