# Graph Navigator

**Автор:** Апаркина Ника

---

## Описание

**Graph Navigator** — консольное приложение для работы с графами.  
Поддерживает три типа графов, обходы BFS/DFS, поиск кратчайшего пути (алгоритм Дейкстры и BFS), сохранение/загрузку в JSON, а также полную валидацию пользовательского ввода.

Архитектура построена по паттерну **MVC** с применением **Factory Method** для создания графов.

---

## Архитектура

```
graph_navigator/
├── main.py                       # Точка входа
├── models/
│   ├── graph_node.py             # Класс GraphNode (вершина графа)
│   ├── base_graph.py             # Абстрактный базовый класс Graph
│   ├── graph_types.py            # DirectedGraph, UndirectedGraph, WeightedGraph
│   └── graph_factory.py          # Фабрика графов + десериализация из JSON
├── algorithms/
│   ├── traversal.py              # BFS, DFS, bfs_path
│   └── dijkstra.py               # Алгоритм Дейкстры
├── storage/
│   └── graph_storage.py          # Сохранение/загрузка JSON
├── controller/
│   └── graph_controller.py       # MVC Controller
├── view/
│   └── console_view.py           # MVC View (консольный интерфейс)
└── tests/
    ├── test_part1.py              # 49 тестов: модели, алгоритмы, хранилище
    └── test_part2.py              # 47 тестов: контроллер, интеграция
```

### Применённые принципы ООП
| Принцип | Где применён |
|---|---|
| **Инкапсуляция** | Приватные поля `_nodes`, `_adjacency` в `Graph`; свойства в `GraphNode` |
| **Наследование** | `DirectedGraph`, `UndirectedGraph`, `WeightedGraph` наследуют `Graph` |
| **Полиморфизм** | `add_edge` / `remove_edge` реализованы по-разному в каждом подклассе |
| **Абстракция** | `Graph` (ABC) с абстрактными методами `add_edge`, `remove_edge` |

### Паттерны проектирования
- **Factory Method** — `GraphFactory.create("directed" | "undirected" | "weighted")`
- **MVC** — `ConsoleView` → `GraphController` → модели/алгоритмы

---

## Требования

- Python **3.10+** (используется синтаксис `X | Y` для типов)
- Стандартная библиотека, сторонних зависимостей нет

---

## Запуск

```bash
git clone https://github.com/<your-username>/graph-navigator.git
cd graph-navigator
python main.py
```

---

## Команды приложения

| Команда | Описание |
|---|---|
| `new <type>` | Создать граф (`directed` / `undirected` / `weighted`) |
| `info` | Информация о текущем графе |
| `add-node <id>` | Добавить вершину |
| `del-node <id>` | Удалить вершину |
| `nodes` | Список вершин |
| `add-edge <A> <B> [вес]` | Добавить ребро (вес только для WeightedGraph) |
| `del-edge <A> <B>` | Удалить ребро |
| `edges` | Список рёбер |
| `neighbors <id>` | Соседи вершины |
| `bfs <start>` | Обход в ширину |
| `dfs <start>` | Обход в глубину |
| `path <A> <B>` | Кратчайший путь (Dijkstra / BFS) |
| `save <имя>` | Сохранить граф в JSON |
| `load <имя>` | Загрузить граф из JSON |
| `ls` | Список сохранённых файлов |
| `rm <имя>` | Удалить файл |
| `help` | Справка |
| `exit` | Выход |

---

## Примеры использования

### Взвешенный граф + Дейкстра

```
graph> new weighted
✔  Created new WeightedGraph.

graph> add-node A
✔  Node 'A' added.
graph> add-node B
✔  Node 'B' added.
graph> add-node C
✔  Node 'C' added.

graph> add-edge A B 1
✔  Edge 'A' → 'B' (weight=1.0) added.
graph> add-edge B C 2
✔  Edge 'B' → 'C' (weight=2.0) added.
graph> add-edge A C 10
✔  Edge 'A' → 'C' (weight=10.0) added.

graph> path A C
✔  Dijkstra shortest path: A → B → C
   Total distance: 3.0

graph> save my_graph
✔  Graph saved to 'saved_graphs/my_graph.json'.
```

### Ненаправленный граф + BFS

```
graph> new undirected
✔  Created new UndirectedGraph.

graph> add-node 1
graph> add-node 2
graph> add-node 3
graph> add-edge 1 2
graph> add-edge 2 3

graph> bfs 1
✔  BFS order: 1 → 2 → 3

graph> path 1 3
✔  BFS shortest path: 1 → 2 → 3
   Hops: 2
```

### Загрузка из JSON

```
graph> load my_graph
✔  Graph loaded from 'my_graph'. WeightedGraph(nodes=3, edges=3)

graph> info
ℹ  Type : WeightedGraph
   Nodes: 3  →  A  B  C
   Edges: 3
```

---

## Запуск тестов

```bash
# Из папки graph_navigator
python -m unittest tests.test_part1 -v   # 49 тестов
python -m unittest tests.test_part2 -v   # 47 тестов

# Все сразу
python -m unittest discover tests -v
```

**Итого: 96 тестов, все проходят.**

---

## Лицензия

MIT
