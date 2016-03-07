class Signature(object):
    """
    Signatures are a concept to create IDs based on processes inside the trees.
    By using signatures, similar nodes might be grouped for example. This improves
    the compression factor but might decrease the precision of the algorithm.
    """
    def prepare_signature(self, node, parent):
        """
        Methods takes a node and prepares its signature. The signature is directly
        attached to the node.
        :param node: The node whose signature needs to be calculated.
        """
        self._prepare_signature(node, node.name)

    def _prepare_signature(self, node, node_id):
        node.__dict__.setdefault('signature_id', {})[self] = str(node_id)

    def get_signature(self, node, parent):
        """
        Method returns the signature of the given node. If no signature has been
        assigned so far, it is calculated and attached.
        :param node: The node whose signature should be returned.
        :return: The signature.
        """
        try:
            return node.signature_id[self]
        except (AttributeError, KeyError):
            self.prepare_signature(node, parent)
            return node.signature_id[self]

    def __repr__(self):
        return self.__class__.__name__


class ParentChildByNameTopologySignature(Signature):
    def prepare_signature(self, node, parent):
        algorithm_id = "%s_%s" % (
            node.name,
            hash(self.get_signature(parent, None) if parent is not None else node.name)
        )
        self._prepare_signature(node, algorithm_id)


class ParentChildOrderTopologySignature(Signature):
    def prepare_signature(self, node, parent):
        count = node.node_number()
        parent_signature = self.get_signature(parent, None) if parent is not None else None
        algorithm_id = "%s.%d_%s" % (
            self._first_part_algorithm_id(parent_signature if parent_signature is not None else ""),
            count,
            hash(parent_signature if parent_signature is not None else node.name)
        )
        self._prepare_signature(node, algorithm_id)

    def _first_part_algorithm_id(self, algorithm_id):
        return algorithm_id.split("_")[0]


class ParentChildOrderByNameTopologySignature(ParentChildOrderTopologySignature):
    """
    For this method order for processes matters. If you do have several processes with the
    same name after each other, they get the same name. If they appear again after another
    process it differs.
    """
    def prepare_signature(self, node, parent):
        count = node.node_number()
        parent_signature = self.get_signature(parent, None) if parent is not None else None
        grouped_count = self._grouped_count(node, count)
        algorithm_id = "%s.%d_%s_%s" % (
            self._first_part_algorithm_id(parent_signature if parent_signature is not None else ""),
            grouped_count,
            node.name,
            hash(parent_signature if parent_signature is not None else node.name)
        )
        self._prepare_signature(node, algorithm_id)

    def _grouped_count(self, node, position):
        parent = node.parent()
        if parent is None or parent.child_count() <= 0:
            return 0
        children = list(parent.children())
        names = []
        for i in range(position+1):
            current_name = str(children[i].name)
            last_name = names[len(names)-1] if len(names) > 0 else ""
            if current_name != last_name:
                names.append(current_name)
        return len(names)-1


class ParentCountedChildrenByNameTopologySignature(Signature):
    """
    This class constructs the signature by using up to count neighbouring nodes.
    If there are less neighbours available, nothing is appended. On this way, there
    is an upper bound in possible signatures being created.
    """
    def __init__(self, count=20):
        Signature.__init__(self)
        self._count = count

    def prepare_signature(self, node, parent):
        neighbors = self.predecessors(
                node,
                parent.children() if parent is not None else [],
        )
        algorithm_id = "%s_%s_%s" %(
            "_".join(str(node) for node in neighbors),
            node.name,
            hash(self.get_signature(parent, None) if parent is not None else node.name)
        )
        self._prepare_signature(node, algorithm_id)

    def predecessors(self, node, neighbors):
        # TODO: can be improved
        results = []
        neighbors = list(neighbors)
        if len(neighbors) > 0:
            position = node.node_number()
            for j in range(position-1, position-1-self._count, -1):
                if j >= 0:
                    results.insert(0, neighbors[j].name)
        return results

    def __repr__(self):
        return self.__class__.__name__ + " (count: %d)" % self._count
