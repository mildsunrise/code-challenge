#!/usr/bin/env python3

from typing import Callable

Point = tuple[int, int]
point_add: Callable[[Point, Point], Point] = lambda x, y: (x[0] + y[0], x[1] + y[1])
point_sub: Callable[[Point, Point], Point] = lambda x, y: (x[0] - y[0], x[1] - y[1])
point_neg: Callable[[Point], Point] = lambda x, k: (-x[0], -x[1])
point_scale: Callable[[Point, int], Point] = lambda x, k: (x[0] * k, x[1] * k)
point_min: Callable[[Point, Point], Point] = lambda x, y: (min(x[0], y[0]), min(x[1], y[1]))
point_max: Callable[[Point, Point], Point] = lambda x, y: (max(x[0], y[0]), max(x[1], y[1]))

def main():
    T = int(input())
    D = int(input())
    sprites = [ parse_sprite() for _ in range(D) ]
    for i in range(T):
        P = int(input())
        defs = [ tuple(map(int, input().split())) for _ in range(P) ]
        assert all(len(d) == 3 and 0 <= d[0] < len(sprites) for d in defs)
        ans = process_case(sprites, defs)
        print(f'Case #{i+1}: {ans}')

Sprite = list[list[bool]]
SpriteDef = tuple[int, int, int]

def parse_sprite() -> Sprite:
    W, H = map(int, input().split())
    rows = [ [ {'0': False, '1': True}[x] for x in input() ] for _ in range(H) ]
    assert all(len(row) == W for row in rows)
    return rows

def process_case(sprites: list[Sprite], defs: list[SpriteDef]) -> set[str]:
    def resolve_def(d: SpriteDef) -> tuple[Sprite, tuple[int, int], tuple[int, int]]:
        # returns (sprite pixel getter, bounding box start, bounding box end)
        idx, *start = d
        sprite = sprites[idx]
        size = len(sprite[0]), len(sprite)
        get_pixel_rel = lambda p: sprite[p[1]][p[0]]
        get_pixel = lambda p: get_pixel_rel(point_sub(p, start))
        return get_pixel, start, point_add(start, size)

    def sprites_collide(d1, d2):
        s1, p1, q1 = resolve_def(d1)
        s2, p2, q2 = resolve_def(d2)
        # find bounding box intersection, skip if empty
        p, q = point_max(p1, p2), point_min(q1, q2)
        iw, ih = point_sub(q, p)
        if not (iw > 0 and ih > 0): return False
        # check intersected rectangle
        check = lambda x: s1(x) and s2(x)
        return any(check(point_add(p, (x, y))) for x in range(iw) for y in range(ih))

    return sum(1 for i, d1 in enumerate(defs) for d2 in defs[i+1:] if sprites_collide(d1, d2))

if __name__ == '__main__': main()
