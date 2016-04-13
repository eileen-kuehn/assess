from assess.exceptions.exceptions import TreeInvalidatedException


class OrderedTreeNode(object):
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
        count = 0
        node = self
        while node.parent():
            count += 1
            node = node.parent()
        return count

    def children(self):
        return self._children

    def children_list(self):
        return self._children

    def child_count(self):
        return len(self._children)

    def node_count(self):
        count = 1
        for child in self._children:
            count += child.node_count()
        return count

    def node_number(self):
        return self.position

    def parent(self):
        return self._parent

    def add_node(self, name=None, **kwargs):
        return self._prototype.add_node(name=name, parent=self, **kwargs)

    #def __repr__(self):
    #    return self.__class__.__name__ + " (" + ', '.join('%s=%s'%(arg, self.__getattribute__(arg)) for arg in vars(self)) + ")"


class OrderedTree(object):
    def __init__(self):
        self.root = None
        self._node_counter = 0

    def _unique_node_id(self):
        # nx.utils.generate_unique_node()
        return str(self.node_count())

    def node_count(self):
        return self._node_counter

    def add_node(self, name=None, parent=None, **kwargs):
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
            parent._children.append(node)
        self._node_counter += 1
        return node


class Process(object):
    # TODO: can this be exchanged by process from gnmutils? or extended?
    """
    A process represents the actual node inside the process tree.
    """
    def __init__(self, prototype, node_id, **kwargs):
        self._prototype = prototype
        self.node_id = node_id
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
        return self.__class__.__name__ + " (" + ', '.join('%s=%s'%(arg, self.__getattribute__(arg)) for arg in vars(self)) + ")"


class Tree(object):
    def __init__(self):
        self._graph = OrderedTree()

    def add_node(self, name, parent=None, **kwargs):
        if parent is None and self.root() is not None:
            raise TreeInvalidatedException
        return self._graph.add_node(name=name, parent=parent, **kwargs)

    def node_count(self):
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
            to_visit = [root]
            while to_visit:
                root = to_visit.pop(0)
                yield root
                for child in root.children():
                    to_visit.append(child)

        root = self._graph.root
        if root is not None:
            for node in (dfs(root) if depth_first else wfs(root)):
                yield node

    def parent(self, node):
        """
        Method that returns the parent node of given node.
        :param node: A node inside the tree.
        :return: Parent node of node.
        """
        return node.parent()

    def node_number(self, node):
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

    def children(self, node):
        """
        Generator that yields children of given node.
        :param node: A node inside the tree.
        :return: A generator for children of node.
        """
        for child in node.children():
            yield child

    def children_list(self, node):
        return node.children()

    def child_count(self, node):
        """
        Method that returns the number of children for the specified node.
        :param node: A node inside the tree.
        :return: The number of children of node.
        """
        # TODO: can be refactored by counting number of edges
        return len(node.children())

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
        def subtree_repr(root):
            children = list(self.children(root))
            if children:
                return node_repr(root) + ": " + sequence_fmt % ", ".join(subtree_repr(child) for child in children)
            return node_repr(root)
        return sequence_fmt % (subtree_repr(self.root()))

    def __repr__(self):
        return self.__class__.__name__ + " (" + ", ".join(str(node) for node in self.nodes()) + ")"


class Prototype(Tree):
    pass
