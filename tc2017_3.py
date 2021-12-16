#!/usr/bin/env python3

def main():
    for i in range(int(input())):
        P = int(input())
        ans = process_case(P)
        print(f'Case #{i+1}: {ans}')

def process_case(P):
    return P.bit_length()

if __name__ == '__main__': main()
