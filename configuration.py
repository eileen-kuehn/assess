from assess.algorithms.incrementaldistancealgorithm import IncrementalDistanceAlgorithm
from assess.algorithms.signatures.signatures import *

configurations = [{
    "algorithms":[
        IncrementalDistanceAlgorithm
    ], "signatures": [
        lambda: ParentChildByNameTopologySignature(),
        lambda: ParentChildOrderTopologySignature(),
        lambda: ParentChildOrderByNameTopologySignature(),
        lambda: ParentCountedChildrenByNameTopologySignature(count=3),
        lambda: ParentCountedChildrenByNameTopologySignature(count=4)
    ]
}]

