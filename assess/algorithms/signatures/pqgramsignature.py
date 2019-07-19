"""
This module provides an adapted implementation of pq-grams.
"""
from assess.algorithms.signatures.signatures import Signature


class PQGramSignature(Signature):
    """
    The PQGramSignature implements the pq-gram from literature but takes some
    adaptations to make it usable on streamed tree data.
    """
    def __init__(self, height=1, width=0):
        Signature.__init__(self)
        self._height = height
        self._width = width

    def prepare_signature(self, node, parent):
        parents = self.parent_generator(node)
        siblings = self.sibling_generator(node, self._width)
        # Attention: this ordering is different from original pq-grams!
        algorithm_id = "_".join([next(parents) for _ in range(self._height)]) + \
                       ("_%s_" % node.name) + \
                       "_".join([next(siblings) for _ in range(self._width)])
        self._prepare_signature(node, algorithm_id)

    def finish_node(self, node):
        # node is the PARENT of the current hierarchy ^^
        result = []
        if node.children_list():
            # take the last node to initialize the generators
            parent_generator = self.parent_generator(node)
            parents = [node.name] + [next(parent_generator) for _ in
                                     range(self._height - 1)]
            siblings = list(self.sibling_finish_generator(node, self._width))
            while siblings:
                algorithm_id = "_".join(parents) + \
                               ("_%s_" % "") + \
                               "_".join(siblings)
                result.append(algorithm_id)
                siblings.pop()
        return result

    @staticmethod
    def parent_generator(root):
        """
        Generator returns names of parents in order. When no more parents are
        existent, an empty string is returned.

        :param root: The node to start at
        :return: Parent name generator
        """
        while True:
            try:
                root = root.parent()
            except AttributeError:
                break
            else:
                try:
                    yield root.name
                except AttributeError:
                    break
        while True:
            yield ''

    def __repr__(self):
        return self.__class__.__name__ + " (p=%d, q=%d)" % (self._height, self._width)
