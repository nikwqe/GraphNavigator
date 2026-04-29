"""
GraphStorage - Save and load graphs from JSON files.
"""

import json
import os
from models.base_graph import Graph
from models.graph_factory import GraphFactory


class GraphStorage:
    """
    Handles serialization and deserialization of Graph objects to/from JSON files.

    Encapsulates all I/O logic so the rest of the application stays clean.
    """

    def __init__(self, directory: str = "."):
        """
        Args:
            directory: Folder where JSON files will be saved/loaded.
                       Created automatically if it doesn't exist.
        """
        self._directory = directory
        os.makedirs(directory, exist_ok=True)

    # ─── Public API ───────────────────────────────────────────────────────────

    def save(self, graph: Graph, filename: str) -> str:
        """
        Serialize graph to JSON and write it to a file.

        Args:
            graph:    The graph to save.
            filename: File name (with or without .json extension).

        Returns:
            Absolute path of the written file.

        Raises:
            IOError: If the file cannot be written.
        """
        path = self._resolve_path(filename)
        data = graph.to_dict()
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return path

    def load(self, filename: str) -> Graph:
        """
        Read a JSON file and reconstruct the graph.

        Args:
            filename: File name (with or without .json extension).

        Returns:
            A fully reconstructed Graph instance.

        Raises:
            FileNotFoundError: If the file doesn't exist.
            ValueError:        If the JSON is malformed or the type is unknown.
        """
        path = self._resolve_path(filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"File '{path}' not found.")
        with open(path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in '{path}': {e}") from e
        return GraphFactory.from_dict(data)

    def list_saved(self) -> list[str]:
        """Return a list of all .json files in the storage directory."""
        try:
            return [
                f for f in os.listdir(self._directory) if f.endswith(".json")
            ]
        except OSError:
            return []

    def delete(self, filename: str) -> bool:
        """
        Delete a saved graph file.

        Returns:
            True if deleted, False if the file didn't exist.
        """
        path = self._resolve_path(filename)
        if os.path.exists(path):
            os.remove(path)
            return True
        return False

    # ─── Internal ─────────────────────────────────────────────────────────────

    def _resolve_path(self, filename: str) -> str:
        """Ensure filename ends with .json and is rooted in the storage dir."""
        if not filename.endswith(".json"):
            filename += ".json"
        return os.path.join(self._directory, filename)
