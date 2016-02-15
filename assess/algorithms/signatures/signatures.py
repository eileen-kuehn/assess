from assess.exceptions.exceptions import NodeNotFoundException


class Signature(object):
    """
    Signatures are a concept to create IDs based on processes inside the trees.
    By using signatures, similar nodes might be grouped for example. This improves
    the compression factor but might decrease the precision of the algorithm.
    """
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

    def _node_number(self, node, neighboring_nodes):
        for i in range(0, len(neighboring_nodes)):
            if node == neighboring_nodes[i]:
                number = i
                break
        else:
            raise NodeNotFoundException
        return number

    def __repr__(self):
        return self.__class__.__name__


class ParentCountedChildrenByNameTopologySignature(Signature):
    def __init__(self, count=20):
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
            position = self._node_number(node, neighbors)
            for j in range(position-1, position-1-self._count, -1):
                if j >= 0:
                    results.insert(0, neighbors[j].name)
                else:
                    results.insert(0, "")
        else:
            results = ["" for i in range(0, self._count)]
        return results

    def __repr__(self):
        return self.__class__.__name__ + " (count: %d)" % self._count


class ParentChildByNameTopologySignature(Signature):
    def prepare_signature(self, node):
        algorithm_id = "%s_%s" %(
            node.name,
            hash(self.get_signature(node.parent()) if node.parent() is not None else node.name)
        )
        self._prepare_signature(node, algorithm_id)


class ParentChildOrderTopologySignature(Signature):
    def prepare_signature(self, node):
        count = self._node_number(node, list(node.parent().children()) if node.parent() is not None else [node])
        algorithm_id = "%s.%d_%s" % (
            self._first_part_algorithm_id(self.get_signature(node.parent()) if node.parent() is not None else ""),
            count,
            hash(self.get_signature(node.parent()) if node.parent() is not None else node.name)
        )
        self._prepare_signature(node, algorithm_id)

    def _first_part_algorithm_id(self, algorithm_id):
        return algorithm_id.split("_")[0]


class ParentChildOrderByNameTopologySignature(ParentChildOrderTopologySignature):
    def prepare_signature(self, node):
        count = self._node_number(node, list(node.parent().children()) if node.parent() is not None else [node])
        algorithm_id = "%s.%d_%s_%s" % (
            self._first_part_algorithm_id(self.get_signature(node.parent()) if node.parent() is not None else ""),
            count,
            node.name,
            hash(self.get_signature(node.parent()) if node.parent() is not None else node.name)
        )
        self._prepare_signature(node, algorithm_id)
