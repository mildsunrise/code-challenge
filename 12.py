#!/usr/bin/env python3

from itertools import groupby
from collections import defaultdict

# Note: the 0 <= D <= 20 limit is incorrect

sorted_groupby = lambda x, k: groupby(sorted(x, key=k), key=k)
dict_groupby = lambda x, fk, fv: \
    { k: list(map(fv, vs)) for k, vs in sorted_groupby(x, fk) }

def main():
    for i in range(int(input())):
        M = int(input())
        assert 1 <= M <= 100
        websites = [ parse_website() for _ in range(M) ]
        ans = process_case(websites)
        print(f'Case #{i+1}: {ans}')

Trade = tuple[str, str, int]
Website = tuple[str, list[Trade]]

def parse_website() -> Website:
    name, K = input().split()
    K = int(K)
    assert 0 <= K <= 100
    trades = [ parse_trade() for _ in range(K) ]
    return name, trades

def parse_trade() -> Trade:
    a, D, b = input().split('-')
    D = int(D)
    assert 0 <= D <= 200
    return (a, b, D)

# I can't believe the amount of time I've lost on this,
# only to realize that D is guaranteed to be an integer...
# if hope that wasn't on purpose.
# 
# anyway. with integer D, the problem converts from a Weight
# Constrained Shortest Path Problem (which is NP-hard) into
# a much easier "shortest path with at least one of the edges
# in this set" (the set being the edges with D > 1).
# edges with D == 0 are discarded.
#
# that problem is a shortest path problem on a different graph
# made of two copies of the original graph, plus edges of the
# set connecting them. get all the shortest paths, maximize income.

def process_case(websites: list[Website]) -> int:
    # make digraph (remove D=0 edges) and derive our duplicated graph
    graph = preprocess_graph(websites)
    start, end = (False, 'BTC'), (True, 'BTC')

    # BFS to find shortest paths
    predecessors = find_predecessors(graph, start, end)
    if predecessors is None: return 1

    # from all shortest paths, find the one with maximum profit
    # (we can think of `predecessors` as a weighted DAG where we
    # want to find longest path)
    return dag_longest_path(predecessors, end, start)

# bool is True if we've already profitable, i.e. destination copy
Node = tuple[bool, str]
Digraph = dict[Node, list[tuple[Node, int]]]

def preprocess_graph(websites: list[Website]) -> Digraph:
    edges = ( trade for _, trades in websites for trade in trades )
    edges = [ (a,b,D) for a,b,D in edges if D > 0 ]

    copied_edges = [ ((copy, a), (copy, b), D)
        for copy in (False, True) for a, b, D in edges ]
    copied_edges.extend(
        ((False, a), (True, b), D) for a, b, D in edges if D > 1 )

    return dict_groupby(copied_edges, lambda edge: edge[0], lambda edge: edge[1:])

def find_predecessors(graph: Digraph, start: Node, end: Node) -> Digraph:
    predecessors: Digraph = defaultdict(lambda: [], { start: [] })
    current_level: set[Node] = set(predecessors)

    while current_level:
        if end in current_level:
            return dict(predecessors)
        next_level: set[Node] = set()
        for a in current_level:
            for b, D in graph.get(a, []):
                if b not in predecessors:
                    next_level.add(b)
                if b not in predecessors or b in next_level:
                    predecessors[b].append((a, D))
        current_level = next_level

    return None  # no shortest path

def dag_longest_path(graph: Digraph, start: Node, end: Node) -> int:
    topological_nodes = []
    visited = set()
    def visit(nodes):
        for node in nodes:
            if node in visited: continue
            visited.add(node)
            visit(adj for adj, _ in graph.get(node, []))
            topological_nodes.append(node)
    visit(graph)

    distances = { start: 1 }
    for node in reversed(topological_nodes):
        for adj, D in graph.get(node, []):
            subdistance = distances.get(node, 0) * D
            if distances.get(adj, 0) < subdistance:
                distances[adj] = subdistance
    return distances[end]

if __name__ == '__main__': main()
