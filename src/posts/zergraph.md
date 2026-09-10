---
title: building an svg git graph renderer
date: sept. 7, 2026
---

i'm doing this project in python because doing it in any other language is overcomplicated.

## turning the git commits into a graph

\[1\] if you've taken a computer science class or learnt about dsa before, you may have heard of a graph. it's a data structure behind some of the most intricate algorithms. here, it's convenient not because we're making an algorithm but to use it later to display it. to get the git commits, i run the command:

```
git log --all --topo-order --pretty=format:%H%x09%P%x09%an%x09%at%x09%s
```

for the repo right now, it looks like this:

```
...2bb4b        fivy    1788708596      latex, introduction post and image layout
...20c8e        fivy    1788678283      dynamicize posts.html to display post. freedom over visible posts with json object in post>
...f77ff        fivy    1788664814      ficks
...85e09        fivy    1788664564      404 page
...7c7dc        left    1788664496      github workflow
...f53e8        fivy    1788664033      the base site is done
...e8dfd        fivy    1788617613      update with todo and lots of minor fixes for main.py
...0cfa3        fivy    1788411423      rewrite: my own ssg
...
```

\[2\] then i split it to get the its sha, its parent's sha, author, timestamp and message. i originally used `--date-order` before today but that doesn't help since commits come in different branches at interleaving times, we don't know which branch is which (important for rendering the metro-style git graph) so i switched to `--topo-order`. imagine as the git graph has a split commit (2 commits have the same parent) and a merge commit (a commit have 2 parents)

![](/assets/topo-order-demo.png)

<p class="timegap"><time datetime="2026-09-08">sept. 10, 2026</time></p>

## processing the graph into a layout

\[3\] to be able to construct a layout like this, we also need to define what a layout is. we can think of a layout as having rows (sequential commits in rows) and columns (branches/lanes as columns) as well as lane color for branches. 

\[4\] now, we can move on to processing layouts. basically when you read and process commits there are 2 phases: positioning nodes and connecting edges. first, we have to place nodes correctly (and this is the most important phase). connecting edges just accesses the node's positions via sha and a position lookup dictionary. from there, we also need 2 subphases. for the first subphase, we can assign lanes to each node with another lookup dictionary i'll call `branches:dict[str, int]` or maybe assign a branch's members to a branch in `branch_members:dict[int, list[str]]` so the order now doesn't matter as long as they're in the same branch. for the second subphase, we reorder the graph's nodes to be chronological and use a rule to deduce the node's column in layout.

![](/assets/explanationzergraph.png)

### branch assignment - positional processor subphase 1

\[5\] the core idea of our positional processor's first subphase to assigning branches is that: branches can be defined and modified relying on "expectations" (unresolved parent-child relationships due to nodes being read in process order/topological order). as long as each node receives a stable `branch_id` or is a member of a `branch` such that it doesn't violate the edges.

\[6\] to store the expectations, create `active:list[tuple[int, str]]` which stores a pair `(branch_id, expected_sha)`. i actually prefer to use `branch_members:dict[int, list[str]]` for a reason you'll see later.

![](/assets/branch_assignment_zergraph.png)
*: the current tie-break condition for 1+ branches is assigning the node the lowest branch id

```python
def assign_branches(nodes):
    active = []
    branch_members = {}
    next_id = 0

    for node in nodes:
        sha = node["sha"]
        matches = [e for e in active if e[1] == sha]

        if not matches:
            branch_id = next_id
            next_id += 1
        else:
            branch_id = min(e[0] for e in matches)
            active = [e for e in active if e not in matches]

        branch_members.setdefault(branch_id, []).append(sha)

        for i, parent_sha in enumerate(node["parents"]):
            if i == 0:
                pid = branch_id
            else:
                pid = next_id
                next_id += 1
            active.append((pid, parent_sha))

    return branch_members
```

\[7\] to illustrate this algorithm, we're going to take the second graph from paragraph \[4\]:
```python
class graph():
    def __init__(self):
        self.nodes = {}
        self.edges = []

    def insert_node(self, sha:str, parents:list[str]):
        self.nodes[sha] = {"sha": sha, "parents": parents}

...

if __name__ == "__main__":
    test = graph()
    test.insert_node("A", ["B", "C", "E"])
    test.insert_node("B", ["F"])
    test.insert_node("C", ["D"])
    test.insert_node("D", ["E"])
    test.insert_node("E", ["H"])
    test.insert_node("F", ["G"])
    test.insert_node("G", ["H"])
    test.insert_node("H", []) # remember to add it as a valid node or it won't be processed

    print(assign_branches(test.nodes.values()))
```

