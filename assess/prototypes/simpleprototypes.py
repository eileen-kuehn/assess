"""
Module describes a general tree as well as a more specialised prototype. Also
the definition for the single nodes is defined.
"""
import bisect
from collections import deque

from assess.algorithms.signatures.signatures import Signature
from assess.algorithms.signatures.ensemblesignature import EnsembleSignature
from assess.algorithms.signatures.ensemblesignaturecache import EnsembleSignatureCache
from assess.exceptions.exceptions import TreeInvalidatedException, \
    NodeNotEmptyException, \
    NodeNotRemovedException, NodeNotFoundException, DataNotInCacheException
from assess.events.events import Event, ProcessStartEvent, ProcessExitEvent, \
    TrafficEvent, EmptyProcessEvent, ParameterEvent
from assess.algorithms.signatures.signaturecache import SignatureCache, \
    PrototypeSignatureCache

from assess.utility.objectcache import ObjectCache
from assess.utility.randoms import id_generator

from gnmutils.exceptions import ObjectIsRootException


class OrderedTreeNode(object):
    """
    Class describes a node of a tree that ensures the correct order of nodes
    within the tree.

    :param node_id: ID of node
    :param name: Name of node
    :param parent: Parent node of node
    :param position: Position of node within siblings
    :param tree: Tree where node belongs to
    :param kwargs: Additional arguments
    """
    def __init__(self, node_id, name=None, parent=None, previous_node=None,
                 next_node=None, position=0, tree=None, **kwargs):
        self.name = name
        self.node_id = node_id
        self._parent = parent
        self._children = []
        self._prototype = tree
        self.previous_node = previous_node
        self.next_node = next_node
        self.position = position
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __hash__(self):
        return hash(id(self))

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        return self.dao() == other.dao()

    def dao(self):
        def check_keys(key):
            return not ("signature_id" in key
                        or "position" in key
                        or "previous_node" in key
                        or "next_node" in key
                        or key.startswith("_"))
        return {
            key: getattr(self, key) for key in vars(self) if check_keys(key)
        }

    def parameters(self):
        # TODO: those should be configured via black- or whitelists
        def check_keys(key):
            return not ("name" in key
                        or "node_id" in key
                        or "tme" in key
                        or "exit_tme" in key
                        or "pid" in key
                        or "ppid" in key)
        return {
            key: getattr(self, key) for key in self.dao() if check_keys(key)
        }

    def depth(self):
        """
        Method returns the depth of the current node within the tree. If the node
        is the root, then 0 is returned. So depth equals the number of parents.

        :return: Depth of the node within the tree
        """
        count = 0
        node = self
        while node.parent():
            count += 1
            node = node.parent()
        return count

    def children(self):
        """
        Generator that yields children of the node.

        :return: Generator for children
        """
        for child in self._children:
            yield child

    def children_list(self):
        """
        List of children of the node.

        :return: List of children
        """
        return self._children

    def child_count(self):
        """
        Method returns the current count of children of the node.

        :return: Count of children
        """
        return len(self._children)

    def node_count(self):
        """
        Method returns the count of nodes within the subtree of the node.
        The actual count is calculated recursively.

        :return: Count of nodes in subtree
        """
        count = 1
        for child in self.children():
            count += child.node_count()
        return count

    def node_number(self):
        """
        Method returns the position of the node regarding its siblings.
        If the node is the first element, 0 is returned.

        :return: Node position
        """
        return self.position

    def parent(self):
        """
        Method returns the parent of the node, if it does not have a parent,
        it returns None.

        :return: Parent, None otherwise
        """
        return self._parent

    def add_node(self, name=None, **kwargs):
        """
        Method to add a new node to the list of children of the node.
        It is appended to the end of the children's list.

        :param name: Name of the new node to add
        :param kwargs: Params to be added to the node
        :return: Reference to new created node
        """
        return self._prototype.add_node(name=name, parent=self, **kwargs)

    # Pickling
    # The next/previous node fields create infinite recursion when traversing
    # the tree, which is what pickle does. We store the IDs instead, and fetch
    # the real nodes when loading.
    # Since there is ALSO recursion with the tree itself, we wait for the tree
    # to be done loading everything and tell us about it.
    def __getstate__(self):
        state = self.__dict__.copy()
        if state['previous_node'] is not None:
            state['previous_node'] = state['previous_node'].node_id
        if state['next_node'] is not None:
            state['next_node'] = state['next_node'].node_id
        return state

    def __setstate__(self, state):
        self.__dict__ = state
        # NOTE: prev/next node resolution MUST be called externally

    def resolve_siblings(self):
        """
        Tell the node to load its siblings by ID; must be called once after unpickling
        """
        try:
            self.previous_node = self._prototype.node_by_node_id(self.previous_node)
        except NodeNotFoundException:
            if self.previous_node is not None:
                raise
        try:
            self.next_node = self._prototype.node_by_node_id(self.next_node)
        except NodeNotFoundException:
            if self.next_node is not None:
                raise

    def __repr__(self):
        return '%s(next=%s, prev=%s)' % (
            self.__class__.__name__,
            getattr(self.next_node, "node_id", None),
            getattr(self.previous_node, "node_id", None)
        )


