"""
Tests for the first half of Graph Navigator:
  - GraphNode
  - DirectedGraph / UndirectedGraph / WeightedGraph
  - GraphFactory
  - BFS / DFS traversal
  - Dijkstra's algorithm
  - GraphStorage (JSON round-trip)
"""

import os
import sys
import tempfile
import unittest

# Make sure imports resolve from the project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from models.graph_node import GraphNode
from models.graph_types import DirectedGraph, UndirectedGraph, WeightedGraph
from models.graph_factory import GraphFactory
from algorithms.traversal import bfs, dfs, bfs_path, dfs_recursive
from algorithms.dijkstra import dijkstra, dijkstra_all
from storage.graph_storage import GraphStorage


# ─── GraphNode ────────────────────────────────────────────────────────────────

class TestGraphNode(unittest.TestCase):

    def test_create_valid_node(self):
        n = GraphNode("A")
        self.assertEqual(n.node_id, "A")
        self.assertEqual(n.data, {})

    def test_create_node_with_data(self):
        n = GraphNode("B", {"color": "red"})
        self.assertEqual(n.data["color"], "red")

    def test_empty_id_raises(self):
        with self.assertRaises(ValueError):
            GraphNode("")

    def test_whitespace_id_raises(self):
        with self.assertRaises(ValueError):
            GraphNode("   ")

    def test_non_string_data_raises(self):
        n = GraphNode("X")
        with self.assertRaises(TypeError):
            n.data = "not a dict"

    def test_equality(self):
        self.assertEqual(GraphNode("A"), GraphNode("A"))
        self.assertNotEqual(GraphNode("A"), GraphNode("B"))

    def test_serialization_round_trip(self):
        n = GraphNode("Z", {"weight": 42})
        n2 = GraphNode.from_dict(n.to_dict())
        self.assertEqual(n, n2)
        self.assertEqual(n2.data["weight"], 42)


# ─── DirectedGraph ────────────────────────────────────────────────────────────

class TestDirectedGraph(unittest.TestCase):

    def setUp(self):
        self.g = DirectedGraph()
        self.g.add_node("A")
        self.g.add_node("B")
        self.g.add_node("C")

    def test_add_and_has_node(self):
        self.assertTrue(self.g.has_node("A"))
        self.assertFalse(self.g.has_node("Z"))

    def test_duplicate_node_raises(self):
        with self.assertRaises(ValueError):
            self.g.add_node("A")

    def test_add_and_has_edge(self):
        self.g.add_edge("A", "B")
        self.assertTrue(self.g.has_edge("A", "B"))
        self.assertFalse(self.g.has_edge("B", "A"))  # directed!

    def test_duplicate_edge_raises(self):
        self.g.add_edge("A", "B")
        with self.assertRaises(ValueError):
            self.g.add_edge("A", "B")

    def test_remove_edge(self):
        self.g.add_edge("A", "B")
        self.g.remove_edge("A", "B")
        self.assertFalse(self.g.has_edge("A", "B"))

    def test_remove_missing_edge_raises(self):
        with self.assertRaises(KeyError):
            self.g.remove_edge("A", "B")

    def test_remove_node_cascades(self):
        self.g.add_edge("A", "B")
        self.g.add_edge("C", "B")
        self.g.remove_node("B")
        self.assertFalse(self.g.has_node("B"))
        self.assertFalse(self.g.has_edge("A", "B"))
        self.assertFalse(self.g.has_edge("C", "B"))

    def test_edge_to_missing_node_raises(self):
        with self.assertRaises(KeyError):
            self.g.add_edge("A", "MISSING")


# ─── UndirectedGraph ──────────────────────────────────────────────────────────

class TestUndirectedGraph(unittest.TestCase):

    def setUp(self):
        self.g = UndirectedGraph()
        for nid in ["A", "B", "C"]:
            self.g.add_node(nid)

    def test_edge_is_symmetric(self):
        self.g.add_edge("A", "B")
        self.assertTrue(self.g.has_edge("A", "B"))
        self.assertTrue(self.g.has_edge("B", "A"))

    def test_remove_edge_removes_both_directions(self):
        self.g.add_edge("A", "B")
        self.g.remove_edge("A", "B")
        self.assertFalse(self.g.has_edge("A", "B"))
        self.assertFalse(self.g.has_edge("B", "A"))

    def test_no_duplicate_edges_in_serialization(self):
        self.g.add_edge("A", "B")
        self.g.add_edge("B", "C")
        d = self.g.to_dict()
        self.assertEqual(len(d["edges"]), 2)


