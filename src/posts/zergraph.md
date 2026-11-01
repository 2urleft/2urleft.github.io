---
title: building a simple git commit graph renderer
date: sept. 7, 2026
---

## where to start with a git commit?

\[1\] a git history is already a graph, since every commit points to one or more parent commits. the first parent usually continues the main line of development, and extra parents show where branches have been merged. to draw this history, we need to give every commit a position and then draw a line between each commit and its parents.

\[2\] i split zergraph into two small programs so each one can focus on one part of the job. `parser.py` reads the history and gives each commit a row and column, then writes that layout as json. `renderer.py` reads the layout and turns it into an svg, which means i can work on how the graph looks without changing how git commits are read.

## parsing the git history

\[3\] the easiest way to get the commit data is to ask git for every commit reachable from its references, in topological order:

```bash
git log --all --topo-order --pretty=format:%H%x00%P%x00%an%x00%at%x00%s%x00
```

\[4\] each record has five fields separated by nul characters: the commit sha, its parent shas, the author's name, the author timestamp, and the subject. nul is handy here because spaces and tabs can appear in names or messages without confusing the parser. when there are several parents, their shas are separated by spaces.

```python
fields = result.stdout.split("\0")
while fields and not fields[-1].strip():
    fields.pop()

commits = []

for index in range(0, len(fields), 5):
    sha, parents_text, author, timestamp_text, subject = fields[index:index + 5]
    commits.append(commit(
        sha=sha,
        parents=tuple(parents_text.split()) if parents_text.strip() else (),
        author=author,
        timestamp=int(timestamp_text),
        subject=subject,
    ))
```

\[5\] each record becomes a `commit` with those five values. then `commit_graph` keeps the commits indexed by sha and adds an edge from each loaded parent to its child. i only add edges when both commits are present, so a partial history can still be drawn even if an older parent is missing.

```python
for child_sha, item in graph.nodes.items():
    for parent_sha in item.parents:
        if parent_sha in graph.nodes:
            graph.edges.append(edge(parent=parent_sha, child=child_sha))
```

\[6\] git's `--topo-order` gives us a useful order for laying out the history, so i keep that order instead of sorting by timestamps. timestamps can be skewed, and they don't guarantee that a commit will appear before its parent. keeping the supplied order makes the row assignment predictable.

## placing commits into lanes

\[7\] the layout gives each commit a row and a column. rows follow the order from git, while columns show the lanes that commits travel along. i keep a list called `lanes`; each entry is a commit sha that the lane is waiting to see next. if the current commit is already in that list, its index gives us its column. otherwise, i start a new lane at the end.

\[8\] after placing a commit, i remove its sha from the lane list and schedule its loaded parents. the first parent takes over the same lane, while any additional parent is placed in a nearby lane unless another active lane already expects it. that way, a first-parent history can continue in a straight column, and merge commits can bring other lanes into it.

\[9\] the main loop in `build_layout` is small enough to show on its own. the actual function also handles an empty history and removes duplicate parent shas before scheduling them:

```python
lanes = []
positions = {}

for row, commit in enumerate(commits):
    if commit.sha in lanes:
        col = lanes.index(commit.sha)
    else:
        col = len(lanes)
        lanes.append(commit.sha)

    positions[commit.sha] = (col, row)
    lanes.pop(col)

    loaded_parents = [p for p in commit.parents if p in graph.nodes]
    if loaded_parents:
        lanes.insert(col, loaded_parents[0])
        for offset, parent in enumerate(loaded_parents[1:], start=1):
            if parent not in lanes:
                lanes.insert(min(col + offset, len(lanes)), parent)
```

\[10\] once every commit has a position, i can build a `layout_edge` for each parent-child relationship. the edge records both shas and their coordinates, and it is marked as straight when the commits share a column or as a branch when they don't. the finished `layout` keeps all the nodes and edges together, along with the row and column counts.

```json
{
  "nodes": [
    {
      "sha": "child",
      "row": 0,
      "col": 0,
      "commit": {
        "sha": "child",
        "parents": ["parent"],
        "author": "alex",
        "timestamp": 100,
        "subject": "make a change"
      }
    },
    {
      "sha": "parent",
      "row": 1,
      "col": 0,
      "commit": {
        "sha": "parent",
        "parents": [],
        "author": "alex",
        "timestamp": 90,
        "subject": "start the project"
      }
    }
  ],
  "edges": [
    {
      "parent_sha": "parent",
      "child_sha": "child",
      "start": [0, 1],
      "end": [0, 0],
      "kind": "straight"
    }
  ]
}
```

## handing the layout to the renderer

\[11\] saving the layout as json gives `renderer.py` a simple format to read. nodes keep their sha, row, column, and commit details; edges keep the endpoint shas, coordinates, and type. i can also load this json later without asking git to rebuild the layout.

\[12\] `parser.py` can read from a repository path or from a commit fixture passed with `--input-json`. fixtures are useful when i want to try the same graph more than once, since they keep the commits and their order fixed. `tests/fixtures/all-in-one.json` is one example with a feature branch, a hotfix, and a couple of merges.

```powershell
python parser.py ..\some-repo --pretty
python parser.py --input-json tests\fixtures\all-in-one.json --pretty
```

## drawing the commit graph

\[13\] before drawing anything, the renderer assigns colors to the edges. it walks commits in row order and follows first parents, giving each unclaimed history its own line. an edge to the first parent uses the child's line, while an extra merge-parent edge uses the parent's line, so the merged branch keeps its color as it joins the graph.

```python
line_of = {}
next_line = 0

for sha in sorted(nodes, key=lambda sha: nodes[sha].row):
    if sha in line_of:
        continue

    current = sha
    while current is not None and current not in line_of:
        line_of[current] = next_line
        current = first_parent(nodes[current], nodes)

    next_line += 1
```

\[14\] edges in the same column can usually be drawn straight down, unless another station is in the way. when an edge changes columns, the renderer tries to route it through the gutter between lanes: it leaves the station diagonally, travels vertically in the gutter, then turns diagonally into the other station. the diagonals use 45-degree angles when there is enough room. if they don't fit, the renderer tries a larger row gap and otherwise uses a direct connection. overlapping routes share the gutter by using different slots.

```python
def build_path(start, end, gutter_x):
    (x1, y1), (x2, y2) = start, end
    direction = 1 if y2 > y1 else -1
    first_diagonal = abs(gutter_x - x1)
    second_diagonal = abs(x2 - gutter_x)

    if abs(y2 - y1) < first_diagonal + second_diagonal:
        return None

    return [
        start,
        (gutter_x, y1 + direction * first_diagonal),
        (gutter_x, y2 - direction * second_diagonal),
        end,
    ]
```

\[15\] i draw the edges first and the stations on top, so the lines don't cover the commit shapes. regular commits are circles, merge commits are diamonds, and commits without parents are squares. each line gets a small extension and a t-bar at its ends, while optional labels show the subject, author, date, and sha. text is escaped before being added to the svg.

\[16\] colors and spacing live in `theme` and `render_style`, away from the graph layout. from the command line, i can pick a light or dark theme, change colors, hide labels or guides, add a legend, and adjust alignment or canvas width. the renderer can take a saved layout, a fixture, or a repository directly:

```bash
python renderer.py layout.json -o graph.svg
python renderer.py tests\fixtures\all-in-one.json -o graph.svg --dark --legend
python renderer.py ..\some-repo -o graph.svg --align center --width 1000
```
