import networkx as nx

from assess.exceptions.exceptions import TreeInvalidatedException


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
        for child in self._prototype.children(self):
            yield child

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
        self._graph = nx.DiGraph()

    def add_node(self, name, parent=None, **kwargs):
        node_id = nx.utils.generate_unique_node()
        node = Process(self, node_id, name=name, **kwargs)
        if parent is None and self.root() is not None:
            raise TreeInvalidatedException()
        self._graph.add_node(
            node_id,
            data=node,
            position=kwargs.get("position", parent.child_count() if parent is not None else 0)
        )
        if parent is not None:
            self._graph.add_edge(
                parent.node_id,
                node_id,
                weight=1.0
            )
        return node

    def node_with_node_id(self, node_id):
        return self._graph.node[node_id]["data"]

    def node_count(self):
        return self._graph.number_of_nodes()

    # TODO: implement stop condition for depth and width first
    def nodes(self, depth_first=True):
        """
        Method that returns a generator yielding all nodes inside the tree, either in
        depth first or width first order.
        :param depth_first: Depth first order if True, otherwise width first.
        :return: Generator for tree nodes.
        """
        def dfs(root):
            if root is None:
                root = self.root()
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
            if root is None:
                root = self.root()
            to_visit = [root]
            while len(to_visit) > 0:
                root = to_visit.pop(0)
                yield root
                for child in root.children():
                    to_visit.append(child)

        root = self.root()
        if root is not None:
            for node in (dfs(root) if depth_first else wfs(root)):
                yield node

    def parent(self, node):
        """
        Method that returns the parent node of given node.
        :param node: A node inside the tree.
        :return: Parent node of node.
        """
        result = []
        for node_id in self._graph.predecessors(node.node_id):
            result.append(self.node_with_node_id(node_id))
        assert len(result) <= 1
        return result[0] if len(result) > 0 else None

    def node_number(self, node):
        """
        The node number of node with respect to its neighbouring nodes.
        :param node: A node inside the tree.
        :return: The node number of node.
        """
        number = 0
        parent = self.parent(node)
        neighboring_nodes = list(self.children(parent)) if parent is not None else []
        for i in range(0, len(neighboring_nodes)):
            if node == neighboring_nodes[i]:
                number = i
                break
        return number

    def root(self):
        """
        Method that returns the root node of a tree. None otherwise.
        :return: Root node. None otherwise.
        """
        try:
            root = self._graph.node[self._graph.nodes()[0]]["data"]
            while root.parent() is not None:
                root = root.parent()
        except Exception as e:
            return None
        else:
            return root

    def children(self, node):
        """
        Generator that yields children of given node.
        :param node: A node inside the tree.
        :return: A generator for children of node.
        """
        for node_id in sorted(self._graph.successors(node.node_id), key=lambda nid: self._graph.node[nid]['position']):
            yield self.node_with_node_id(node_id)

    def child_count(self, node):
        """
        Method that returns the number of children for the specified node.
        :param node: A node inside the tree.
        :return: The number of children of node.
        """
        return len(list(self.children(node)))

    def subtree_node_count(self, node=None):
        """
        Method that gives the number of nodes in subtree rooted at node. If node is not given,
        the node count of the complete tree is returned.
        :param node: Node where subtree is rooted.
        :return: Node count of subtree rooted at ndoe.
        """
        if node is None:
            node = self.root()
        count = 1
        if self.child_count(node) > 0:
            for child in self.children(node):
                count += self.subtree_node_count(child)
        return count

    def tree_repr(self, node_repr=lambda node: node.name, sequence_fmt="[%s]"):
        def subtree_repr(root):
            if list(root.children()):
                return node_repr(root) + ": " + sequence_fmt % ", ".join(subtree_repr(child) for child in root.children())
            return node_repr(root)
        return sequence_fmt % (subtree_repr(self.root()))

    def __repr__(self):
        return self.__class__.__name__ + " (" + ", ".join(node for node in self._graph.nodes()) + ")"


class Prototype(Tree):
    pass