# ─── WeightedGraph ────────────────────────────────────────────────────────────

class TestWeightedGraph(unittest.TestCase):

    def setUp(self):
        self.g = WeightedGraph()
        for nid in ["A", "B", "C"]:
            self.g.add_node(nid)

    def test_weight_stored_correctly(self):
        self.g.add_edge("A", "B", 3.5)
        self.assertAlmostEqual(self.g.get_weight("A", "B"), 3.5)

    def test_negative_weight_raises(self):
        with self.assertRaises(ValueError):
            self.g.add_edge("A", "B", -1)

    def test_non_numeric_weight_raises(self):
        with self.assertRaises(TypeError):
            self.g.add_edge("A", "B", "heavy")

    def test_update_weight(self):
        self.g.add_edge("A", "B", 2.0)
        self.g.update_weight("A", "B", 7.0)
        self.assertAlmostEqual(self.g.get_weight("A", "B"), 7.0)

    def test_zero_weight_allowed(self):
        self.g.add_edge("A", "B", 0)
        self.assertAlmostEqual(self.g.get_weight("A", "B"), 0.0)


# ─── GraphFactory ─────────────────────────────────────────────────────────────

class TestGraphFactory(unittest.TestCase):

    def test_create_directed(self):
        g = GraphFactory.create("directed")
        self.assertIsInstance(g, DirectedGraph)

    def test_create_undirected(self):
        g = GraphFactory.create("undirected")
        self.assertIsInstance(g, UndirectedGraph)

    def test_create_weighted(self):
        g = GraphFactory.create("weighted")
        self.assertIsInstance(g, WeightedGraph)

    def test_case_insensitive(self):
        g = GraphFactory.create("DIRECTED")
        self.assertIsInstance(g, DirectedGraph)

    def test_unknown_type_raises(self):
        with self.assertRaises(ValueError):
            GraphFactory.create("hypergraph")

    def test_from_dict_round_trip(self):
        g = WeightedGraph()
        g.add_node("X")
        g.add_node("Y")
        g.add_edge("X", "Y", 5.0)
        data = g.to_dict()
        g2 = GraphFactory.from_dict(data)
        self.assertIsInstance(g2, WeightedGraph)
        self.assertTrue(g2.has_node("X"))
        self.assertAlmostEqual(g2.get_weight("X", "Y"), 5.0)


# ─── BFS / DFS ────────────────────────────────────────────────────────────────

class TestTraversal(unittest.TestCase):

    def _build_graph(self):
        """Simple directed graph: A->B, A->C, B->D, C->D"""
        g = DirectedGraph()
        for nid in ["A", "B", "C", "D"]:
            g.add_node(nid)
        g.add_edge("A", "B")
        g.add_edge("A", "C")
        g.add_edge("B", "D")
        g.add_edge("C", "D")
        return g

    def test_bfs_visits_all_reachable(self):
        g = self._build_graph()
        result = bfs(g, "A")
        self.assertEqual(sorted(result), ["A", "B", "C", "D"])

    def test_bfs_order(self):
        g = self._build_graph()
        result = bfs(g, "A")
        # A must come first; B and C before D
        self.assertEqual(result[0], "A")
        self.assertIn(result.index("B"), [1, 2])
        self.assertEqual(result[-1], "D")

    def test_dfs_visits_all_reachable(self):
        g = self._build_graph()
        result = dfs(g, "A")
        self.assertEqual(sorted(result), ["A", "B", "C", "D"])

    def test_dfs_recursive_matches_iterative(self):
        g = self._build_graph()
        self.assertEqual(dfs(g, "A"), dfs_recursive(g, "A"))

    def test_bfs_missing_start_raises(self):
        g = DirectedGraph()
        with self.assertRaises(KeyError):
            bfs(g, "X")

    def test_dfs_single_node(self):
        g = DirectedGraph()
        g.add_node("solo")
        self.assertEqual(dfs(g, "solo"), ["solo"])

    def test_bfs_path_found(self):
        g = self._build_graph()
        path = bfs_path(g, "A", "D")
        self.assertIsNotNone(path)
        self.assertEqual(path[0], "A")
        self.assertEqual(path[-1], "D")
        self.assertEqual(len(path), 3)

    def test_bfs_path_same_node(self):
        g = self._build_graph()
        self.assertEqual(bfs_path(g, "A", "A"), ["A"])

    def test_bfs_path_unreachable(self):
        g = DirectedGraph()
        g.add_node("A")
        g.add_node("B")
        self.assertIsNone(bfs_path(g, "A", "B"))