```
(venv) PS C:\Users\TRUONG NGHIA QUAN\Documents\projects-that-i-made\2urleft.github.io\ssg> python ../test.py
{0: ['A', 'B', 'F', 'G', 'H'], 1: ['C', 'D', 'E']}
```

it's also worth adding this:
```py
if active:
    raise ValueError(f"unresolved branch entries — missing root commits? {active}")
```
for unresolved child nodes if the parent node doesn't exist. last time i didn't add `test.insert_node("H", [])` so running it with this line will give me:

```
(venv) PS C:\Users\TRUONG NGHIA QUAN\Documents\projects-that-i-made\2urleft.github.io\ssg> python ../test.py
Traceback (most recent call last):
  File "C:\Users\TRUONG NGHIA QUAN\Documents\projects-that-i-made\2urleft.github.io\test.py", line 50, in <module>
    print(assign_branches(test.nodes.values()))
          ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\TRUONG NGHIA QUAN\Documents\projects-that-i-made\2urleft.github.io\test.py", line 36, in assign_branches
    raise ValueError(f"unresolved branch entries — missing root commits? {active}")
ValueError: unresolved branch entries — missing root commits? [(0, 'B'), (1, 'C'), (2,'E')]
```

### column packing - positional processor subphase 2

\[8\] next, we assign the nodes a position. first, sort the nodes chronologically (*from now on, we're going to use [2urleft/zergraph](https://github.com/2urleft/zergraph)'s data structures*):
```python
class graph():
    ...

    def sort_chronologically(self):
        self.nodes = {sha: commit for sha, commit in sorted(self.nodes.items(), key=lambda x: x[1].get("timestamp"))}
```
and after assigning `branches = assign_branches(cgraph.nodes)`, run an algorithm for column packing.

\[9\] initialize `columns:dict[int, int]` for `branch_id: column` and `free_columns` as a min-heap/list of column indices.

![](/assets/column_packing_zergraph.png)

```python
def assign_columns(nodes, branch_members, last_row_of_branch):
    columns = {}
    free_columns = []
    next_column = 0
    layout_nodes = []

    for row, (sha, commit) in enumerate(nodes.items()):
        branch_id = next(b for b, members in branch_members.items() if sha in members)

        if branch_id in columns:
            col = columns[branch_id]
        elif free_columns:
            col = min(free_columns)
            free_columns.remove(col)
        else:
            col = next_column
            next_column += 1
        columns[branch_id] = col

        layout_nodes.append(
            layoutnode(
                sha=sha,
                row=row,
                col=col,
                branch_id=branch_id,
                lane_color=branch_id,
                commit=commit,
            )
        )

        if row == last_row_of_branch[branch_id]:
            free_columns.append(col)
            del columns[branch_id]

    return layout_nodes
```

\[10\] you should notice the `last_row_of_branch`, for every branch there's a row that is last in chronological order which ends the branch and opens up a free column for new branches. note that this should be computed when the nodes are in chronological order:

```python
def display_lnodes(nodes:list[layoutnode]):
    for node in nodes:
        print(f"{node.sha} at ({node.row}, {node.col}) branch {node.branch_id}")

def build_layout(cgraph:graph):
    branches = assign_branches(cgraph.nodes)
    cgraph.sort_chronologically()
    row_by_sha = {sha: row for row, sha in enumerate(cgraph.nodes)}
    last_row_of_branch = {
        branch_id: max(row_by_sha[sha] for sha in members)
        for branch_id, members in branches.items()
    }
    lnodes = assign_columns(cgraph.nodes, branches, last_row_of_branch)
    display_lnodes(lnodes)
```

here's the result for this repo [(2urleft.github.io)](https://github.com/2urleft/2urleft.github.io):

```
PS C:\Users\TRUONG NGHIA QUAN\Documents\projects-that-i-made\zergraph> python parser.py ../2urleft.github.io
ba7127944f4650e6807e6eab18647419e470cfa3 at (0, 0) branch 0
b14a454ee00b4c9f2fd4d8d2922203e41a5e8dfd at (1, 0) branch 0
ca4f60015759a95d2587890da33e8ba868cf53e8 at (2, 0) branch 0
1f09f8ab9dcce4b003085041c803b9bbccb7c7dc at (3, 0) branch 0
4e9689577bd6070d8e95b012a344a55948885e09 at (4, 0) branch 0
7692697f754e47cbbf982ce60556edf8529f77ff at (5, 0) branch 0
ccc29a88ccfce94af22a7a537e4a5e74c5520c8e at (6, 0) branch 0
6ad479e09d2c7107a403d7fbc901f73cc2f2bb4b at (7, 0) branch 0
a4cf37c1f01812af69be16ff8c3d4e2686d691ab at (8, 0) branch 0
```

a linear graph might not stress test it but it's accurate for now.

### edge connection

