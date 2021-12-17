#!/usr/bin/env python3

from collections import defaultdict

def main():
    for i in range(int(input())):
        T = int(input())
        edges = [ tuple(input().split(',')) for _ in range(T) ]
        assert all(len(edge) == 2 and all(edge) for edge in edges)
        ans = process_case(edges)
        print(f'Case #{i+1}: {",".join(sorted(ans)) if ans else "-"}')

def process_case(edges: list[tuple[str, str]]) -> set[str]:
    neighbors: dict[str, set[str]] = defaultdict(set)
    for x, y in edges:
        neighbors[x].add(y)
        neighbors[y].add(x)
    if not neighbors:
        return set()

    heights: dict[str, int] = dict()
    articulation_points: set[str] = set()

    def dfs(node: str, height=0) -> int:
        low = heights[node] = height
        for neighbor in neighbors[node]:
            if neighbor in heights:
                sublow = heights[neighbor]  # back edge
            else:
                sublow = dfs(neighbor, height + 1)
                if sublow >= height and height > 0:
                    articulation_points.add(node)
            low = min(low, sublow)
        return low

    dfs(root := next(iter(neighbors)))
    assert len(heights) == len(neighbors), 'original graph not connected'
    if sum(1 for n in neighbors[root] if heights[n] == 1) > 2:
        articulation_points.add(root)
    return articulation_points

if __name__ == '__main__': main()