class OrderedTree(object):
    """
    Class that builds up a tree that takes care of the order of nodes, so it
    does implement an ordered tree.
    """
    def __init__(self):
        self.root = None
        self._node_counter = 0
        self._unique_counter = 0
        self._last_node = None  # helper to build up global order
        self._nodes_dict = {}

    def unique_node_id(self, node_id=None):
        """
        Method returns a unique id.

        :return: Unique id
        """
        # nx.utils.generate_unique_node()
        if node_id is None:
            return str(self._unique_counter)
        return "%s_%s" % (str.split(node_id, "_")[0], id_generator(size=6))

    def node_count(self):
        """
        Returns the current count of nodes within the tree.

        :return: Current count of nodes
        """
        return self._node_counter

    def remove_node(self, node=None):
        if node.child_count() > 0:
            raise NodeNotEmptyException()
        node = self._nodes_dict.pop(node.node_id, None)
        if node is None:
            raise NodeNotRemovedException()
        else:
            self._node_counter -= 1
            # remove from parent
            children = node.parent().children_list()
            node_index = children.index(node)
            children.remove(node)
            # update node positions
            for index in range(node_index, len(children)):
                children[index].position -= 1
            if self._last_node == node:
                self._last_node = node.previous_node
                node.previous_node.next_node = None
            else:
                node.previous_node.next_node = node.next_node
                node.next_node.previous_node = node.previous_node

    def add_node(self, name=None, parent=None, previous_node=None, next_node=None,
                 node_id=None, **kwargs):
        """
        Method adds a new node to the actual tree. If parent is not given,
        the node gets the root node of the tree.

        :param name: Name of the node to create
        :param parent: Parent of the node to attach to
        :param previous_node: Reference to last node
        :param next_node: Reference to next node
        :param node_id: unique ID of node
        :param kwargs: Additional parameters of the node
        :return: Reference to the created node
        """
        if previous_node is None:
            # try to determine last known node
            previous_node = self._last_node
        # TODO: check if node_id is unique in tree
        node = OrderedTreeNode(
            node_id=node_id if node_id is not None else self.unique_node_id(),
            name=name,
            parent=parent,
            previous_node=previous_node,
            next_node=next_node,
            tree=self,
            position=parent.child_count() if parent is not None else 0,
            **kwargs
        )
        # First check if the generated node is valid within tree
        if self._nodes_dict.get(node.node_id, None) is not None:
            raise TreeInvalidatedException
        # Then go on with everything else
        if previous_node is not None:
            # set next node for last node
            previous_node.next_node = node
        if self.root is None:
            self.root = node
        else:
            parent.children_list().append(node)
        self._last_node = node
        self._node_counter += 1
        self._unique_counter += 1
        self._nodes_dict[node.node_id] = node
        return node

    def node_by_node_id(self, node_id=None):
        """
        Method allows the access to nodes by specifying their node_id.

        :param node_id: The node_id of the node to return.
        :return: Node whose node_id matches, otherwise None
        """
        node = self._nodes_dict.get(node_id, None)
        if node is None:
            raise NodeNotFoundException()
        return node

    def __setstate__(self, state):
        # Since self._nodes_dict contains all nodes, each node must be fully
        # unpickled before _nodes_dict can be created. This means the
        # OrderedTree is finalized AFTER the nodes. We need to trigger a post-
        # finalization step where nodes may look up siblings in the tree.
        self.__dict__ = state
        for node in self._nodes_dict.values():
            node.resolve_siblings()


