"""
This module provides an adapted implementation of pq-grams.
"""
from assess.algorithms.signatures.signatures import Signature


class PQGramSignature(Signature):
    """
    The PQGramSignature implements the pq-gram from literature but takes some adaptations to make
    it usable on streamed tree data.
    """
    def __init__(self, height=1, width=1):
        Signature.__init__(self)
        self._height = height
        self._width = width

    def prepare_signature(self, node, parent):
        parents = self.parent_generator(node)
        siblings = self.sibling_generator(node)
        # Attention: this ordering is different from original pq-grams!
        algorithm_id = "_".join(reversed([next(parents) for _ in range(self._height)])) + \
                       ("_%s_" % node.name) + \
                       "_".join([next(siblings) for _ in range(self._width)])
        self._prepare_signature(node, algorithm_id)

    def finish_node(self, node):
        result = []
        if len(node.children_list()) > 0:
            # take the last node to initialize the generators
            anchor = node.children_list()[-1]
            parent_generator = self.parent_generator(anchor)
            parents = list(reversed([next(parent_generator) for _ in range(self._height)]))
            siblings = node.children_list()[-self._width:]

            for _ in range(self._width):
                algorithm_id = "_".join(parents) + ("_%s_" % "") + \
                               "_".join(str(sibling.name) if sibling is not None else "" for sibling in siblings)
                result.append(algorithm_id)
                if len(siblings) >= self._width:
                    siblings.pop(0)
                siblings.append(None)
        return result

    @staticmethod
    def parent_generator(root):
        """
        Generator returns names of parents in order. When no more parents are existent, an
        empty string is returned.

        :param root: The node to start at
        :return: Parent name generator
        """
        while True:
            try:
                root = root.parent()
            except AttributeError:
                root = None
            yield root.name if root is not None else ""

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
