from utility.exceptions import *


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
