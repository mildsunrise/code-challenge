#!/usr/bin/env python3

def main():
    for i in range(int(input())):
        dice = tuple(map(int, input().split(':')))
        ans = process_case(dice)
        print(f'Case #{i+1}: {ans}')

def process_case(dice):
    assert all(1 <= x <= 6 for x in dice)
    score = sum(dice)
    return score + 1 if score < 12 else '-'

if __name__ == '__main__': main()
