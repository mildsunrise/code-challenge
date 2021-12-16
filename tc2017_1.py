#!/usr/bin/env python3

idivceil = lambda x, d: (x + (d - 1)) // d

def main():
    for i in range(int(input())):
        N = int(input())
        Sx = list(map(int, input().split()))
        assert len(Sx) == N
        ans = process_case(Sx)
        print(f'Case #{i+1}: {ans}')

def process_case(case):
    return idivceil(sum(case), 8)

if __name__ == '__main__': main()
