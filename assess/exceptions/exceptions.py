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


class MatrixDoesNotMatchBounds(Exception):
    """Thrown when the distance matrix is expanded over its bounds"""
    def __init__(self, expected=None, width=None, height=None):
        Exception.__init__(
            self,
            "The bounds of the matrix do not match (expected: %dx%d, received: width %d, height %d"
            % (expected, expected, width, height)
        )
