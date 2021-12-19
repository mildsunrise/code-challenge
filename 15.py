#!/usr/bin/env python3

def main():
    for i in range(int(input())):
        ans = process_case(int(input()))
        print(f'Case #{i+1}: {ans}')

M = 10**8 + 7  # prime

# naive way... at 1e8 it's not worth it to use anything else

def process_case(n: int) -> int:
    # M is not a tuentistic number, so if it gets included
    # the product drops to 0
    if n >= M: return 0

    # The code looks messy but it's worth to use counters here (since
    # mods / divisions would otherwise take most of the time).
    # But CPython is SO SLOW that the algorithm improvement gets lost
    # in the VM's overhead. In PyPy it's about 10x faster with counters.
    product = 1
    i = 1
    ctr1, ctr2, ctr3 = 80 + 1, 80 * 1000 + 1, 80 * 1000**2 + 1
    while i <= n:
        if ctr1 == 100:
            i += 10; ctr1 = 10; ctr2 += 10; ctr3 += 10
        elif ctr2 == 100_000:
            i += 10_000; ctr2 = 10_000; ctr3 += 10_000
        elif ctr3 == 100_000_000:
            i += 10_000_000; ctr3 = 10_000_000
        else:
            # I wonder if PyPy optimizes this modulus into products
            product = (product * i) % M
            i += 1; ctr1 += 1; ctr2 += 1; ctr3 += 1
    return product

if __name__ == '__main__': main()
