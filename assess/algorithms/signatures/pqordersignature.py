from assess.algorithms.signatures.signatures import Signature, ParentChildByNameTopologySignature


class PQOrderSignature(Signature):
    """
    The PQOrder Signature creates a signature that is required to eliminate permutations within
    data. It is dependent on infinite-length encoding in p dimension and finite-length encoding
    in Q dimension. Furthermore, it performs an ordering in Q dimension for width + 1 nodes.
    Hence, only width nodes are encoded. The ordering also includes the actual anchor node.
    Besides the anchor node width siblings are stored.
    """
    def __init__(self, width=1):
        Signature.__init__(self)
        self._width = width

    def prepare_signature(self, node, parent):
        ordered_nodes = [node.name]
        siblings = self.sibling_generator(node)
        for _ in xrange(self._width + 1):
            ordered_nodes.append(next(siblings))
        ordered_nodes.sort()  # ascending order
        algorithm_id = "%s_%s_%s" % (
            "_".join(ordered_nodes[-(self._width+1):-1]),  # up to width ordered siblings
            ordered_nodes[-1],  # last element as anchor node name
            hash(self.get_signature(parent, None, dimension="p") if parent is not None else node.name)
        )
        p_signature = ParentChildByNameTopologySignature.signature_string(
            node.name, self.get_signature(parent, None, dimension="p") if parent is not None else node.name)
        self._prepare_signature(node, algorithm_id, p=p_signature)

    def finish_node(self, node):
        result = []
        if len(node.children_list()) > 0:
            # we need to consider the insertion of empty nodes
            ordered_nodes = node.children_list()[-(self._width+1):]
            ordered_nodes = [node.name for node in ordered_nodes]
            ordered_nodes.sort()
            if len(ordered_nodes) > self._width:
                ordered_nodes.pop(0)
            for _ in xrange(self._width):
                algorithm_id = "%s_%s_%s" % (
                    "_".join(ordered_nodes[-self._width:]),
                    "",
                    hash(self.get_signature(node.parent(), None, dimension="p"))
                )
                result.append(algorithm_id)
                if len(ordered_nodes) > 1:
                    ordered_nodes.pop(0)
                else:
                    ordered_nodes.append("")
        return result

    @staticmethod
    def sibling_generator(node):
        """
        Generator returns names of left siblings in order. When no more siblings to the left
        can be found, an empty string is returned.

        :param node: The node to start at
        :return: Sibling name generator
        """
        position = node.node_number()
        parent = node.parent()
        neighbors = parent.children_list()[:position] if parent is not None else []
        for neighbor in reversed(neighbors):
            yield neighbor.name
        while True:
            yield ""

    def __repr__(self):
        return self.__class__.__name__ + " (q=%d)" % self._width
