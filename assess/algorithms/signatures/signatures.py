from assess.prototypes.simpleprototypes import Tree
from assess.exceptions.exceptions import NodeNotFoundException


class Signature(object):
    def prepare_signature(self, node):
        self._prepare_signature(node, node.name)

    def _prepare_signature(self, node, node_id):
        node.__dict__.setdefault('signature_id', {})[self] = node_id

    def get_signature(self, node):
        try:
            return node.signature_id[self]
        except (AttributeError, KeyError):
            self.prepare_signature(node)
            return node.signature_id[self]


class ParentCountedChildrenByNameTopologySignature(Signature):
    def __init__(self, count=0):
        Signature.__init__(self)
        self._count = count

    def prepare_signature(self, node):
        neighbors = self.predecessors(
                node,
                node.parent().children() if node.parent() is not None else [],
        )
        algorithm_id = "%s_%s_%s" %(
            "_".join(node for node in neighbors),
            node.name,
            hash(self.get_signature(node.parent()) if node.parent() is not None else node.name)
        )
        self._prepare_signature(node, algorithm_id)

    def predecessors(self, node, neighbors):
        results = []
        neighbors = list(neighbors)
        if len(neighbors) > 0:
            position = 0
            for i in range(0, len(neighbors)):
                if neighbors[i] == node:
                    position = i
                else:
                    continue
                break
            else:
                raise NodeNotFoundException()
            for j in range(position-1, position-1-self._count, -1):
                if j >= 0:
                    results.insert(0, neighbors[j].name)
                else:
                    results.insert(0, "")
        else:
            results = ["" for i in range(0, self._count)]
        return results


class ParentChildByNameTopologySignature(Signature):
    def prepare_signature(self, node):
        algorithm_id = "%s_%s" %(
            node.name,
            hash(self.get_signature(node.parent()) if node.parent() is not None else node.name)
        )
        self._prepare_signature(node, algorithm_id)


class ParentChildOrderTopologySignature(Signature):
    def prepare_signature(self, node):
        depth = node.depth()
        if depth == 0:
            # root processes
            name = "%d" % depth
        else:
            neighbors = node.parent().children()
            count = self._node_number_on_layer(node, neighbors)
            name = "%s.%d" % (node.parent().name, count)
        algorithm_id = Tree.unique_name(
                name,
                node.depth(),
                self.get_signature(node.parent()) if node.parent() is not None else node.name
        )
        node.name = name
        self._prepare_signature(node, algorithm_id)

    def _node_number_on_layer(self, process, neighboring_processes):
        count = 0
        for node in neighboring_processes:
            count += 1
            if node == process:
                return count
        raise NodeNotFoundException(process, neighboring_processes)


class ParentChildOrderByNameTopologySignature(ParentChildOrderTopologySignature):
    # TODO: numbers have wrong order?!
    def prepare_signature(self, node):
        depth = node.depth()
        if depth == 0:
            # root processes
            name = "%s.%d" % (node.name, depth)
        else:
            neighbors = node.parent().children()
            count = self._node_number_on_layer(node, neighbors)
            name = "%s.%d" % (node.name, count)
        algorithm_id = Tree.unique_name(
                name,
                node.depth(),
                self.get_signature(node.parent()) if node.parent() is not None else node.name
        )
        self._prepare_signature(node, algorithm_id)
