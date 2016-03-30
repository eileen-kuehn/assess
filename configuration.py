from assess.algorithms.incrementaldistancealgorithm import IncrementalDistanceAlgorithm
from assess.algorithms.signatures.signatures import *
from assess.decorators.compressionfactordecorator import CompressionFactorDecorator
from assess.decorators.datadecorator import DataDecorator
from assess.decorators.distancematrixdecorator import DistanceMatrixDecorator
from assess.decorators.performancedecorator import PerformanceDecorator

# Most critical, so take as leading decorator
performance = PerformanceDecorator()
compression = CompressionFactorDecorator()
data = DataDecorator()
distance = DistanceMatrixDecorator(normalized=False)
distance2 = DistanceMatrixDecorator(normalized=True)
# Build decorator chain with performance as last
compression.decorator = performance
data.decorator = compression
distance2.decorator = data
distance.decorator = distance2

configurations = [{
    "algorithms": [
        IncrementalDistanceAlgorithm
    ], "signatures": [
        lambda: ParentChildByNameTopologySignature(),
        lambda: ParentChildOrderTopologySignature(),
        lambda: ParentChildOrderByNameTopologySignature(),
        lambda: ParentCountedChildrenByNameTopologySignature(count=3),
        lambda: ParentCountedChildrenByNameTopologySignature(count=4)
    ], "decorator": distance
}]

