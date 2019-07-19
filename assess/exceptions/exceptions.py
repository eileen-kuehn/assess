"""
Module implements different Exceptions being used within ASSESS.
"""


class EventNotSupportedException(Exception):
    """Thrown when algorithm does not support a specific event"""
    def __init__(self, event=None):
        Exception.__init__(
            self,
            "Received [%s] event and does not support it so far!" % event
        )


class NodeNotFoundException(Exception):
    """Thrown when a specific node cannot be found"""
    def __init__(self, node=None, amount=None):
        Exception.__init__(
            self,
            "Cannot find %s between %s" % (node, amount)
        )


class TreeInvalidatedException(Exception):
    """Thrown when an invalid tree is being created"""
    def __init__(self):
        Exception.__init__(
            self,
            "An invalid tree is being created"
        )


class TreeNotStartedException(Exception):
    """ Thrown when event is added to algorithm and tree is not started"""
    def __init__(self):
        Exception.__init__(
            self,
            "Event was added without correct initialisation of algorithm "
            "(tree not started)"
        )


class NodeNotEmptyException(Exception):
    """Thrown when trying to remove a node that still has children"""
    def __init__(self):
        Exception.__init__(
            self,
            "A node is trying to be removed that still has children"
        )


class NodeNotRemovedException(Exception):
    """Thrown when a node could not be removed"""
    def __init__(self):
        Exception.__init__(
            self,
            "A node could not be removed from tree"
        )


class MatrixDoesNotMatchBounds(Exception):
    """Thrown when the distance matrix is expanded over its bounds"""
    def __init__(self, expected=None, width=None, height=None):
        Exception.__init__(
            self,
            "The bounds of the matrix do not match (expected: %dx%d, "
            "received: width %d, height %d"
            % (expected, expected, width, height)
        )


class DecoratorNotFoundException(Exception):
    """Thrown when updating decorators and a matching decorator is not found"""
    def __init__(self, decorator=None):
        Exception.__init__(
            self,
            "No matching decorator has been found for %s" % decorator
        )


class DataNotInCacheException(Exception):
    pass
