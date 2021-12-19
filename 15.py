#!/usr/bin/env python3

from itertools import count
import sys

def main():
    from time import time
    import pickle
    global primes
    if False:
        s = time()
        find_primes()
        print('Primes calculated.', file=sys.stderr)
        print(f'in {time()-s:.2f}s')
        with open('primes.pkl', 'wb') as f:
            pickle.dump(primes, f)
    else:
        with open('primes.pkl', 'rb') as f:
            primes = pickle.load(f)
    for i in range(int(input())):
        ans = process_case(int(input()))
        print(f'Case #{i+1}: {ans}')

M = 10**8 + 7  # prime


# PREPROCESSING
# -------------

primes = []
def find_primes(word_bytes: int = 1):
    '''precalculate primes < M using sieve of eratosthenes'''
    # reserve memory
    memory = bytearray((M // 2 // 8 // 8 + 1) * 8)
    view = memoryview(memory).cast({ 1: 'B', 2: 'H', 4: 'I', 8: 'Q'}[word_bytes])

    # initialize it
    wide_view = memoryview(memory).cast('Q'); wide_value = ~((~0) << 64)
    for o in range(len(wide_view)): wide_view[o] = wide_value

    # go!
    primes.append(2)
    word_bits = word_bytes * 8; word_bits_2 = word_bits * 2
    size_mask = word_bits - 1; size_shift = size_mask.bit_length()
    o = 0; p = 3; P = (M - 3) // 2

    def mark_prime():
        primes.append(p)
        n = (p - 3) // 2
        while n < P:
            o = n >> size_shift; bit = n & size_mask
            view[o] &= ~(1 << bit)
            n += p

    while p < M:
        if view[o] == 0:
            o += 1; p += word_bits_2
            continue
        bit = 0
        while bit < word_bits:
            if (view[o] >> bit) & 1:
                mark_prime()
            bit += 1; p += 2
        o += 1


# CASE LOGIC
# ----------

# basic modular arithmetic

mod_prod = lambda a, b: (a * b) % M

def mod_div(a, b):
    d, x, _ = egcd(b, M)
    q, r = divmod(a, d)
    assert not r, 'division not possible'
    return mod_prod(q, x)

def egcd(a, b):
    '''extended euclidean algorithm'''
    a = (a, 1, 0)
    b = (b, 0, 1)
    while True:
        q, r = divmod(a[0], b[0])
        if not r: return b
        a, b = b, (r, a[1] - q*b[1], a[2] - q*b[2])

# modular factorial calculation

def mod_factorial(n: int, m: int=0):
    '''calculates (n! / m!) mod M'''
    assert n >= m
    result = 1
    for prime in primes:
        if prime > n: break
        exp = get_factorial_exponent(prime, n) - get_factorial_exponent(prime, m)
        result = mod_prod(result, pow(prime, exp, M))
    return result

def get_factorial_exponent(prime: int, n: int):
    '''get maximum p for which `prime^p | n!` using Legendre's formula'''
    p = 0
    while n:
        n //= prime
        p += n
    return p

# main logic

def process_case(n: int) -> int:
    # M is not a tuentistic number, so if it gets included
    # the product drops to 0
    if n >= M: return 0

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
            product = mod_prod(product, i)
            i += 1; ctr1 += 1; ctr2 += 1; ctr3 += 1
    return product

    # I think we're just going to multiply all tuenstistic numbers
    # up to n, then take that out of n!
    tuentistic_product = 1
    print('factorial...')
    factorial = mod_factorial(n)

    from time import time
    t = time()
    print('rest of product...', n)
    i = 0
    ctr1, ctr2, ctr3 = 80, 80 * 1000, 80 * 1000**2
    while i < n:
        if ctr1 == 100:
            end = i + 10
            while i < end:
                tuentistic_product = mod_prod(tuentistic_product, i)
                i += 1
            ctr1 = 10; ctr2 += 10; ctr3 += 10
        elif ctr2 == 100_000:
            end = i + 10_000
            while i < end:
                tuentistic_product = mod_prod(tuentistic_product, i)
                i += 1
            ctr2 = 10_000; ctr3 += 10_000
        elif ctr3 == 100_000_000:
            end = i + 10_000_000
            while i < end:
                tuentistic_product = mod_prod(tuentistic_product, i)
                i += 1
            ctr3 = 10_000_000
        else:
            i += 1; ctr1 += 1; ctr2 += 1; ctr3 += 1
    print(f'took {time()-t:.2f}s')

    return mod_div(factorial, tuentistic_product)

if __name__ == '__main__': main()
