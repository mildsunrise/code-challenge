#!/usr/bin/env python3

# For this to go reasonably fast, we do two things:
# - we store rows of bits in ints, using them as bitstrings
#   so we can then use more efficient bitwise operations
#   and so we can move a lot of the hot code into C land.
# - since there's a lot of bitmap instances and they are sparse,
#   checking every pair O(n^2) won't cut it; use a spatial index

from typing import Callable
from sklearn.neighbors import NearestNeighbors

Point = tuple[int, int]
point_add: Callable[[Point, Point], Point] = lambda x, y: (x[0] + y[0], x[1] + y[1])
point_sub: Callable[[Point, Point], Point] = lambda x, y: (x[0] - y[0], x[1] - y[1])
point_neg: Callable[[Point], Point] = lambda x, k: (-x[0], -x[1])
point_scale: Callable[[Point, int], Point] = lambda x, k: (x[0] * k, x[1] * k)
point_min: Callable[[Point, Point], Point] = lambda x, y: (min(x[0], y[0]), min(x[1], y[1]))
point_max: Callable[[Point, Point], Point] = lambda x, y: (max(x[0], y[0]), max(x[1], y[1]))

# parsing / main code

def main():
    T = int(input())
    D = int(input())
    sprites = [ parse_sprite() for _ in range(D) ]
    process_case = process_sprites(sprites)
    for i in range(T):
        P = int(input())
        defs = [ parse_sprite_def(sprites) for _ in range(P) ]
        ans = process_case(defs)
        print(f'Case #{i+1}: {ans}')

Sprite = tuple[Point, list[int]]
SpriteDef = tuple[int, Point]

def parse_sprite() -> Sprite:
    W, H = map(int, input().split())
    assert 0 <= W <= 512 and 0 <= H <= 512
    rows = [ input() for _ in range(H) ]
    assert all(len(row) == W and all(x in '01' for x in row) for row in rows)
    rows = [ int(row[::-1], 2) for row in rows ]
    return (W, H), rows

def parse_sprite_def(sprites: list[Sprite]) -> SpriteDef:
    I, X, Y = map(int, input().split())
    assert 0 <= I < len(sprites)
    return I, (X, Y)

# logic!

def process_sprites(sprites: list[Sprite]) -> Callable[[SpriteDef], int]:
    def resolve_def(d: SpriteDef) -> tuple[Sprite, tuple[int, int], tuple[int, int]]:
        # returns (sprite pixel getter, bounding box start, bounding box end)
        idx, start = d
        size, sprite = sprites[idx]
        return sprite, start, point_add(start, size)

    def sprites_collide(d1, d2):
        s1, p1, q1 = resolve_def(d1)
        s2, p2, q2 = resolve_def(d2)
        # find bounding box intersection, skip if empty
        p, q = point_max(p1, p2), point_min(q1, q2)
        iw, ih = point_sub(q, p)
        if not (iw > 0 and ih > 0): return False
        # check intersected rectangle (hot code, avoid range() and stuff)
        y1, y2 = p[1] - p1[1], p[1] - p2[1]
        endy1 = q[1] - p1[1]
        shift1, shift2 = p[0] - p1[0], p[0] - p2[0]
        mask = ~((~0) << iw)
        while y1 < endy1:
            row1 = s1[y1] >> shift1
            row2 = s2[y2] >> shift2
            if mask & row1 & row2: return True
            y1 += 1; y2 += 1
        return False

    def process_case(defs: list[SpriteDef]) -> set[str]:
        # build the spatial index, using the sprite centers
        defsmap = NearestNeighbors(metric='chebyshev')
        sprite_center = lambda d: point_add(d[1], point_scale(sprites[d[0]][0], 0.5))
        defsmap.fit([ sprite_center(d) for d in defs ])

        # perform search
        hits = defsmap.radius_neighbors(radius=512, return_distance=False)
        return sum(1 for i1, shits in enumerate(hits) for i2 in shits
            if i2 > i1 and sprites_collide(defs[i1], defs[i2]))

    return process_case

if __name__ == '__main__': main()
