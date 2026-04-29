"""
Tests for the second half of Graph Navigator:
  - GraphController (MVC Controller)
  - ConsoleView input validation helpers
  - Integration: controller + storage round-trip
"""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from controller.graph_controller import GraphController
from models.graph_types import DirectedGraph, UndirectedGraph, WeightedGraph
from view.console_view import ConsoleView


# ─── GraphController ─────────────────────────────────────────────────────────

class TestGraphControllerCreation(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.ctrl = GraphController(storage_dir=self.tmp)

    def test_create_directed(self):
        msg = self.ctrl.create_graph("directed")
        self.assertIn("DirectedGraph", msg)

    def test_create_undirected(self):
        self.ctrl.create_graph("undirected")
        info = self.ctrl.current_graph_info()
        self.assertIn("UndirectedGraph", info)

    def test_create_weighted(self):
        self.ctrl.create_graph("weighted")
        info = self.ctrl.current_graph_info()
        self.assertIn("WeightedGraph", info)

    def test_unknown_type_raises(self):
        with self.assertRaises(ValueError):
            self.ctrl.create_graph("magic")

    def test_no_graph_raises_runtime_error(self):
        with self.assertRaises(RuntimeError):
            self.ctrl.current_graph_info()


class TestGraphControllerNodes(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.ctrl = GraphController(storage_dir=self.tmp)
        self.ctrl.create_graph("directed")

    def test_add_node(self):
        msg = self.ctrl.add_node("A")
        self.assertIn("A", msg)
        self.assertIn("A", self.ctrl.list_nodes())

    def test_add_duplicate_node_raises(self):
        self.ctrl.add_node("A")
        with self.assertRaises(ValueError):
            self.ctrl.add_node("A")

    def test_remove_node(self):
        self.ctrl.add_node("A")
        self.ctrl.remove_node("A")
        self.assertNotIn("A", self.ctrl.list_nodes())

    def test_remove_missing_node_raises(self):
        with self.assertRaises(KeyError):
            self.ctrl.remove_node("GHOST")

    def test_list_nodes_empty(self):
        self.assertEqual(self.ctrl.list_nodes(), [])

    def test_list_nodes_sorted(self):
        for n in ["C", "A", "B"]:
            self.ctrl.add_node(n)
        self.assertEqual(self.ctrl.list_nodes(), ["A", "B", "C"])


class TestGraphControllerEdges(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.ctrl = GraphController(storage_dir=self.tmp)
        self.ctrl.create_graph("directed")
        for n in ["A", "B", "C"]:
            self.ctrl.add_node(n)

    def test_add_edge(self):
        msg = self.ctrl.add_edge("A", "B")
        self.assertIn("A", msg)
        self.assertIn("B", msg)

    def test_add_edge_missing_node_raises(self):
        with self.assertRaises(KeyError):
            self.ctrl.add_edge("A", "Z")

    def test_remove_edge(self):
        self.ctrl.add_edge("A", "B")
        msg = self.ctrl.remove_edge("A", "B")
        self.assertIn("removed", msg.lower())

    def test_remove_missing_edge_raises(self):
        with self.assertRaises(KeyError):
            self.ctrl.remove_edge("A", "B")

    def test_list_edges_empty(self):
        self.assertEqual(self.ctrl.list_edges(), [])

    def test_list_edges_nonempty(self):
        self.ctrl.add_edge("A", "B")
        self.ctrl.add_edge("B", "C")
        edges = self.ctrl.list_edges()
        self.assertEqual(len(edges), 2)

    def test_undirected_edge_listed_once(self):
        ctrl = GraphController(storage_dir=self.tmp)
        ctrl.create_graph("undirected")
        ctrl.add_node("X")
        ctrl.add_node("Y")
        ctrl.add_edge("X", "Y")
        self.assertEqual(len(ctrl.list_edges()), 1)

    def test_show_neighbors(self):
        self.ctrl.add_edge("A", "B")
        self.ctrl.add_edge("A", "C")
        result = self.ctrl.show_neighbors("A")
        self.assertIn("B", result)
        self.assertIn("C", result)

    def test_show_neighbors_empty(self):
        result = self.ctrl.show_neighbors("A")
        self.assertIn("no", result.lower())


class TestGraphControllerAlgorithms(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.ctrl = GraphController(storage_dir=self.tmp)

    def _build_directed(self):
        self.ctrl.create_graph("directed")
        for n in ["A", "B", "C", "D"]:
            self.ctrl.add_node(n)
        self.ctrl.add_edge("A", "B")
        self.ctrl.add_edge("A", "C")
        self.ctrl.add_edge("B", "D")

    def _build_weighted(self):
        self.ctrl.create_graph("weighted")
        for n in ["A", "B", "C"]:
            self.ctrl.add_node(n)
        self.ctrl.add_edge("A", "B", 1.0)
        self.ctrl.add_edge("B", "C", 2.0)
        self.ctrl.add_edge("A", "C", 10.0)

    def test_bfs_output(self):
        self._build_directed()
        result = self.ctrl.run_bfs("A")
        self.assertIn("BFS", result)
        self.assertIn("A", result)
        self.assertIn("D", result)

    def test_dfs_output(self):
        self._build_directed()
        result = self.ctrl.run_dfs("A")
        self.assertIn("DFS", result)

    def test_bfs_missing_start_raises(self):
        self._build_directed()
        with self.assertRaises(KeyError):
            self.ctrl.run_bfs("Z")

    def test_bfs_path_found(self):
        self._build_directed()
        result = self.ctrl.find_shortest_path("A", "D")
        self.assertIn("A", result)
        self.assertIn("D", result)
        self.assertIn("Hops", result)

    def test_bfs_path_unreachable(self):
        self._build_directed()
        result = self.ctrl.find_shortest_path("D", "A")
        self.assertIn("No path", result)

    def test_dijkstra_path(self):
        self._build_weighted()
        result = self.ctrl.find_shortest_path("A", "C")
        self.assertIn("Dijkstra", result)
        self.assertIn("3.0", result)

    def test_dijkstra_unreachable(self):
        self.ctrl.create_graph("weighted")
        self.ctrl.add_node("X")
        self.ctrl.add_node("Y")
        result = self.ctrl.find_shortest_path("X", "Y")
        self.assertIn("No path", result)


class TestGraphControllerPersistence(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.ctrl = GraphController(storage_dir=self.tmp)

    def _make_graph(self):
        self.ctrl.create_graph("weighted")
        self.ctrl.add_node("P")
        self.ctrl.add_node("Q")
        self.ctrl.add_edge("P", "Q", 5.5)

    def test_save_and_load(self):
        self._make_graph()
        self.ctrl.save_graph("my_graph")
        msg = self.ctrl.load_graph("my_graph")
        self.assertIn("WeightedGraph", msg)

    def test_list_saved_shows_files(self):
        self._make_graph()
        self.ctrl.save_graph("alpha")
        files = self.ctrl.list_saved_graphs()
        self.assertIn("alpha.json", files)

    def test_delete_saved(self):
        self._make_graph()
        self.ctrl.save_graph("to_del")
        msg = self.ctrl.delete_saved_graph("to_del")
        self.assertIn("Deleted", msg)
        self.assertNotIn("to_del.json", self.ctrl.list_saved_graphs())

    def test_delete_nonexistent(self):
        msg = self.ctrl.delete_saved_graph("ghost")
        self.assertIn("not found", msg.lower())

    def test_load_missing_file_raises(self):
        with self.assertRaises(FileNotFoundError):
            self.ctrl.load_graph("no_such_file")

    def test_loaded_graph_is_functional(self):
        self._make_graph()
        self.ctrl.save_graph("func_test")
        self.ctrl.load_graph("func_test")
        result = self.ctrl.find_shortest_path("P", "Q")
        self.assertIn("5.5", result)


# ─── ConsoleView input validation ─────────────────────────────────────────────

class TestConsoleViewValidation(unittest.TestCase):
    """Test the static input-validation helpers on ConsoleView."""

    def test_valid_id(self):
        self.assertEqual(ConsoleView._validate_id("A"), "A")
        self.assertEqual(ConsoleView._validate_id("  node1  "), "node1")

    def test_empty_id_raises(self):
        with self.assertRaises(ValueError):
            ConsoleView._validate_id("")

    def test_whitespace_only_id_raises(self):
        with self.assertRaises(ValueError):
            ConsoleView._validate_id("   ")

    def test_too_long_id_raises(self):
        with self.assertRaises(ValueError):
            ConsoleView._validate_id("x" * 65)

    def test_forbidden_chars_raise(self):
        for bad in [" ", "/", "\\", "'", '"', ":", ","]:
            with self.assertRaises(ValueError, msg=f"Expected error for char {bad!r}"):
                ConsoleView._validate_id(f"node{bad}id")

    def test_valid_weight(self):
        self.assertAlmostEqual(ConsoleView._parse_weight("3.5"), 3.5)
        self.assertAlmostEqual(ConsoleView._parse_weight("0"), 0.0)
        self.assertAlmostEqual(ConsoleView._parse_weight("100"), 100.0)

    def test_non_numeric_weight_raises(self):
        with self.assertRaises(ValueError):
            ConsoleView._parse_weight("heavy")

    def test_negative_weight_raises(self):
        with self.assertRaises(ValueError):
            ConsoleView._parse_weight("-1")

    def test_float_string_weight(self):
        self.assertAlmostEqual(ConsoleView._parse_weight("2.718"), 2.718)


# ─── Integration: full flow ───────────────────────────────────────────────────

class TestIntegration(unittest.TestCase):
    """End-to-end scenarios covering the entire stack."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def test_directed_full_flow(self):
        ctrl = GraphController(storage_dir=self.tmp)
        ctrl.create_graph("directed")
        for n in ["S", "A", "B", "T"]:
            ctrl.add_node(n)
        ctrl.add_edge("S", "A")
        ctrl.add_edge("S", "B")
        ctrl.add_edge("A", "T")
        ctrl.add_edge("B", "T")

        bfs_res = ctrl.run_bfs("S")
        self.assertIn("T", bfs_res)

        path_res = ctrl.find_shortest_path("S", "T")
        self.assertIn("Hops: 2", path_res)

        ctrl.save_graph("directed_flow")
        ctrl2 = GraphController(storage_dir=self.tmp)
        ctrl2.load_graph("directed_flow")
        self.assertIn("DirectedGraph", ctrl2.current_graph_info())

    def test_weighted_full_flow(self):
        ctrl = GraphController(storage_dir=self.tmp)
        ctrl.create_graph("weighted")
        for n in ["X", "Y", "Z"]:
            ctrl.add_node(n)
        ctrl.add_edge("X", "Y", 4)
        ctrl.add_edge("Y", "Z", 3)
        ctrl.add_edge("X", "Z", 10)

        result = ctrl.find_shortest_path("X", "Z")
        self.assertIn("7.0", result)

        ctrl.save_graph("weighted_flow")
        ctrl2 = GraphController(storage_dir=self.tmp)
        ctrl2.load_graph("weighted_flow")
        result2 = ctrl2.find_shortest_path("X", "Z")
        self.assertIn("7.0", result2)

    def test_undirected_full_flow(self):
        ctrl = GraphController(storage_dir=self.tmp)
        ctrl.create_graph("undirected")
        for n in ["1", "2", "3"]:
            ctrl.add_node(n)
        ctrl.add_edge("1", "2")
        ctrl.add_edge("2", "3")

        dfs_res = ctrl.run_dfs("1")
        self.assertIn("3", dfs_res)

        path_res = ctrl.find_shortest_path("1", "3")
        self.assertIn("Hops: 2", path_res)

    def test_remove_node_updates_edges(self):
        ctrl = GraphController(storage_dir=self.tmp)
        ctrl.create_graph("directed")
        for n in ["A", "B", "C"]:
            ctrl.add_node(n)
        ctrl.add_edge("A", "B")
        ctrl.add_edge("B", "C")
        ctrl.remove_node("B")

        edges = ctrl.list_edges()
        self.assertEqual(edges, [])

        result = ctrl.find_shortest_path("A", "C")
        self.assertIn("No path", result)

    def test_graph_repr_after_operations(self):
        ctrl = GraphController(storage_dir=self.tmp)
        ctrl.create_graph("weighted")
        ctrl.add_node("M")
        ctrl.add_node("N")
        ctrl.add_edge("M", "N", 9.0)
        info = ctrl.current_graph_info()
        self.assertIn("WeightedGraph", info)
        self.assertIn("M", info)
        self.assertIn("N", info)


if __name__ == "__main__":
    unittest.main(verbosity=2)
