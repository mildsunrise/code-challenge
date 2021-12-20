#!/usr/bin/env python3

from functools import reduce

def main():
    for i in range(int(input())):
        N = int(input())
        heaps = list(map(int, input().split()))
        assert len(heaps) == N
        assert all(heap > 0 for heap in heaps)
        ans = process_case(heaps)
        print(f'Case #{i+1}: {ans}')

def process_case(heaps: list[int]) -> str:
    nimber_for_heap = lambda n: n % 3
    nimber = reduce(lambda a, b: a ^ b, map(nimber_for_heap, heaps))
    return 'Edu' if nimber else 'Alberto'

if __name__ == '__main__': main()
