"""
GraphFactory - Factory pattern for creating graph instances by type string.
"""

from models.base_graph import Graph
from models.graph_types import DirectedGraph, UndirectedGraph, WeightedGraph


class GraphFactory:
    """
    Factory for creating graph objects.

    Supported types (case-insensitive):
        - "directed"    → DirectedGraph
        - "undirected"  → UndirectedGraph
        - "weighted"    → WeightedGraph
    """

    _REGISTRY: dict[str, type] = {
        "directed": DirectedGraph,
        "undirected": UndirectedGraph,
        "weighted": WeightedGraph,
    }

    @classmethod
    def create(cls, graph_type: str) -> Graph:
        """
        Create and return a new empty graph of the given type.

        Args:
            graph_type: One of 'directed', 'undirected', 'weighted'.

        Returns:
            A fresh Graph instance.

        Raises:
            ValueError: If graph_type is unknown.
        """
        key = graph_type.strip().lower()
        if key not in cls._REGISTRY:
            available = ", ".join(cls._REGISTRY.keys())
            raise ValueError(
                f"Unknown graph type '{graph_type}'. "
                f"Available types: {available}."
            )
        return cls._REGISTRY[key]()

    @classmethod
    def from_dict(cls, data: dict) -> Graph:
        """
        Reconstruct a graph from a serialized dictionary (loaded from JSON).

        Args:
            data: Dict with keys 'graph_type', 'nodes', 'edges'.

        Returns:
            A populated Graph instance.
        """
        raw_type = data.get("graph_type", "")
        # Map class name → factory key
        type_map = {
            "DirectedGraph": "directed",
            "UndirectedGraph": "undirected",
            "WeightedGraph": "weighted",
        }
        factory_key = type_map.get(raw_type, raw_type.lower())
        graph = cls.create(factory_key)

        for node_data in data.get("nodes", []):
            graph.add_node(node_data["node_id"], node_data.get("data", {}))

        for edge_data in data.get("edges", []):
            graph.add_edge(
                edge_data["from"],
                edge_data["to"],
                edge_data.get("weight", 1.0),
            )

        return graph

    @classmethod
    def available_types(cls) -> list[str]:
        return list(cls._REGISTRY.keys())
