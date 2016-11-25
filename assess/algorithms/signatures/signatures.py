"""
Module supports different signature implementations that can be used to compress trees based
on different characteristics of workflows.
"""
from assess.algorithms.signatures.signaturecache import SignatureCache, PrototypeSignatureCache


class Signature(object):
    """
    Signatures are a concept to create IDs based on processes inside the trees.
    By using signatures, similar nodes might be grouped for example. This improves
    the compression factor but might decrease the precision of the algorithm.
    """
    signature_cache_class = SignatureCache
    prototype_signature_cache_class = PrototypeSignatureCache

    def __init__(self, *args, **kwargs):
        self.count = 1

    def __new__(cls, *args, **kwargs):
        for arg in args:
            if "ParentChildByNameTopologySignature" in arg:
                return ParentChildByNameTopologySignature.__new__(
                    ParentChildByNameTopologySignature)
            elif "ParentChildOrderTopologySignature" in arg:
                return ParentChildOrderTopologySignature()
            elif "ParentChildOrderByNameTopologySignature" in arg:
                return ParentChildOrderByNameTopologySignature()
        #     elif "ParentCountedChildrenByNameTopologySignature" in arg:
        #         # TODO: can kwargs be edited? Than to splitting to get the actual count
        #         return ParentCountedChildrenByNameTopologySignature()
        return super(Signature, cls).__new__(cls)

    def prepare_signature(self, node, parent):
        """
        Methods takes a node and prepares its signature. The signature is directly
        attached to the node.
        :param node: The node whose signature needs to be calculated.
        :param parent: Parent of the node
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

    def finish_node(self, node):
        return []

    def __repr__(self):
        return self.__class__.__name__


class ParentChildByNameTopologySignature(Signature):
    """
    ParentChildByNameTopologySignature mainly uses the names of single nodes as well as the actual
    hierarchy of the node by considering next to the name also the signature of its parent.
    As nodes inside a list of children with an equal name are accumulated, this signature is very
    good for compression when nodes are used repeatedly.

    Attention: The signature does not take care on the ordering of nodes.
    """
    def prepare_signature(self, node, parent):
        algorithm_id = "%s_%s" % (
            node.name,
            hash(self.get_signature(parent, None) if parent is not None else node.name)
        )
        self._prepare_signature(node, algorithm_id)


class ParentChildOrderTopologySignature(Signature):
    """
    ParentChildOrderTopologySignature just looks at the order and count of nodes. No names or other
    attributes are considered. Therefore only topology is key.
    You cannot expect any compression from this signature except the skipping of attributes and
    their values.
    """
    def prepare_signature(self, node, parent):
        count = node.node_number()
        parent_signature = self.get_signature(parent, None) if parent is not None else None
        algorithm_id = "%s.%d_%s" % (
            self._first_part_algorithm_id(parent_signature if parent_signature is not None else ""),
            count,
            hash(parent_signature if parent_signature is not None else node.name)
        )
        self._prepare_signature(node, algorithm_id)

    @staticmethod
    def _first_part_algorithm_id(algorithm_id):
        return algorithm_id.split("_")[0]


class ParentChildOrderByNameTopologySignature(ParentChildOrderTopologySignature):
    """
    For this method order for processes matters. If you do have several processes with the same
    name after each other, they get the same resulting signature. If they appear again after another
    process it differs.
    """
    def prepare_signature(self, node, parent):
        count = node.node_number()
        if count > 0:
            previous_node = parent.children_list()[count-1]
            grouped_count = previous_node.group_position \
                if previous_node.name == node.name else previous_node.group_position + 1
        else:
            grouped_count = 0
        node.group_position = grouped_count

        parent_signature = self.get_signature(parent, None) if parent is not None else None
        algorithm_id = "%s.%d_%s_%s" % (
            self._first_part_algorithm_id(parent_signature if parent_signature is not None else ""),
            grouped_count,
            node.name,
            hash(parent_signature if parent_signature is not None else node.name)
        )
        self._prepare_signature(node, algorithm_id)


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
        position = node.node_number()
        neighbors = parent.children_list()[-((len(parent.children_list())-position) +
                                             self._count):position] if parent is not None else []
        algorithm_id = "%s_%s_%s" % (
            "_".join(str(node.name) for node in neighbors),
            node.name,
            hash(self.get_signature(parent, None) if parent is not None else node.name)
        )
        self._prepare_signature(node, algorithm_id)

    def finish_node(self, node):
        result = []
        if len(node.children_list()) > 0:
            # we need to consider the insertion of empty nodes
            parent = node
            neighbors = parent.children_list()[-self._count:]
            for _ in range(self._count):
                algorithm_id = "%s_%s_%s" % (
                    "_".join(str(node.name) if node is not None else "" for node in neighbors),
                    "",
                    hash(self.get_signature(parent, None))
                )
                result.append(algorithm_id)
                # it might happen that we do not have a sufficient amount of nodes, so leave them
                if len(neighbors) >= self._count:
                    neighbors.pop(0)
                neighbors.append(None)
        return result

    def __repr__(self):
        return self.__class__.__name__ + " (count: %d)" % self._count
