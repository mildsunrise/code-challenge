#!/usr/bin/env python3

def main():
    for i in range(int(input())):
        N, K = map(int, input().split())
        assert N <= 1000 and N % K == 0
        names = [ input() for _ in range(N) ]
        ans = process_case(names, K)
        print(f'Case #{i+1}: {ans}')

# - The longest common prefix of a set of names is equivalent to the longest
#   common prefix between min(names) and max(names), or put another way, the
#   names with minimum and maximum index in a sorted list.
# - So, instead of evaluating all possible *partitions* of the names in groups,
#   we only need to consider the *bounds* of these partitions (start & end
#   indices for every group).
# - Growing the bounds of a group makes no sense, it can't possibly give a
#   higher score.
# - If we have a partition, it makes no sense to consider modifications that
#   would only keep or grow the bounds of the groups.
# - From there we can prove that removing a maximum-score group (whichever
#   it is) from our names can't decrease the total score (removed group + 
#   maximum score of groups left).
# - We can find a maximum-score group by checking all K contiguous segments
#   of the list. Iteratively remove these groups until left with no names.
# - It could be further optimized by using a tree data structure that computes
#   LCA in constant time, or to incrementally recompute the subscores only at
#   the position we removed the word...

def common_prefix(a, b):
    for x, y in zip(a, b):
        if x != y: break
        yield x

def process_case(names: list[str], K: int) -> int:
    names = sorted(names)
    score = 0
    get_score = lambda a, b: sum(1 for _ in common_prefix(a, b))
    while names:
        subscore, pos = max((get_score(names[i], names[i+K-1]), i)
            for i in range(len(names) - (K-1)))
        score += subscore
        names = names[:pos] + names[pos + K:]
    return score

if __name__ == '__main__': main()