class Tree(object):
    """
    Class that represents a tree with no ensured ordering of nodes.
    """
    def __init__(self):
        self._graph = OrderedTree()

    def remove_node(self, node=None, node_id=None):
        """
        Method removes a node from the actual tree. The method raises an error
        if the node still has children attached.

        :param node: The node to be removed
        :param node_id: unique ID of node
        """
        if node is None:
            node = self._graph.node_by_node_id(node_id=node_id)
        self._graph.remove_node(node=node)

    def remove_subtree(self, node=None, node_id=None):
        """
        Method removes a subtree from the actual tree, meaning, that a node and
        all its children are removed.

        :param node: The node where subtree removal starts from
        :param node_id: unique ID of node is removed recursively
        """
        if node is None:
            node = self._graph.node_by_node_id(node_id=node_id)
        nodes_to_be_removed = []
        for child in self.nodes(node=node):
            nodes_to_be_removed.append(child)
        while len(nodes_to_be_removed) > 0:
            node = nodes_to_be_removed.pop()
            self.remove_node(node=node)

    def add_node(self, name, parent=None, parent_node_id=None, **kwargs):
        """
        Method to add a new node to the tree. If given parent is None, and there
        is currently no root, then the node becomes the root of the tree.

        :param name: Name of the node to be created
        :param parent: Parent where to attach the node
        :param parent_node_id: Reference to parent within tree
        :param kwargs: Additional attribute of the node
        :return: Reference to the newly created node
        """
        if parent_node_id is not None:
            parent = self._graph.node_by_node_id(node_id=parent_node_id)
        if parent is None and self.root() is not None:
            raise TreeInvalidatedException
        try:
            return self._graph.add_node(name=name, parent=parent, **kwargs)
        except TreeInvalidatedException:
            # got a collision for node_id, so regenerate
            del kwargs["node_id"]
            return self._graph.add_node(
                name=name,
                parent=parent,
                node_id=self._graph.unique_node_id(),
                **kwargs
            )

    def node_count(self):
        """
        Method returns the current count of nodes within the tree.

        :return: Count of nodes
        """
        return self._graph.node_count()

    # TODO: implement stop condition for depth and width first
    def nodes(self, node=None, depth_first=True, order_first=False,
              include_marker=False):
        """
        Method that returns a generator yielding all nodes inside the tree,
        either in depth first or width first order.

        :param node: The node to start at
        :param depth_first: Depth first order if True, otherwise width first.
        :param order_first: Returns nodes by order they have been added.
        :param include_marker: Defines if empty nodes for marking end of children
            are included.
        :return: Generator for tree nodes.
        """
        def ofs(root):
            """
            Method follows links to next nodes to generate node order.

            :param root: Where to start node traversal
            :return: Order first node generator
            """
            while root is not None:
                yield root
                if include_marker:
                    # check if current node is the last in children
                    try:
                        if len(root.children_list()) == 0:
                            yield EmptyNode(parent=root)
                        if root == root.parent().children_list()[-1]:
                            yield EmptyNode(parent=root.parent())
                    except AttributeError:
                        # there is no parent
                        pass
                root = root.next_node

        def dfs(root):
            """
            Method recursively implements a depth first generator for nodes of
            the tree. The given node defines which subtree is used for traversal.

            :param root: Where to start node traversal
            :return: Depth first node generator
            """
            yield root
            try:
                for child in root.children():
                    for new_node in dfs(child):
                        yield new_node
                if include_marker:
                    yield EmptyNode(parent=root)
            except TypeError:
                pass
            except AttributeError:
                pass

        def wfs(root):
            """
            Method recursively implements a width first generator for nodes of
            the tree. The given node defines which subtree is used for traversal.

            :param root: Where to start node traversal
            :return: Width first node generator
            """
            to_visit = [root]
            while to_visit:
                root = to_visit.pop(0)
                yield root
                if include_marker:
                    # check if current node is the last in children
                    try:
                        if root == root.parent().children_list()[-1]:
                            yield EmptyNode(parent=root.parent())
                        if len(root.children_list()) == 0:
                            to_visit.append(EmptyNode(parent=root))
                    except AttributeError:
                        # there is no parent
                        pass
                    except IndexError:
                        pass
                try:
                    to_visit.extend(root.children_list())
                except AttributeError:
                    pass

        base_node = node or self._graph.root
        if base_node is not None:
            for node in ofs(base_node) if order_first else \
                    dfs(base_node) if depth_first else wfs(base_node):
                yield node

    @staticmethod
    def parent(node):
        """
        Method that returns the parent node of given node.
        :param node: A node inside the tree.
        :return: Parent node of node.
        """
        return node.parent()

    @staticmethod
    def node_number(node):
        """
        The node number of node with respect to its neighbouring nodes.
        :param node: A node inside the tree.
        :return: The node number of node.
        """
        return node.position

    def root(self):
        """
        Method that returns the root node of a tree. None otherwise.
        :return: Root node. None otherwise.
        """
        return self._graph.root

    @staticmethod
    def children(node):
        """
        Generator that yields children of given node.
        :param node: A node inside the tree
        :return: A generator for children of node.
        """
        return node.children()

    @staticmethod
    def children_list(node):
        """
        Returns list of children for given node.

        :param node: A node inside the tree
        :return: A list of children of node
        """
        return node.children_list()

    @staticmethod
    def child_count(node):
        """
        Method that returns the number of children for the specified node.

        :param node: A node inside the tree.
        :return: The number of children of node.
        """
        return node.child_count()

    def subtree_node_count(self, node=None):
        """
        Method that gives the number of nodes in subtree rooted at node.
        If node is not given, the node count of the complete tree is returned.

        :param node: Node where subtree is rooted.
        :return: Node count of subtree rooted at ndoe.
        """
        if node is None:
            node = self.root()
        count = 1
        for child in self.children(node):
            count += self.subtree_node_count(child)
        return count

    def tree_repr(self, node_repr=lambda node: node.name, sequence_fmt="[%s]"):
        """
        Method offers custom implementation for tree representation.

        :param node_repr: Lambda for node representation
        :param sequence_fmt: Formatter
        :return: String describing the tree
        """
        def subtree_repr(root):
            """
            Implementation to deal with subtree of a tree for output.

            :param root: Root to start subtree output
            :return: Representation of a node
            """
            children = self.children_list(root)
            if children:
                return node_repr(root) + ": " + sequence_fmt % ", ".join(
                    subtree_repr(child) for child in children
                )
            return node_repr(root)
        return sequence_fmt % (subtree_repr(self.root()))

    def __repr__(self):
        return self.__class__.__name__ + " (" + ", ".join(
            str(node) for node in self.nodes()) + ")"


