"""
Module describes a general tree as well as a more specialised prototype. Also the definition for
the single nodes is defined.
"""
from assess.exceptions.exceptions import TreeInvalidatedException


class OrderedTreeNode(object):
    """
    Class describes a node of a tree that ensures the correct order of nodes within the tree.

    :param node_id: ID of node
    :param name: Name of node
    :param parent: Parent node of node
    :param position: Position of node within siblings
    :param tree: Tree where node belongs to
    :param kwargs: Additional arguments
    """
    def __init__(self, node_id, name=None, parent=None, position=0, tree=None, **kwargs):
        self.node_id = node_id
        self.name = name
        self._parent = parent
        self._children = []
        self._prototype = tree
        self.position = position
        for key, value in kwargs.items():
            setattr(self, key, value)

    def depth(self):
        """
        Method returns the depth of the current node within the tree. If the node is the root, then
        0 is returned. So depth equals the number of parents.

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
        Method returns the position of the node regarding its siblings. If the node is the first
        element, 0 is returned.

        :return: Node position
        """
        return self.position

    def parent(self):
        """
        Method returns the parent of the node, if it does not have a parent, it returns None.

        :return: Parent, None otherwise
        """
        return self._parent

    def add_node(self, name=None, **kwargs):
        """
        Method to add a new node to the list of children of the node. It is appended to the end
        of the children's list.

        :param name: Name of the new node to add
        :param kwargs: Params to be added to the node
        :return: Reference to new created node
        """
        return self._prototype.add_node(name=name, parent=self, **kwargs)

    #def __repr__(self):
    #    return self.__class__.__name__ + " (" + ', '.join('%s=%s'%(arg, self.__getattribute__(arg))
    #                                                      for arg in vars(self)) + ")"


class OrderedTree(object):
    """
    Class that builds up a tree that takes care of the order of nodes, so it does implement an
    ordered tree.
    """
    def __init__(self):
        self.root = None
        self._node_counter = 0

    def _unique_node_id(self):
        """
        Method returns a unique id.

        :return: Unique id
        """
        # nx.utils.generate_unique_node()
        return str(self.node_count())

    def node_count(self):
        """
        Returns the current count of nodes within the tree.

        :return: Current count of nodes
        """
        return self._node_counter

    def add_node(self, name=None, parent=None, **kwargs):
        """
        Method adds a new node to the actual tree. If parent is not given, the node gets the root
        ndoe of the tree.

        :param name: Name of the node to create
        :param parent: Parent of the node to attach to
        :param kwargs: Additional parameters of the node
        :return: Reference to the created node
        """
        node = OrderedTreeNode(
            node_id=self._unique_node_id(),
            name=name,
            parent=parent,
            tree=self,
            position=parent.child_count() if parent is not None else 0,
            **kwargs
        )
        if self.root is None:
            self.root = node
        else:
            parent.children_list().append(node)
        self._node_counter += 1
        return node


class Process(object):
    # TODO: can this be exchanged by process from gnmutils? or extended?
    """
    A process represents the actual node inside the process tree.

    :param prototype: Prototype the process belongs to
    :param node_id: ID of process
    :param kwargs: Additional parameters
    """
    def __init__(self, prototype, node_id, **kwargs):
        self._prototype = prototype
        self.node_id = node_id
        self.pid = 0
        for key in kwargs.keys():
            self.__setattr__(key, kwargs[key])

    def add_child(self, name, **kwargs):
        """
        Method to add a child node to the current node.

        :param name: The name of the new process.
        :param kwargs: Additional parameters.
        :return: The newly created node.
        """
        # TODO: ensure not to overwrite given pid and ppid
        ppid = self.pid
        pid = self._prototype.node_count() + 1
        position = self.child_count()
        return self._prototype.add_node(name, self, pid=pid, ppid=ppid, position=position, **kwargs)

    def depth(self):
        """
        Returns the depth of the node. The root node has depth 0.
        :return: Depth of the node.
        """
        depth = 0
        node = self
        while node.parent() is not None:
            depth += 1
            # update node
            node = node.parent()
        return depth

    def parent(self):
        """
        Returns the parent node of the current node.
        :return: Parent.
        """
        return self._prototype.parent(self)

    def children(self):
        """
        Generator for children of the current node.
        :return: Generator for children of node.
        """
        return self._prototype.children(self)

    def node_number(self):
        """
        Returns number in relation to its neighbouring nodes. First means number 0.
        :return: Number between neighbouring nodes.
        """
        return self._prototype.node_number(self)

    def child_count(self):
        """
        Returns the count of children from current node.
        :return: Child count.
        """
        return self._prototype.child_count(self)

    def __repr__(self):
        return self.__class__.__name__ + " (" + ', '.join('%s=%s'%(arg, self.__getattribute__(arg))
                                                          for arg in vars(self)) + ")"


class Tree(object):
    """
    Class that represents a tree with no ensured ordering of nodes.
    """
    def __init__(self):
        self._graph = OrderedTree()

    def add_node(self, name, parent=None, **kwargs):
        """
        Method to add a new node to the tree. If given parent is None, and there is currently no
        root, then the node becomes the root of the tree.

        :param name: Name of the node to be created
        :param parent: Parent where to attach the node
        :param kwargs: Additional attribute of the node
        :return: Reference to the newly created node
        """
        if parent is None and self.root() is not None:
            raise TreeInvalidatedException
        return self._graph.add_node(name=name, parent=parent, **kwargs)

    def node_count(self):
        """
        Method returns the current count of nodes within the tree.

        :return: Count of nodes
        """
        return self._graph.node_count()

    # TODO: implement stop condition for depth and width first
    def nodes(self, depth_first=True):
        """
        Method that returns a generator yielding all nodes inside the tree, either in
        depth first or width first order.
        :param depth_first: Depth first order if True, otherwise width first.
        :return: Generator for tree nodes.
        """
        def dfs(root):
            """
            Method recursively implements a depth first generator for nodes of the tree.
            The given node defines which subtree is used for traversal.

            :param root: Where to start node traversal
            :return: Depth first node generator
            """
            yield root
            try:
                for child in root.children():
                    for new_node in dfs(child):
                        yield new_node
            except TypeError:
                pass
            except AttributeError:
                pass

        def wfs(root):
            """
            Method recursively implements a width first gneerator for nodes of the tree.
            The given node defines which subtree is used for traversal.

            :param root: Where to start node traversal
            :return: Width first node generator
            """
            to_visit = [root]
            while to_visit:
                root = to_visit.pop(0)
                yield root
                for child in root.children():
                    to_visit.append(child)

        base_node = self._graph.root
        if base_node is not None:
            for node in dfs(base_node) if depth_first else wfs(base_node):
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

    def subtree_node_count(self, node):
        """
        Method that gives the number of nodes in subtree rooted at node. If node is not given,
        the node count of the complete tree is returned.
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
        return self.__class__.__name__ + " (" + ", ".join(str(node) for node in self.nodes()) + ")"


class Prototype(Tree):
    """
    Subclass of a tree that represents a prototype (class for convenience only).
    """
    pass
