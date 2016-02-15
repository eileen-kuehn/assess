import networkx as nx


class Process(object):
    def __init__(self, prototype, node_id, **kwargs):
        self._prototype = prototype
        self.node_id = node_id
        for key in kwargs.keys():
            self.__setattr__(key, kwargs[key])

    def depth(self):
        depth = 0
        node = self
        while self._prototype.parent(node) is not None:
            depth += 1
            # update node
            node = self._prototype.parent(node)
        return depth

    def parent(self):
        return self._prototype.parent(self)

    def children(self):
        for child in self._prototype.children(self):
            yield child

    def child_count(self):
        return self._prototype.child_count(self)

    def __repr__(self):
        return self.__class__.__name__ + " (" + ', '.join('%s=%s'%(arg, self.__getattribute__(arg)) for arg in vars(self)) + ")"


class Tree(object):
    def __init__(self):
        self._graph = nx.DiGraph()

    def add_node(self, name, parent=None, **kwargs):
        #node_id = self._unique_name(name, parent)
        node_id = nx.utils.generate_unique_node()
        node = Process(self, node_id, name=name, **kwargs)
        self._graph.add_node(
            node_id,
            data=node
        )
        if parent is not None:
            self._graph.add_edge(
                parent.node_id,
                node_id,
                weight=0.5
            )
        return node

    def node_with_node_id(self, node_id):
        return self._graph.node[node_id]["data"]

    def node_count(self):
        return len(self._graph.nodes())

    def nodes(self, depth_first=True):
        def depth_first(root):
            if root is None:
                root = self.root()
            yield root
            try:
                for child in root.children():
                    for new_node in depth_first(child):
                        yield new_node
            except TypeError:
                pass

        def width_first(root):
            if root is None:
                root = self.root()
                toVisit = [root]
                while len(toVisit) > 0:
                    root = toVisit.pop(0)
                    yield root
                    for child in root.children():
                        toVisit.append(child)

        for node in (depth_first(self.root()) if depth_first(self.root()) else width_first(self.root())):
            yield node

    # TODO: this should just be one parent, not list of parents
    def parent(self, node):
        result = []
        for node_id in self._graph.predecessors(node.node_id):
            result.append(self.node_with_node_id(node_id))
        return result[0] if len(result) > 0 else None

    def root(self):
        try:
            root = self._graph.node[self._graph.nodes()[0]]["data"]
        except:
            return None
        else:
            if root.parent() is None:
                return root
            print("this shouldn't happen...")
            return None

    def children(self, node):
        for node_id in self._graph.successors(node.node_id):
            yield self.node_with_node_id(node_id)

    def child_count(self, node):
        return len(self._graph.successors(node.node_id))

    def subtree_node_count(self, node):
        count = 1
        if self.child_count(node) > 0:
            for child in self.children(node):
                count += self.subtree_node_count(child)
        return count

    def _unique_name(self, name, parent):
        return "%s_%d_%X" % (
            name,
            parent.depth() + 1 if parent is not None else 0,
            hash(parent.node_id) if parent is not None else hash(name)
        )

    @staticmethod
    def unique_name(name, depth, parent_info):
        return "%s_%d_%X" % (
            name,
            depth,
            hash(parent_info)
        )

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


def prototype_one():
    T = Prototype()
    # create nodes
    root_node = T.add_node(
            "root",
            n=1, n_err=0,
            t=1, t_err=0,
            m={
                "v_i": 0,
                "v_o": 0
            }
    )
    ls_node = T.add_node(
            "ls",
            parent=root_node,
            n=1, n_err=0,
            t=1, t_err=0,
            m={
                "v_i": 0,
                "v_o": 0
            }
    )
    T.add_node(
            "wget",
            parent=root_node,
            n=1, n_err=0,
            t=1, t_err=0,
            m={
                "v_i": 0,
                "v_o": 0
            }
    )
    T.add_node(
            "mv",
            parent=ls_node,
            n=1, n_err=0,
            t=1, t_err=0,
            m={
                "v_i": 0,
                "v_o": 0
            }
    )
    T.add_node(
            "rm",
            parent=ls_node,
            n=1, n_err=0,
            t=1, t_err=0,
            m={
                "v_i": 0,
                "v_o": 0
            }
    )
    # return prototype
    return T

def prototype_two():
    T = Prototype()
    # create nodes
    root_node = T.add_node(
            "root",
            n=1, n_err=0,
            t=1, t_err=0,
            m={
                "v_i": 0,
                "v_o": 0
            }
    )
    ls_node = T.add_node(
            "ls",
            parent=root_node,
            n=1, n_err=0,
            t=1, t_err=0,
            m={
                "v_i": 0,
                "v_o": 0
            }
    )
    T.add_node(
            "rm",
            parent=root_node,
            n=1, n_err=0,
            t=1, t_err=0,
            m={
                "v_i": 0,
                "v_o": 0
            }
    )
    T.add_node(
            "mv",
            parent=ls_node,
            n=1, n_err=0,
            t=1, t_err=0,
            m={
                "v_i": 0,
                "v_o": 0
            }
    )
    T.add_node(
            "rm",
            parent=ls_node,
            n=1, n_err=0,
            t=1, t_err=0,
            m={
                "v_i": 0,
                "v_o": 0
            }
    )
    # return prototype
    return T
