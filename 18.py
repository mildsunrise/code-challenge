#!/usr/bin/env python3

from collections import Counter

def main():
    for i in range(int(input())):
        N = int(input())
        insns = [ tuple(input().split()) for _ in range(N) ]
        assert all(len(insn) == 2 and insn[1] in ARGS for insn in insns)
        min, diff = process_case(insns)
        print(f'Case #{i+1}: {min}, {diff}')

ARGS = {
    'UP':    '00',
    'DOWN':  '11',
    'RIGHT': '10',
    'LEFT':  '01',
}

def process_case(insns: list[tuple[int, int]]) -> tuple[int, int]:
    codes = Counter(op for op, _ in insns)

    # calculate huffman code
    # nodes are (freq, max_depth, depths), we minimize freq then max_depth
    nodes = [ (freq, 0, { label: 0 }) for label, freq in codes.items() ]
    while len(nodes) > 1:
        (fa, ma, da), (fb, mb, db), *nodes = sorted(nodes, key=lambda n: n[:2])
        depths = { k: v + 1 for k, v in (da | db).items() }
        nodes.append((fa + fb, max(ma, mb) + 1, depths))
    _, max_depth, depths = nodes[0]

    # override because apparently 0-length code for 1 node isn't allowed
    if len(depths) == 1:
        depths = { k: v + 1 for k, v in depths.items() }
        max_depth += 1
    
    length = sum(depths[op] + len(ARGS[arg]) for op, arg in insns)
    diff = max_depth - min(depths.values())
    return length, diff

if __name__ == '__main__': main()
