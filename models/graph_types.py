"""
Concrete graph implementations: DirectedGraph, UndirectedGraph, WeightedGraph.
"""

from models.base_graph import Graph


class DirectedGraph(Graph):
    """
    Directed graph (digraph): edges have direction (A → B ≠ B → A).
    All edges have an implicit weight of 1.0.
    """

    def add_edge(self, from_id: str, to_id: str, weight: float = 1.0) -> None:
        self._require_nodes(from_id, to_id)
        if self.has_edge(from_id, to_id):
            raise ValueError(f"Edge '{from_id}' -> '{to_id}' already exists.")
        self._adjacency[from_id][to_id] = 1.0  # weight ignored for unweighted

    def remove_edge(self, from_id: str, to_id: str) -> None:
        self._require_nodes(from_id, to_id)
        if not self.has_edge(from_id, to_id):
            raise KeyError(f"Edge '{from_id}' -> '{to_id}' not found.")
        del self._adjacency[from_id][to_id]


class UndirectedGraph(Graph):
    """
    Undirected graph: edges are symmetric (A — B implies B — A).
    All edges have an implicit weight of 1.0.
    """

    def add_edge(self, from_id: str, to_id: str, weight: float = 1.0) -> None:
        self._require_nodes(from_id, to_id)
        if self.has_edge(from_id, to_id):
            raise ValueError(f"Edge between '{from_id}' and '{to_id}' already exists.")
        self._adjacency[from_id][to_id] = 1.0
        self._adjacency[to_id][from_id] = 1.0

    def remove_edge(self, from_id: str, to_id: str) -> None:
        self._require_nodes(from_id, to_id)
        if not self.has_edge(from_id, to_id):
            raise KeyError(f"Edge between '{from_id}' and '{to_id}' not found.")
        del self._adjacency[from_id][to_id]
        self._adjacency[to_id].pop(from_id, None)

    def to_dict(self) -> dict:
        """Override to avoid serializing duplicate edges."""
        seen = set()
        edges = []
        for from_id, neighbors in self._adjacency.items():
            for to_id, weight in neighbors.items():
                key = tuple(sorted([from_id, to_id]))
                if key not in seen:
                    seen.add(key)
                    edges.append({"from": from_id, "to": to_id, "weight": weight})
        return {
            "graph_type": self.graph_type,
            "nodes": [n.to_dict() for n in self._nodes.values()],
            "edges": edges,
        }


class WeightedGraph(Graph):
    """
    Weighted directed graph: edges have direction and custom non-negative weights.
    Used with Dijkstra's shortest path algorithm.
    """

    def add_edge(self, from_id: str, to_id: str, weight: float = 1.0) -> None:
        self._require_nodes(from_id, to_id)
        self._validate_weight(weight)
        if self.has_edge(from_id, to_id):
            raise ValueError(f"Edge '{from_id}' -> '{to_id}' already exists.")
        self._adjacency[from_id][to_id] = float(weight)

    def remove_edge(self, from_id: str, to_id: str) -> None:
        self._require_nodes(from_id, to_id)
        if not self.has_edge(from_id, to_id):
            raise KeyError(f"Edge '{from_id}' -> '{to_id}' not found.")
        del self._adjacency[from_id][to_id]

    def update_weight(self, from_id: str, to_id: str, new_weight: float) -> None:
        """Update the weight of an existing edge."""
        self._require_nodes(from_id, to_id)
        self._validate_weight(new_weight)
        if not self.has_edge(from_id, to_id):
            raise KeyError(f"Edge '{from_id}' -> '{to_id}' not found.")
        self._adjacency[from_id][to_id] = float(new_weight)
