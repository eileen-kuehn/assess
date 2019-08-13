"""
This module implements the possibility to encapsulate different signatures into
one single signature. This allows to pick the best available signature to
calculate distances.
"""
from itertools import zip_longest
from typing import List

from assess.algorithms.signatures.signatures import Signature
from assess.algorithms.signatures.ensemblesignaturecache import \
    EnsembleSignatureCache, EnsemblePrototypeSignatureCache


class EnsembleSignatureList(list):
    def __repr__(self):
        return "%s%s" % (self.__class__.__name__, list.__repr__(self))

    def __hash__(self):
        return hash(tuple(self))


class EnsembleSignature(Signature):
    signature_cache_class = EnsembleSignatureCache
    prototype_signature_cache_class = EnsemblePrototypeSignatureCache

    def __init__(self, signatures: List[Signature] = None):
        Signature.__init__(self)
        self._signatures = signatures
        self.count = len(signatures)

    def prepare_signature(self, node, parent):
        for signature in self._signatures:
            signature.prepare_signature(node, parent)

    def get_signature(self, node, parent):
        """
        EnsembleSignature calls all of its signatures to get the relevant tokens.
        Those are appended to a list to be returned. The position in the list
        defines the signature that was used to generate the token.

        :param node:
        :param parent:
        :return: List of token in signature order
        """
        result = EnsembleSignatureList()
        for signature in self._signatures:
            result.append(signature.get_signature(node, parent))
        return result

    def finish_node(self, node):
        result = EnsembleSignatureList()
        for signature in self._signatures:
            result.append(signature.finish_node(node))
        return [EnsembleSignatureList(element) for element in zip_longest(*result)]

    def __repr__(self):
        return "%s (%s)" % (self.__class__.__name__, ", ".join(
            [repr(signature) for signature in self._signatures]))