# ─── Dijkstra ─────────────────────────────────────────────────────────────────

class TestDijkstra(unittest.TestCase):

    def _build_weighted(self):
        """
            A --1-- B
            |       |
            4       2
            |       |
            C --1-- D
            A also connects directly to D with weight 10
        """
        g = WeightedGraph()
        for nid in ["A", "B", "C", "D"]:
            g.add_node(nid)
        g.add_edge("A", "B", 1)
        g.add_edge("B", "D", 2)
        g.add_edge("A", "C", 4)
        g.add_edge("C", "D", 1)
        g.add_edge("A", "D", 10)
        return g

    def test_shortest_path_and_distance(self):
        g = self._build_weighted()
        path, dist = dijkstra(g, "A", "D")
        self.assertEqual(path, ["A", "B", "D"])
        self.assertAlmostEqual(dist, 3.0)

    def test_same_node(self):
        g = self._build_weighted()
        path, dist = dijkstra(g, "A", "A")
        self.assertEqual(path, ["A"])
        self.assertAlmostEqual(dist, 0.0)

    def test_unreachable_returns_none(self):
        g = WeightedGraph()
        g.add_node("A")
        g.add_node("B")
        path, dist = dijkstra(g, "A", "B")
        self.assertIsNone(path)
        self.assertEqual(dist, float("inf"))

    def test_dijkstra_all(self):
        g = self._build_weighted()
        result = dijkstra_all(g, "A")
        self.assertAlmostEqual(result["D"][1], 3.0)
        self.assertAlmostEqual(result["B"][1], 1.0)
        self.assertAlmostEqual(result["C"][1], 4.0)

    def test_missing_start_raises(self):
        g = WeightedGraph()
        with self.assertRaises(KeyError):
            dijkstra(g, "NONE", "X")


# ─── GraphStorage ─────────────────────────────────────────────────────────────

class TestGraphStorage(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.storage = GraphStorage(self.tmp_dir)

    def _sample_graph(self):
        g = WeightedGraph()
        g.add_node("P", {"label": "Paris"})
        g.add_node("L", {"label": "London"})
        g.add_edge("P", "L", 340.0)
        return g

    def test_save_and_load(self):
        g = self._sample_graph()
        self.storage.save(g, "test_graph")
        g2 = self.storage.load("test_graph")
        self.assertIsInstance(g2, WeightedGraph)
        self.assertTrue(g2.has_node("P"))
        self.assertAlmostEqual(g2.get_weight("P", "L"), 340.0)

    def test_auto_json_extension(self):
        g = self._sample_graph()
        path = self.storage.save(g, "no_ext")
        self.assertTrue(path.endswith(".json"))

    def test_list_saved(self):
        self.storage.save(self._sample_graph(), "g1")
        self.storage.save(self._sample_graph(), "g2")
        files = self.storage.list_saved()
        self.assertIn("g1.json", files)
        self.assertIn("g2.json", files)

    def test_load_missing_file_raises(self):
        with self.assertRaises(FileNotFoundError):
            self.storage.load("nonexistent")

    def test_delete(self):
        self.storage.save(self._sample_graph(), "to_delete")
        self.storage.delete("to_delete")
        self.assertNotIn("to_delete.json", self.storage.list_saved())

    def test_undirected_round_trip(self):
        g = UndirectedGraph()
        g.add_node("X")
        g.add_node("Y")
        g.add_edge("X", "Y")
        self.storage.save(g, "undirected")
        g2 = self.storage.load("undirected")
        self.assertIsInstance(g2, UndirectedGraph)
        self.assertTrue(g2.has_edge("X", "Y"))
        self.assertTrue(g2.has_edge("Y", "X"))  # symmetric restored


if __name__ == "__main__":
    unittest.main(verbosity=2)