class Prototype(Tree):
    """
    Subclass of a tree that represents a prototype (class for convenience only).
    """
    @staticmethod
    def from_tree(tree):
        result = Prototype()
        object_cache = ObjectCache()
        for node, _ in tree.walkDFS():
            try:
                parent = object_cache.get_data(
                    value=node.value.tme,
                    key=node.value.ppid,
                    validate_range=True
                )
            except DataNotInCacheException:
                parent = None
            process = result.add_node(parent=parent, **vars(node.value).copy())
            object_cache.add_data(process, key=process.pid, value=process.tme)
        return result

    @staticmethod
    def from_job(job):
        parent_dict = {}
        result = Prototype()
        for process in job.processes_in_order():
            try:
                parent = parent_dict.get(job.parent(process), None)
            except ObjectIsRootException:
                parent = None
            node = result.add_node(parent=parent, **vars(process).copy())
            # FIXME: also adding traffic here...
            node.traffic = process.traffic
            parent_dict[process] = node
        return result

    def to_index(self, signature, cache=None, statistics_cls=None, supported=None):
        if supported is None:
            supported = {
                ProcessStartEvent: True,
                ProcessExitEvent: True,
                TrafficEvent: False,
                ParameterEvent: False
            }
        if cache is None:
            if isinstance(signature, EnsembleSignature):
                cache = EnsembleSignatureCache(supported, statistics_cls=statistics_cls)
            else:
                cache = SignatureCache(supported, statistics_cls=statistics_cls)
        return self.to_prototype(
            signature=signature,
            cache=cache,
            statistics_cls=statistics_cls,
            _is_prototype=False,
            supported=supported
        )

    def to_prototype(self, signature: Signature, cache=None, statistics_cls=None,
                     _is_prototype=True, supported=None) -> SignatureCache:
        if supported is None:
            supported = {
                ProcessStartEvent: True,
                ProcessExitEvent: True,
                TrafficEvent: False,
                ParameterEvent: False
            }
        if cache is None:
            cache = PrototypeSignatureCache(supported, statistics_cls=statistics_cls)
        if _is_prototype:
            add_signature = self._handle_prototype_ensemble_signature_list
        else:
            add_signature = self._handle_ensemble_signature_list
        # FIXME: I should care about EmptyProcessEvent
        cache.supported[EmptyProcessEvent] = True
        for event in self.event_iter(include_marker=True, supported=supported):
            if isinstance(event.node, EmptyNode):
                current_signature = signature.finish_node(event.node.parent())
                for ensemble_signature in current_signature:
                    # FIXME: turn into ExitEvent
                    add_signature(event, ensemble_signature, cache, supported)
                continue
            else:
                current_signature = signature.get_signature(
                    event.node, event.node.parent())
            add_signature(event, current_signature, cache, supported)
        del cache.supported[EmptyProcessEvent]
        return cache

    def _handle_ensemble_signature_list(
            self, event, ensemble_signature_list, cache, supported):
        if type(event) == EmptyProcessEvent:
            if supported.get(ProcessStartEvent, False):
                cache[ensemble_signature_list, ProcessStartEvent] = {
                    "value": 0
                }
            if supported.get(ProcessExitEvent, False):
                cache[ensemble_signature_list, ProcessExitEvent] = {
                    "value": 0
                }
        else:
            cache[ensemble_signature_list, type(event)] = {
                "value": event.value
            }

    def _handle_prototype_ensemble_signature_list(
            self, event, ensemble_signature_list, cache, supported):
        if type(event) == EmptyProcessEvent:
            # EmptyProcessEvent means, that we are appending some dummy nodes.
            # Those apparently have Start and Exit events, so add it
            if supported.get(ProcessStartEvent, False):
                cache[ensemble_signature_list, self, ProcessStartEvent] = {
                    "value": 0
                }
            if supported.get(ProcessExitEvent, False):
                cache[ensemble_signature_list, self, ProcessExitEvent] = {
                    "value": 0
                }
        else:
            cache[ensemble_signature_list, self, type(event)] = {
                "value": event.value
            }

    def event_iter(self, include_marker=True, supported=None):
        exit_event_queue = deque()  # (tme, -#events, event); leftmost popped FIRST
        event_count = 0

        for node in self.node_iter(include_marker=include_marker):
            try:
                now = node.tme
            except AttributeError:
                # EmptyNode Event only needs to be forwarded
                event = EmptyProcessEvent()
                event.node = node
                yield event
                continue

            # yield any exit events that should have happened so far
            while exit_event_queue and exit_event_queue[0][0] < now:
                yield exit_event_queue.popleft()[2]

            existing_parameter_nodes = {}
            for event in Event.events_from_node(node, supported=supported):
                event_count += 1
                if isinstance(event, ProcessStartEvent):
                    event.node = node
                    yield event
                    continue
                elif isinstance(event, ProcessExitEvent):
                    event.node = node
                else:
                    try:
                        current_node = existing_parameter_nodes[event.name]
                    except KeyError:
                        existing_parameter_nodes[event.name] = OrderedTreeNode(
                            1, **event.__dict__)
                        current_node = existing_parameter_nodes[event.name]
                        current_node._parent = node
                    event.node = current_node
                    if event.tme <= now:
                        yield event
                        continue
                try:
                    bisect.insort_right(
                        exit_event_queue, (event.tme, -event_count, event))
                except AttributeError:
                    pass
        while exit_event_queue:
            yield exit_event_queue.popleft()[2]

    def node_iter(self, include_marker=False):
        return self.nodes(order_first=True, include_marker=include_marker)

    def __iter__(self):
        return self.node_iter()

    def __repr__(self):
        return "%s (%s)" % (self.__class__.__name__, self.node_count())


class EmptyNode(object):
    __slots__ = "_parent"

    def __init__(self, parent):
        self._parent = parent

    def parent(self):
        return self._parent
