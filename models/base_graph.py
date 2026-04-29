"""
Base Graph class - abstract foundation for all graph types.
"""

from abc import ABC, abstractmethod
from models.graph_node import GraphNode


class Graph(ABC):
    """
    Abstract base class for all graph types.
    Provides common node/edge management with enforced interface for subclasses.
    """

    def __init__(self):
        # node_id -> GraphNode
        self._nodes: dict[str, GraphNode] = {}
        # adjacency: node_id -> {neighbor_id: weight}
        self._adjacency: dict[str, dict[str, float]] = {}

    # ─── Node operations ──────────────────────────────────────────────────────

    def add_node(self, node_id: str, data: dict = None) -> GraphNode:
        """Add a node. Raises ValueError if already present."""
        if node_id in self._nodes:
            raise ValueError(f"Node '{node_id}' already exists.")
        node = GraphNode(node_id, data)
        self._nodes[node_id] = node
        self._adjacency[node_id] = {}
        return node

    def remove_node(self, node_id: str) -> None:
        """Remove a node and all its edges. Raises KeyError if not found."""
        if node_id not in self._nodes:
            raise KeyError(f"Node '{node_id}' not found.")
        del self._nodes[node_id]
        del self._adjacency[node_id]
        # Remove all incoming edges
        for neighbors in self._adjacency.values():
            neighbors.pop(node_id, None)

    def get_node(self, node_id: str) -> GraphNode:
        """Return a node by id. Raises KeyError if not found."""
        if node_id not in self._nodes:
            raise KeyError(f"Node '{node_id}' not found.")
        return self._nodes[node_id]

    def has_node(self, node_id: str) -> bool:
        return node_id in self._nodes

    # ─── Edge operations ──────────────────────────────────────────────────────

    @abstractmethod
    def add_edge(self, from_id: str, to_id: str, weight: float = 1.0) -> None:
        """Add an edge. Implementation differs per graph type."""
        pass

    @abstractmethod
    def remove_edge(self, from_id: str, to_id: str) -> None:
        """Remove an edge."""
        pass

    def has_edge(self, from_id: str, to_id: str) -> bool:
        return from_id in self._adjacency and to_id in self._adjacency[from_id]

    def get_weight(self, from_id: str, to_id: str) -> float:
        """Return edge weight. Raises KeyError if edge not found."""
        if not self.has_edge(from_id, to_id):
            raise KeyError(f"Edge '{from_id}' -> '{to_id}' not found.")
        return self._adjacency[from_id][to_id]

    def neighbors(self, node_id: str) -> list[str]:
        """Return list of neighbor ids for a given node."""
        if node_id not in self._adjacency:
            raise KeyError(f"Node '{node_id}' not found.")
        return list(self._adjacency[node_id].keys())

    # ─── Properties ───────────────────────────────────────────────────────────

    @property
    def nodes(self) -> list[str]:
        return list(self._nodes.keys())

    @property
    def node_count(self) -> int:
        return len(self._nodes)

    @property
    def graph_type(self) -> str:
        return self.__class__.__name__

    # ─── Validation helpers ───────────────────────────────────────────────────

    def _validate_weight(self, weight: float) -> None:
        if not isinstance(weight, (int, float)):
            raise TypeError("Weight must be a number.")
        if weight < 0:
            raise ValueError("Weight must be non-negative.")

    def _require_nodes(self, *node_ids: str) -> None:
        for nid in node_ids:
            if nid not in self._nodes:
                raise KeyError(f"Node '{nid}' not found.")

    # ─── Serialization ────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        """Serialize the entire graph to a dictionary."""
        return {
            "graph_type": self.graph_type,
            "nodes": [n.to_dict() for n in self._nodes.values()],
            "edges": [
                {"from": from_id, "to": to_id, "weight": weight}
                for from_id, neighbors in self._adjacency.items()
                for to_id, weight in neighbors.items()
            ],
        }

    def __repr__(self) -> str:
        return (
            f"{self.graph_type}("
            f"nodes={self.node_count}, "
            f"edges={sum(len(v) for v in self._adjacency.values())})"
        )
