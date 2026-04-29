"""
ConsoleView - MVC View layer.
Handles all input/output with the user via the terminal.
Knows nothing about graph internals — only calls the Controller.
"""

from controller.graph_controller import GraphController


# ─── ANSI colour helpers ──────────────────────────────────────────────────────

class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    CYAN   = "\033[96m"
    RED    = "\033[91m"
    GREY   = "\033[90m"
    WHITE  = "\033[97m"

def ok(msg: str)    -> str: return f"{C.GREEN}✔  {msg}{C.RESET}"
def err(msg: str)   -> str: return f"{C.RED}✖  {msg}{C.RESET}"
def info(msg: str)  -> str: return f"{C.CYAN}ℹ  {msg}{C.RESET}"
def head(msg: str)  -> str: return f"{C.BOLD}{C.YELLOW}{msg}{C.RESET}"
def dim(msg: str)   -> str: return f"{C.GREY}{msg}{C.RESET}"


# ─── Help text ────────────────────────────────────────────────────────────────

HELP_TEXT = """
{h}┌─────────────────────────────────────────────────────┐
│              GRAPH NAVIGATOR  —  Commands            │
└─────────────────────────────────────────────────────┘{r}

{b}GRAPH MANAGEMENT{r}
  new <type>              Create a new graph
                          Types: directed | undirected | weighted
  info                    Show current graph summary
  clear                   Remove all nodes and edges (re-create same type)

{b}NODES{r}
  add-node <id>           Add a node
  del-node <id>           Remove a node (and its edges)
  nodes                   List all nodes

{b}EDGES{r}
  add-edge <A> <B> [w]    Add edge A→B  (weight optional, for WeightedGraph)
  del-edge <A> <B>        Remove edge A→B
  edges                   List all edges
  neighbors <id>          Show outgoing neighbors of a node

{b}ALGORITHMS{r}
  bfs <start>             BFS traversal from start node
  dfs <start>             DFS traversal from start node
  path <A> <B>            Shortest path  (Dijkstra for weighted, BFS otherwise)

{b}PERSISTENCE{r}
  save <filename>         Save current graph to JSON
  load <filename>         Load graph from JSON
  ls                      List saved graph files
  rm <filename>           Delete a saved graph file

{b}OTHER{r}
  help                    Show this help
  exit / quit             Exit the application
""".format(h=C.CYAN, r=C.RESET, b=C.BOLD)


# ─── View ─────────────────────────────────────────────────────────────────────

