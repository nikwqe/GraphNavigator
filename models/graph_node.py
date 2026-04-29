"""
GraphNode module - represents a single vertex in a graph.
"""


class GraphNode:
    """
    Represents a single node (vertex) in a graph.

    Attributes:
        node_id (str): Unique identifier for the node.
        data (dict): Optional metadata associated with the node.
    """

    def __init__(self, node_id: str, data: dict = None):
        if not isinstance(node_id, str) or not node_id.strip():
            raise ValueError("node_id must be a non-empty string.")
        self._node_id = node_id.strip()
        self._data = data if data is not None else {}

    @property
    def node_id(self) -> str:
        return self._node_id

    @property
    def data(self) -> dict:
        return self._data

    @data.setter
    def data(self, value: dict):
        if not isinstance(value, dict):
            raise TypeError("data must be a dictionary.")
        self._data = value

    def __eq__(self, other) -> bool:
        if isinstance(other, GraphNode):
            return self._node_id == other._node_id
        return False

    def __hash__(self) -> int:
        return hash(self._node_id)

    def __repr__(self) -> str:
        return f"GraphNode(id='{self._node_id}')"

    def to_dict(self) -> dict:
        """Serialize the node to a dictionary."""
        return {"node_id": self._node_id, "data": self._data}

    @classmethod
    def from_dict(cls, d: dict) -> "GraphNode":
        """Deserialize a node from a dictionary."""
        return cls(node_id=d["node_id"], data=d.get("data", {}))
