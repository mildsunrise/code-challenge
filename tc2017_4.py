#!/usr/bin/env python3

def main():
    for i in range(int(input())):
        R, *Rs = list(map(int, input().split()))
        assert len(Rs) == R
        ans = process_case(Rs)
        print(f'Case #{i+1}: {ans}')

def process_case(sides):
    sides = sorted(sides)
    triangle_possible = lambda ab, c: ab[-2] + ab[-1] > c
    shortest_perimeter = lambda ab, c: ab[-2] + ab[-1] + c
    partitions = ((sides[:i], sides[i]) for i in range(2, len(sides)))
    return next((shortest_perimeter(*p) for p in partitions if triangle_possible(*p)), 'IMPOSSIBLE')

if __name__ == '__main__': main()