class ConsoleView:
    """
    Console View in the MVC pattern.
    Reads lines from stdin, dispatches to the Controller, prints results.
    """

    def __init__(self):
        self._ctrl = GraphController()
        self._running = False

    # ─── Main loop ────────────────────────────────────────────────────────────

    def run(self) -> None:
        self._running = True
        self._print_banner()
        print(dim("  Type 'help' for commands, 'exit' to quit.\n"))

        while self._running:
            try:
                raw = input(f"{C.BOLD}{C.CYAN}graph>{C.RESET} ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                self._running = False
                break

            if not raw:
                continue
            self._dispatch(raw)

        print(dim("\nBye!"))

    # ─── Dispatcher ───────────────────────────────────────────────────────────

    def _dispatch(self, raw: str) -> None:
        parts = raw.split()
        cmd = parts[0].lower()
        args = parts[1:]

        handlers = {
            "help":       self._cmd_help,
            "exit":       self._cmd_exit,
            "quit":       self._cmd_exit,
            "new":        self._cmd_new,
            "info":       self._cmd_info,
            "clear":      self._cmd_clear,
            "add-node":   self._cmd_add_node,
            "del-node":   self._cmd_del_node,
            "nodes":      self._cmd_nodes,
            "add-edge":   self._cmd_add_edge,
            "del-edge":   self._cmd_del_edge,
            "edges":      self._cmd_edges,
            "neighbors":  self._cmd_neighbors,
            "bfs":        self._cmd_bfs,
            "dfs":        self._cmd_dfs,
            "path":       self._cmd_path,
            "save":       self._cmd_save,
            "load":       self._cmd_load,
            "ls":         self._cmd_ls,
            "rm":         self._cmd_rm,
        }

        handler = handlers.get(cmd)
        if handler is None:
            print(err(f"Unknown command '{cmd}'. Type 'help' for a list."))
            return

        try:
            handler(args)
        except (ValueError, TypeError, KeyError, RuntimeError) as e:
            print(err(str(e)))
        except FileNotFoundError as e:
            print(err(str(e)))

    # ─── Command handlers ─────────────────────────────────────────────────────

    def _cmd_help(self, _):
        print(HELP_TEXT)

    def _cmd_exit(self, _):
        self._running = False

    def _cmd_new(self, args):
        if not args:
            raise ValueError("Usage: new <type>  (directed | undirected | weighted)")
        msg = self._ctrl.create_graph(args[0])
        print(ok(msg))

    def _cmd_info(self, _):
        print(info(self._ctrl.current_graph_info()))

    def _cmd_clear(self, _):
        # Re-read current type then recreate
        g_info = self._ctrl.current_graph_info()
        graph_type_line = g_info.split("\n")[0]          # "Type : WeightedGraph"
        raw_type = graph_type_line.split(":")[1].strip()  # "WeightedGraph"
        type_map = {
            "DirectedGraph": "directed",
            "UndirectedGraph": "undirected",
            "WeightedGraph": "weighted",
        }
        factory_key = type_map.get(raw_type, "directed")
        msg = self._ctrl.create_graph(factory_key)
        print(ok(f"Graph cleared. {msg}"))

    def _cmd_add_node(self, args):
        if not args:
            raise ValueError("Usage: add-node <id>")
        node_id = self._validate_id(args[0])
        print(ok(self._ctrl.add_node(node_id)))

    def _cmd_del_node(self, args):
        if not args:
            raise ValueError("Usage: del-node <id>")
        print(ok(self._ctrl.remove_node(args[0])))

    def _cmd_nodes(self, _):
        nodes = self._ctrl.list_nodes()
        if not nodes:
            print(dim("  (no nodes)"))
        else:
            print(info(f"{len(nodes)} node(s): " + "  ".join(nodes)))

    def _cmd_add_edge(self, args):
        if len(args) < 2:
            raise ValueError("Usage: add-edge <A> <B> [weight]")
        from_id, to_id = args[0], args[1]
        weight = 1.0
        if len(args) >= 3:
            weight = self._parse_weight(args[2])
        print(ok(self._ctrl.add_edge(from_id, to_id, weight)))

    def _cmd_del_edge(self, args):
        if len(args) < 2:
            raise ValueError("Usage: del-edge <A> <B>")
        print(ok(self._ctrl.remove_edge(args[0], args[1])))

    def _cmd_edges(self, _):
        edges = self._ctrl.list_edges()
        if not edges:
            print(dim("  (no edges)"))
        else:
            print(head(f"  Edges ({len(edges)}):"))
            for e in edges:
                print(e)

    def _cmd_neighbors(self, args):
        if not args:
            raise ValueError("Usage: neighbors <id>")
        print(info(self._ctrl.show_neighbors(args[0])))

    def _cmd_bfs(self, args):
        if not args:
            raise ValueError("Usage: bfs <start_node>")
        print(ok(self._ctrl.run_bfs(args[0])))

    def _cmd_dfs(self, args):
        if not args:
            raise ValueError("Usage: dfs <start_node>")
        print(ok(self._ctrl.run_dfs(args[0])))

    def _cmd_path(self, args):
        if len(args) < 2:
            raise ValueError("Usage: path <A> <B>")
        result = self._ctrl.find_shortest_path(args[0], args[1])
        print(ok(result))

    def _cmd_save(self, args):
        if not args:
            raise ValueError("Usage: save <filename>")
        print(ok(self._ctrl.save_graph(args[0])))

    def _cmd_load(self, args):
        if not args:
            raise ValueError("Usage: load <filename>")
        print(ok(self._ctrl.load_graph(args[0])))

    def _cmd_ls(self, _):
        files = self._ctrl.list_saved_graphs()
        if not files:
            print(dim("  No saved graphs found."))
        else:
            print(head(f"  Saved graphs ({len(files)}):"))
            for f in sorted(files):
                print(f"    📄 {f}")

    def _cmd_rm(self, args):
        if not args:
            raise ValueError("Usage: rm <filename>")
        print(ok(self._ctrl.delete_saved_graph(args[0])))

    # ─── Input validation helpers ─────────────────────────────────────────────

    @staticmethod
    def _validate_id(raw: str) -> str:
        stripped = raw.strip()
        if not stripped:
            raise ValueError("Node id cannot be empty.")
        if len(stripped) > 64:
            raise ValueError("Node id too long (max 64 characters).")
        forbidden = set(' \t\n/\\"\':,{}[]')
        bad = [c for c in stripped if c in forbidden]
        if bad:
            raise ValueError(
                f"Node id contains forbidden characters: {' '.join(repr(c) for c in bad)}"
            )
        return stripped

    @staticmethod
    def _parse_weight(raw: str) -> float:
        try:
            w = float(raw)
        except ValueError:
            raise ValueError(f"Invalid weight '{raw}': must be a number.")
        if w < 0:
            raise ValueError(f"Weight must be non-negative, got {w}.")
        return w

    # ─── Banner ───────────────────────────────────────────────────────────────

    @staticmethod
    def _print_banner():
        print(f"""
{C.CYAN}{C.BOLD}
  ██████╗ ██████╗  █████╗ ██████╗ ██╗  ██╗    ███╗   ██╗ █████╗ ██╗   ██╗
 ██╔════╝ ██╔══██╗██╔══██╗██╔══██╗██║  ██║    ████╗  ██║██╔══██╗██║   ██║
 ██║  ███╗██████╔╝███████║██████╔╝███████║    ██╔██╗ ██║███████║██║   ██║
 ██║   ██║██╔══██╗██╔══██║██╔═══╝ ██╔══██║    ██║╚██╗██║██╔══██║╚██╗ ██╔╝
 ╚██████╔╝██║  ██║██║  ██║██║     ██║  ██║    ██║ ╚████║██║  ██║ ╚████╔╝
  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝  ╚═╝    ╚═╝  ╚═══╝╚═╝  ╚═╝  ╚═══╝
{C.RESET}""")
