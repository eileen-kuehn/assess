from assess.algorithms.treedistancealgorithm import TreeDistanceAlgorithm


class TreeEditDistanceAlgorithm(TreeDistanceAlgorithm):
    def __init__(self, **kwargs):
        TreeDistanceAlgorithm.__init__(self, **kwargs)

    def _add_event(self, event, **kwargs):
        print("adding event %s" % event)
