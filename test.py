class graph():
    def __init__(self):
        self.nodes = {}
        self.edges = []

    def insert_node(self, sha:str, parents:list[str]):
        self.nodes[sha] = {"sha": sha, "parents": parents}

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

        if active:
            raise ValueError(f"unresolved branch entries — missing root commits? {active}")

    return branch_members

if __name__ == "__main__":
    test = graph()
    test.insert_node("A", ["B", "C", "E"])
    test.insert_node("B", ["F"])
    test.insert_node("C", ["D"])
    test.insert_node("D", ["E"])
    test.insert_node("E", ["H"])
    test.insert_node("F", ["G"])
    test.insert_node("G", ["H"])

    print(assign_branches(test.nodes.values()))