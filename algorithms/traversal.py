"""
Traversal algorithms: BFS (Breadth-First Search) and DFS (Depth-First Search).
"""

from collections import deque
from models.base_graph import Graph


def bfs(graph: Graph, start_id: str) -> list[str]:
    """
    Breadth-First Search traversal starting from start_id.

    Returns:
        A list of node ids in the order they were visited.

    Raises:
        KeyError: If start_id is not in the graph.
    """
    if not graph.has_node(start_id):
        raise KeyError(f"Start node '{start_id}' not found in graph.")

    visited: list[str] = []
    seen: set[str] = set()
    queue: deque[str] = deque([start_id])
    seen.add(start_id)

    while queue:
        current = queue.popleft()
        visited.append(current)
        for neighbor in sorted(graph.neighbors(current)):  # sorted for determinism
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append(neighbor)

    return visited


def bfs_path(graph: Graph, start_id: str, end_id: str) -> list[str] | None:
    """
    BFS shortest path (by hop count) from start_id to end_id.

    Returns:
        List of node ids representing the path, or None if unreachable.
    """
    if not graph.has_node(start_id):
        raise KeyError(f"Start node '{start_id}' not found.")
    if not graph.has_node(end_id):
        raise KeyError(f"End node '{end_id}' not found.")

    if start_id == end_id:
        return [start_id]

    parent: dict[str, str | None] = {start_id: None}
    queue: deque[str] = deque([start_id])

    while queue:
        current = queue.popleft()
        for neighbor in graph.neighbors(current):
            if neighbor not in parent:
                parent[neighbor] = current
                if neighbor == end_id:
                    return _reconstruct_path(parent, end_id)
                queue.append(neighbor)

    return None  # no path found


def dfs(graph: Graph, start_id: str) -> list[str]:
    """
    Depth-First Search traversal (iterative) starting from start_id.

    Returns:
        A list of node ids in the order they were visited.

    Raises:
        KeyError: If start_id is not in the graph.
    """
    if not graph.has_node(start_id):
        raise KeyError(f"Start node '{start_id}' not found in graph.")

    visited: list[str] = []
    seen: set[str] = set()
    stack: list[str] = [start_id]

    while stack:
        current = stack.pop()
        if current in seen:
            continue
        seen.add(current)
        visited.append(current)
        # Push neighbors in reverse-sorted order so sorted order is processed first
        for neighbor in sorted(graph.neighbors(current), reverse=True):
            if neighbor not in seen:
                stack.append(neighbor)

    return visited


def dfs_recursive(graph: Graph, start_id: str) -> list[str]:
    """
    Depth-First Search traversal (recursive) starting from start_id.

    Returns:
        A list of node ids in the order they were visited.
    """
    if not graph.has_node(start_id):
        raise KeyError(f"Start node '{start_id}' not found in graph.")

    visited: list[str] = []
    seen: set[str] = set()

    def _dfs(node_id: str):
        seen.add(node_id)
        visited.append(node_id)
        for neighbor in sorted(graph.neighbors(node_id)):
            if neighbor not in seen:
                _dfs(neighbor)

    _dfs(start_id)
    return visited


# ─── Internal helper ──────────────────────────────────────────────────────────

def _reconstruct_path(parent: dict, end_id: str) -> list[str]:
    path = []
    current = end_id
    while current is not None:
        path.append(current)
        current = parent[current]
    return list(reversed(path))
