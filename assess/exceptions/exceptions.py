"""
Module implements different Exceptions being used within ASSESS.
"""
from utility.exceptions import BasicException


class EventNotSupportedException(BasicException):
    """Thrown when algorithm does not support a specific event"""
    def __init__(self, event=None):
        BasicException.__init__(
            self,
            "Received [%s] event and does not support it so far!" % event
        )


class NodeNotFoundException(BasicException):
    """Thrown when a specific node cannot be found"""
    def __init__(self, node=None, amount=None):
        BasicException.__init__(
            self,
            "Cannot find %s between %s" % (node, amount)
        )


class TreeInvalidatedException(BasicException):
    """Thrown when an invalid tree is being created"""
    def __init__(self):
        BasicException.__init__(
            self,
            "An invalid tree is being created"
        )


class NodeNotEmptyException(BasicException):
    """Thrown when trying to remove a node that still has children"""
    def __init__(self):
        BasicException.__init__(
            self,
            "A node is trying to be removed that still has children"
        )


class NodeNotRemovedException(BasicException):
    """Thrown when a node could not be removed"""
    def __init__(self):
        BasicException.__init__(
            self,
            "A node could not be removed from tree"
        )


class MatrixDoesNotMatchBounds(BasicException):
    """Thrown when the distance matrix is expanded over its bounds"""
    def __init__(self, expected=None, width=None, height=None):
        BasicException.__init__(
            self,
            "The bounds of the matrix do not match (expected: %dx%d, received: width %d, height %d"
            % (expected, expected, width, height)
        )


class DecoratorNotFoundException(BasicException):
    """Thrown when updating decorators and a matching decorator is not found"""
    def __init__(self, decorator=None):
        BasicException.__init__(
            self,
            "No matching decorator has been found for %s" % decorator
        )
