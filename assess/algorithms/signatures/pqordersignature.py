import zlib

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
        ordered_nodes = [node.name] + list(self.sibling_generator(node, self._width + 1))
        ordered_nodes.sort()  # ascending order
        algorithm_id = "%s_%s_%s" % (
            "_".join(ordered_nodes[1:-1]),  # up to width ordered siblings
            ordered_nodes[-1],  # last element as anchor node name
            zlib.adler32(self.get_signature(parent, None, dimension="p").encode('utf-8', errors='surrogateescape') if parent is not None else b'')
        )
        p_signature = ParentChildByNameTopologySignature.signature_string(
            node.name, self.get_signature(parent, None, dimension="p") if parent is not None else '')
        self._prepare_signature(node, algorithm_id, p=p_signature)

    def finish_node(self, node):
        # node is the PARENT of the current hierarchy :D
        result = []
        p_signature = ParentChildByNameTopologySignature.signature_string(
            '',
            self.get_signature(node, None, dimension="p")
        )
        if node.children_list():
            # we need to consider the insertion of empty nodes
            ordered_nodes = list(self.sibling_finish_generator(node, self._width + 1))
            if ordered_nodes:
                ordered_nodes.sort()
                ordered_nodes.pop(0)
                while ordered_nodes:
                    algorithm_id = "%s_%s" % (
                        "_".join(ordered_nodes),
                        p_signature
                    )
                    result.append(algorithm_id)
                    ordered_nodes.pop(0)
        return result

    def __repr__(self):
        return self.__class__.__name__ + " (q=%d)" % self._width
