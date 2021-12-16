#!/usr/bin/env python3

def main():
    for i in range(int(input())):
        R = int(input())
        Rs = list(map(int, input().split()))
        assert len(Rs) == R
        ans = process_case(Rs)
        print(f'Case #{i+1}: {" ".join(map(str, ans))}')

def process_case(rolls):
    assert all(0 <= roll <= 10 for roll in rolls)
    rolls = list(rolls)

    frames = []
    total_score = 0
    for _ in range(10):
        # consume the rolls for this frame
        score, bonus = 0, 2
        for _ in range(2):
            score += rolls.pop(0)
            assert score <= 10
            if score == 10: break
            bonus -= 1
        # add up points of future bonus rolls
        score += sum(rolls[:bonus])
        # save current total score
        total_score += score
        frames.append(total_score)

    assert len(rolls) == bonus
    return frames


if __name__ == '__main__': main()
