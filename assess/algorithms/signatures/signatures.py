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

    def _prepare_signature(self, node, node_id, **kwargs):
        try:
            node_signature_ids = node.signature_id
        except AttributeError:
            node.signature_id = node_signature_ids = {}
        node_signature_ids[self] = self_signature_ids = {None: node_id}
        self_signature_ids.update(kwargs)

    def get_signature(self, node, parent, dimension=None):
        """
        Method returns the signature of the given node. If no signature has been
        assigned so far, it is calculated and attached.
        :param node: The node whose signature should be returned.
        :param parent: The parent of the node
        :param dimension: Special dimension of signature if existent
        :return: The signature.
        """
        try:
            return node.signature_id[self][dimension]
        except (AttributeError, KeyError):
            self.prepare_signature(node, parent)
            return node.signature_id[self][dimension]

    def finish_node(self, node):
        return []

    def sibling_generator(self, node, width):
        """
        Generator returns names of left siblings in order. When no more siblings to the left
        can be found, an empty string is returned.

        :param node: The node to start at
        :param width: number of siblings to return
        :return: Sibling names
        :rtype: generator
        """
        if hasattr(node, "attribute"):
            return self._sibling_generator(None, 0, width)
        else:
            position = node.node_number()
            parent = node.parent()
            return self._sibling_generator(parent, position, width)

    def sibling_finish_generator(self, parent, width):
        return self._sibling_generator(parent, None, width)

    @staticmethod
    def _sibling_generator(parent, position, width):
        returned_nodes = 0
        if parent and width > 0:
            if position is None:
                child_list = parent.children_list()
                for node in reversed(child_list):
                    if not hasattr(node, "attribute"):
                        returned_nodes += 1
                        yield node.name
                    if returned_nodes >= width:
                        break
                # handle special case that children are attributes only
                if returned_nodes == 0:
                    return
            else:
                for node in reversed(parent.children_list()[:position]):
                    if not hasattr(node, "attribute"):
                        returned_nodes += 1
                        yield node.name
                    if returned_nodes >= width:
                        break
        for _ in xrange(width - returned_nodes):
            yield ''

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
        algorithm_id = self.__class__.signature_string(
            node.name,
            self.get_signature(parent, None) if parent is not None else ''
        )
        self._prepare_signature(node, algorithm_id)

    @staticmethod
    def signature_string(node_name, parent_signature):
        """
        Parent signature usually looks like name_hash(parent_signature). Thus, we again perform
        a hash from parent_signature, to keep this format.

        :param node_name:
        :param parent_signature:
        :return:
        """
        return "%s_%s" % (node_name, hash(parent_signature))


class ParentChildOrderTopologySignature(Signature):
    """
    ParentChildOrderTopologySignature just looks at the order and count of nodes. No names or other
    attributes are considered. Therefore only topology is key.
    You cannot expect any compression from this signature except the skipping of attributes and
    their values.
    """
    def prepare_signature(self, node, parent):
        parent_signature = self.get_signature(parent, None) if parent is not None else None
        algorithm_id = "%s.%d_%s" % (
            self._first_part_algorithm_id(parent_signature if parent_signature is not None else ""),
            node.node_number(),
            hash(parent_signature if parent_signature is not None else "")
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
            hash(parent_signature if parent_signature is not None else "")
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
        neighbors = parent.children_list()[(position - self._count if position > self._count else 0):position]\
            if parent is not None else []
        algorithm_id = "%s_%s_%s" % (
            "_".join(str(node.name) for node in neighbors),
            node.name,
            hash(self.get_signature(parent, None) if parent is not None else "")
        )
        self._prepare_signature(node, algorithm_id)

    def finish_node(self, node):
        result = []
        if node.children_list():
            # we need to consider the insertion of empty nodes
            parent = node
            parent_signature = hash(self.get_signature(parent, None))
            neighbors = list(self.sibling_finish_generator(node, self._count))
            while neighbors:
                result.append("%s_%s_%s" % (
                    "_".join(neighbors),
                    "",
                    parent_signature
                ))
                neighbors.pop()
        return result

    def __repr__(self):
        return self.__class__.__name__ + " (count: %d)" % self._count


class ParentSiblingSignature(Signature):
    """
    This class offers infinite P dimension encoding and fixed width finite-length Q encoding.
    No further things are performed in here, so no sorting or such
    """
    def __init__(self, width=20):
        Signature.__init__(self)
        self._width = width

    def prepare_signature(self, node, parent):
        siblings = self.sibling_generator(node, self._width)
        parent_signature = self.get_signature(parent, None, dimension="p") if parent is not None else ''
        p_signature = ParentChildByNameTopologySignature.signature_string(node.name, parent_signature)
        algorithm_id = "%s_%s" % (
            "_".join(siblings),
            p_signature
        )
        self._prepare_signature(node, algorithm_id, p=p_signature)

    def finish_node(self, node):
        # node is the PARENT of the current hierarchy :P
        result = []
        p_signature = ParentChildByNameTopologySignature.signature_string(
            '',
            self.get_signature(node, None, dimension="p")
        )
        if node.children_list():
            # we need to consider the insertion of empty nodes
            siblings = list(self.sibling_finish_generator(node, self._width))
            while siblings:
                algorithm_id = "%s_%s" % (
                    "_".join(siblings),
                    p_signature
                )
                result.append(algorithm_id)
                siblings.pop()
        return result

    def __repr__(self):
        return self.__class__.__name__ + " (width: %d)" % self._width
