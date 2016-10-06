from assess.algorithms.signatures.signatures import Signature


class PQGramSignature(Signature):
    """
    The PQGramSignature implements the pq-gram from literature but takes some adaptations to make
    it usable on
    """
    def __init__(self, height=1, width=1):
        Signature.__init__(self)
        self._height = height
        self._width = width

    def prepare_signature(self, node, parent):
        def parent_generator(root):
            while True:
                try:
                    root = root.parent()
                except AttributeError:
                    root = None
                yield root.name if root is not None else ""

        def sibling_generator(node):
            position = node.node_number()
            parent = node.parent()
            neighbors = parent.children_list()[0:position] if parent is not None else []
            for neighbor in reversed(neighbors):
                yield neighbor.name
            while True:
                yield ""

        parents = parent_generator(node)
        siblings = sibling_generator(node)
        algorithm_id = "_".join(reversed([next(parents)
                                for _ in range(self._height)])) + ("_%s_" % node.name) + \
                       "_".join([next(siblings)
                                for _ in range(self._width)])
        self._prepare_signature(node, algorithm_id)
