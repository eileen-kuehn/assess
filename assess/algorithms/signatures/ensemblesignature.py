"""
This module implements the possibility to encapsulate different signatures into one single
signature. This allows to pick the best available signature to calculate distances.
"""
from assess.algorithms.signatures.signatures import Signature
from assess.algorithms.signatures.ensemblesignaturecache import EnsembleSignatureCache, \
    EnsemblePrototypeSignatureCache


class EnsembleSignature(Signature):
    signature_cache_class = EnsembleSignatureCache
    prototype_signature_cache_class = EnsemblePrototypeSignatureCache

    def __init__(self, signatures=None):
        Signature.__init__(self)
        self._signatures = signatures
        self.count = len(signatures)

    def prepare_signature(self, node, parent):
        for signature in self._signatures:
            signature.prepare_signature(node, parent)

    def get_signature(self, node, parent):
        """
        EnsembleSignature calls all of its signatures to get the relevant tokens. Those are appended
        to a list to be returned. The position in the list defines the signature that was used to
        generate the token.

        :param node:
        :param parent:
        :return: List of token in signature order
        """
        result = []
        for signature in self._signatures:
            result.append(signature.get_signature(node, parent))
        return result

    def __repr__(self):
        return "%s (%s)" % (self.__class__.__name__, ", ".join(
            [repr(signature) for signature in self._signatures]))
