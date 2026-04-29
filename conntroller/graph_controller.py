"""
GraphController - MVC Controller layer.
Bridges user commands (View) with graph data (Model).
All validation of business rules lives here.
"""

from models.base_graph import Graph
from models.graph_factory import GraphFactory
from models.graph_types import WeightedGraph, UndirectedGraph
from algorithms.traversal import bfs, dfs, bfs_path
from algorithms.dijkstra import dijkstra
from storage.graph_storage import GraphStorage


class GraphController:
    """
    Controller in the MVC pattern.

    Holds the active graph and exposes high-level operations that the
    console View can call without touching model internals directly.
    """

    def __init__(self, storage_dir: str = "saved_graphs"):
        self._graph: Graph | None = None
        self._storage = GraphStorage(storage_dir)

    # ─── Graph lifecycle ──────────────────────────────────────────────────────

    def create_graph(self, graph_type: str) -> str:
        """Create a new empty graph, replacing any existing one."""
        self._graph = GraphFactory.create(graph_type)
        return f"Created new {self._graph.graph_type}."

    def current_graph_info(self) -> str:
        """Return a short summary string about the active graph."""
        g = self._require_graph()
        return (
            f"Type : {g.graph_type}\n"
            f"Nodes: {g.node_count}  →  {', '.join(sorted(g.nodes)) or '(none)'}\n"
            f"Edges: {self._edge_count(g)}"
        )

    # ─── Node operations ──────────────────────────────────────────────────────

    def add_node(self, node_id: str, **kwargs) -> str:
        g = self._require_graph()
        data = {k: v for k, v in kwargs.items() if v is not None}
        g.add_node(node_id, data or None)
        return f"Node '{node_id}' added."

    def remove_node(self, node_id: str) -> str:
        g = self._require_graph()
        g.remove_node(node_id)
        return f"Node '{node_id}' removed."

    def list_nodes(self) -> list[str]:
        return sorted(self._require_graph().nodes)

    # ─── Edge operations ──────────────────────────────────────────────────────

    def add_edge(self, from_id: str, to_id: str, weight: float = 1.0) -> str:
        g = self._require_graph()
        g.add_edge(from_id, to_id, weight)
        weight_str = f" (weight={weight})" if isinstance(g, WeightedGraph) else ""
        arrow = "—" if isinstance(g, UndirectedGraph) else "→"
        return f"Edge '{from_id}' {arrow} '{to_id}'{weight_str} added."

    def remove_edge(self, from_id: str, to_id: str) -> str:
        g = self._require_graph()
        g.remove_edge(from_id, to_id)
        return f"Edge '{from_id}' → '{to_id}' removed."

    def list_edges(self) -> list[str]:
        g = self._require_graph()
        lines = []
        seen = set()
        is_undirected = isinstance(g, UndirectedGraph)
        for from_id in sorted(g.nodes):
            for to_id in sorted(g.neighbors(from_id)):
                key = tuple(sorted([from_id, to_id])) if is_undirected else (from_id, to_id)
                if key in seen:
                    continue
                seen.add(key)
                w = g.get_weight(from_id, to_id)
                arrow = "—" if is_undirected else "→"
                weight_str = f"  [w={w}]" if isinstance(g, WeightedGraph) else ""
                lines.append(f"  {from_id} {arrow} {to_id}{weight_str}")
        return lines

    # ─── Algorithms ───────────────────────────────────────────────────────────

    def run_bfs(self, start_id: str) -> str:
        g = self._require_graph()
        result = bfs(g, start_id)
        return "BFS order: " + " → ".join(result)

    def run_dfs(self, start_id: str) -> str:
        g = self._require_graph()
        result = dfs(g, start_id)
        return "DFS order: " + " → ".join(result)

    def find_shortest_path(self, from_id: str, to_id: str) -> str:
        g = self._require_graph()
        if isinstance(g, WeightedGraph):
            path, dist = dijkstra(g, from_id, to_id)
            if path is None:
                return f"No path from '{from_id}' to '{to_id}'."
            return (
                f"Dijkstra shortest path: {' → '.join(path)}\n"
                f"Total distance: {dist}"
            )
        else:
            path = bfs_path(g, from_id, to_id)
            if path is None:
                return f"No path from '{from_id}' to '{to_id}'."
            return (
                f"BFS shortest path: {' → '.join(path)}\n"
                f"Hops: {len(path) - 1}"
            )

    def show_neighbors(self, node_id: str) -> str:
        g = self._require_graph()
        nb = sorted(g.neighbors(node_id))
        if not nb:
            return f"Node '{node_id}' has no outgoing neighbors."
        return f"Neighbors of '{node_id}': {', '.join(nb)}"

    # ─── Persistence ──────────────────────────────────────────────────────────

    def save_graph(self, filename: str) -> str:
        g = self._require_graph()
        path = self._storage.save(g, filename)
        return f"Graph saved to '{path}'."

    def load_graph(self, filename: str) -> str:
        self._graph = self._storage.load(filename)
        return f"Graph loaded from '{filename}'. {self._graph}"

    def list_saved_graphs(self) -> list[str]:
        return self._storage.list_saved()

    def delete_saved_graph(self, filename: str) -> str:
        deleted = self._storage.delete(filename)
        return f"Deleted '{filename}'." if deleted else f"File '{filename}' not found."

    # ─── Internal helpers ─────────────────────────────────────────────────────

    def _require_graph(self) -> Graph:
        if self._graph is None:
            raise RuntimeError(
                "No active graph. Use 'new <type>' to create one first."
            )
        return self._graph

    @staticmethod
    def _edge_count(g: Graph) -> int:
        return sum(len(g.neighbors(n)) for n in g.nodes)
