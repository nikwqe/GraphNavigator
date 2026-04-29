"""
Dijkstra's algorithm for shortest path in weighted graphs.
"""

import heapq
from models.base_graph import Graph


def dijkstra(graph: Graph, start_id: str, end_id: str) -> tuple[list[str] | None, float]:
    """
    Find the shortest path between two nodes using Dijkstra's algorithm.
    Works correctly only on graphs with non-negative edge weights.

    Args:
        graph:    A Graph instance (best used with WeightedGraph).
        start_id: Starting node id.
        end_id:   Target node id.

    Returns:
        A tuple (path, total_distance) where:
          - path is a list of node ids from start to end, or None if unreachable.
          - total_distance is the sum of edge weights along the path,
            or float('inf') if unreachable.

    Raises:
        KeyError: If start_id or end_id are not present in the graph.
    """
    if not graph.has_node(start_id):
        raise KeyError(f"Start node '{start_id}' not found.")
    if not graph.has_node(end_id):
        raise KeyError(f"End node '{end_id}' not found.")

    if start_id == end_id:
        return [start_id], 0.0

    # dist[node] = best known distance from start
    dist: dict[str, float] = {nid: float("inf") for nid in graph.nodes}
    dist[start_id] = 0.0
    parent: dict[str, str | None] = {start_id: None}

    # Min-heap: (distance, node_id)
    heap: list[tuple[float, str]] = [(0.0, start_id)]

    while heap:
        current_dist, current = heapq.heappop(heap)

        if current_dist > dist[current]:
            continue  # stale entry

        if current == end_id:
            path = _reconstruct_path(parent, end_id)
            return path, dist[end_id]

        for neighbor in graph.neighbors(current):
            weight = graph.get_weight(current, neighbor)
            new_dist = dist[current] + weight
            if new_dist < dist[neighbor]:
                dist[neighbor] = new_dist
                parent[neighbor] = current
                heapq.heappush(heap, (new_dist, neighbor))

    return None, float("inf")  # end_id unreachable


def dijkstra_all(graph: Graph, start_id: str) -> dict[str, tuple[list[str] | None, float]]:
    """
    Run Dijkstra from start_id to every other reachable node.

    Returns:
        Dict mapping node_id → (path, distance).
    """
    if not graph.has_node(start_id):
        raise KeyError(f"Start node '{start_id}' not found.")

    dist: dict[str, float] = {nid: float("inf") for nid in graph.nodes}
    dist[start_id] = 0.0
    parent: dict[str, str | None] = {start_id: None}
    heap: list[tuple[float, str]] = [(0.0, start_id)]

    while heap:
        current_dist, current = heapq.heappop(heap)
        if current_dist > dist[current]:
            continue
        for neighbor in graph.neighbors(current):
            weight = graph.get_weight(current, neighbor)
            new_dist = dist[current] + weight
            if new_dist < dist[neighbor]:
                dist[neighbor] = new_dist
                parent[neighbor] = current
                heapq.heappush(heap, (new_dist, neighbor))

    result = {}
    for node_id in graph.nodes:
        if node_id == start_id:
            result[node_id] = ([start_id], 0.0)
        elif dist[node_id] < float("inf"):
            result[node_id] = (_reconstruct_path(parent, node_id), dist[node_id])
        else:
            result[node_id] = (None, float("inf"))
    return result


# ─── Internal helper ──────────────────────────────────────────────────────────

def _reconstruct_path(parent: dict, end_id: str) -> list[str]:
    path = []
    current = end_id
    while current is not None:
        path.append(current)
        current = parent[current]
    return list(reversed(path))
