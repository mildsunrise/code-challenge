#!/usr/bin/env python3

import socket
import math
from dataclasses import dataclass
from typing import Optional, TextIO
import copy
from collections import defaultdict

SERVER = ('codechallenge-daemons.0x14.net', 7162)


# MATH / UTILITIES
# ----------------

Prime = int
Factorization = dict[Prime, int]
add_factors = lambda a, b: { f: max(a.get(f, 0), b.get(f, 0)) for f in set(a) | set(b) }
intersect_factors = lambda a, b: { f: v for f in set(a) & set(b) if (v := min(a[f], b[f])) }

is_prime = lambda x: all(x % m != 0 for m in range(2, math.isqrt(x)+1))

def factorize(n: int, primes: list[int]) -> Factorization:
    assert n > 0
    primes_iter = iter(primes)
    factors = {}
    while n != 1:
        prime = next(primes_iter)
        exp = 0
        while n % prime == 0:
            n //= prime
            exp += 1
        if exp:
            factors[prime] = exp
    return factors


# COMMUNICATION LAYER
# -------------------

class RemoteJudge(object):
    conn: socket.socket
    connfile: TextIO
    N: int
    Q: int

    def __init__(self):
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        self.conn.settimeout(5)
        self.conn.connect(SERVER)
        self.connfile = self.conn.makefile('wr', buffering=2048, encoding='ascii')

        self.N, self.Q = map(int, self.connfile.readline().split())
        self.queries = 0

    def make_query(self, a: int, b: int) -> int:
        assert all(type(x) is int and 1 <= x <= self.N for x in (a, b))
        assert a != b
        self.queries += 1
        assert self.queries <= self.Q, f'query limit ({self.Q}) exceeded'

        self.connfile.write(f'? {a} {b}\n')
        self.connfile.flush()
        line = self.connfile.readline()
        try:
            return int(line)
        except ValueError:
            raise ValueError(f'received {repr(line.strip())}') from None

    def send_answer(self, ixs: set[int]):
        ixs = ' '.join(map(str, sorted(ixs)))
        self.connfile.write(f'! {ixs}\n')
        self.connfile.flush()
        line = self.connfile.readline()
        # TODO
        raise ValueError(f'received {repr(line.strip())}')


# SOLVER STATE
# ------------

@dataclass
class CellState(object):
    min_factors: int
    max_factors: int
    domain: set[int]
    is_target: Optional[bool]

    def add_factors(self, n: int):
        self.min_factors = math.lcm(self.min_factors, n)
    def restrict_factors(self, n: int):
        self.max_factors = math.gcd(self.max_factors, n)

    def check_max(self, n: int) -> bool:
        return self.max_factors % n == 0
    def check_min(self, n: int) -> bool:
        return n % self.min_factors == 0

    def check(self):
        assert self.domain
        assert self.max_factors % self.min_factors == 0

@dataclass
class SolverState(object):
    # precalculated info depending on N and Q, never touched
    primes: list[int]
    indexes: dict[int, Factorization]
    targets: set[int]

    # absolute info we have from server; rules do not touch this
    queries: dict[tuple[int, int], int]

    cells: dict[int, CellState]

    @staticmethod
    def initial(N: int):
        primes = [ p for p in range(2, N + 1) if is_prime(p) ]
        indexes = { k: factorize(k, primes) for k in range(1, N + 1) }
        targets = set( k for k, factors in indexes.items() if sum(factors.values()) <= 1 )
        domain, max_factors = set(indexes), math.lcm(*indexes)
        return SolverState(primes, indexes, targets, queries={}, cells={
            k: CellState(1, max_factors, domain.copy(), None) for k in domain })

    def dump(self):
        print('-- SOLVER STATE --')
        print(f'{len(self.queries)} queries')
        for (a, b), common in self.queries.items():
            print(f' - {a}, {b} = {common}')
        print(f'{len(self.cells)} cells')
        indexes = self.indexes
        initial_cell = CellState(1, math.lcm(*indexes), set(indexes).copy(), None)
        for c, cell in self.cells.items():
            if cell == initial_cell:
                continue
            label, domain = ('ONLY', cell.domain) if len(cell.domain) < len(indexes) / 2 \
                else ('DISCARDED', set(indexes) - cell.domain)
            domain = f'{len(domain)} {label}: ' + ", ".join(map(str, sorted(domain)))
            target = { True: 'YES', False: 'NO', None: '' }[cell.is_target]
            print(f' [{c:3}] = {cell.min_factors:3} - {cell.max_factors:3}   {target:3}   {domain}')
        print()

    def check(self):
        assert set().union(*(c.domain for c in self.cells.values())) == set(self.indexes)
        for c in self.cells.values(): c.check()


# SOLVER RULES
# ------------

# it really looks like I want a SAT solver here,
# but I find it hard to adapt to the strategy part

def queries_to_factors(st: SolverState):
    '''discover factor restrictions from queries'''
    for cells, common in st.queries.items():
        # factors that are in query -> in both A and B
        for c in cells:
            st.cells[c].add_factors(common)

        # factors that are in A but not in query -> not in B
        for a, b in (cells, cells[::-1]):
            ref = st.cells[a].min_factors
            ref //= math.gcd(ref, common)
            b_max = factorize(st.cells[b].max_factors, st.primes)
            for f, v in st.indexes[ref].items():
                b_max[f] = min(b_max.get(f, 0), v)
            st.cells[b].max_factors = math.prod(f**v for f, v in b_max.items())

def factors_to_domain(st: SolverState):
    '''discover domain restrictions from factors'''
    for cell in st.cells.values():
        cell.domain = { i for i in cell.domain if cell.check_min(i) and cell.check_max(i) }

def domain_to_factors(st: SolverState):
    '''discover factor restrictions from domain'''
    for cell in st.cells.values():
        cell.restrict_factors(math.lcm(*cell.domain))
        cell.add_factors(math.gcd(*cell.domain))

def domain_exclusivity(st: SolverState):
    '''discover new domain restrictions from exclusivity'''
    # look for cells that can only accept some values
    domains: dict[frozenset[int], list[int]] = defaultdict(lambda: [])
    for c, cell in st.cells.items():
        domains[frozenset(cell.domain)].append(c)
    for domain, cells in domains.items():
        assert len(domain) >= len(cells)
        if len(domain) == len(cells):
            for other in set(st.indexes) - set(cells):
                st.cells[other].domain.difference_update(domain)

    # look for values that can only be accepted on some cells
    acceptors_by_val: dict[int, set[int]] = defaultdict(lambda: set())
    for c, cell in st.cells.items():
        for i in cell.domain:
            acceptors_by_val[i].add(c)
    acceptors: dict[frozenset[int], set[int]] = defaultdict(lambda: set())
    for i, cells in acceptors_by_val.items():
        acceptors[frozenset(cells)].add(i)
    for cells, domain in acceptors.items():
        assert len(cells) >= len(domain)
        if len(cells) == len(domain):
            for cell in cells:
                st.cells[cell].domain &= domain

def domain_to_target(st: SolverState):
    '''discover target status from domain'''
    for cell in st.cells.values():
        possibilities = { i in st.targets for i in cell.domain }
        if len(possibilities) == 1:
            is_target = next(iter(possibilities))
            assert cell.is_target in { None, is_target }
            cell.is_target = is_target

    # we could do some more advanced stuff by expanding the domain
    # exclusivity rule, but I think we're fine

    counts = defaultdict(lambda: 0)
    for cell in st.cells.values():
        if cell.is_target != None:
            counts[cell.is_target] += 1

    expected_counts = { True: len(st.targets), False: len(st.indexes) - len(st.targets) }
    for value, count in counts.items():
        assert count <= expected_counts[value]
        if count == expected_counts[value]:
            for cell in st.cells.values():
                if cell.is_target == None:
                    cell.is_target = not value


# STRATEGY & MAIN LOOP
# --------------------

def solve(st: SolverState):
    '''use solver rules to deduce new info'''
    # performance isn't an issue here, so do everything possible
    # until there's nothing else to do (with the info we have)
    while True:
        old_st, st = st, copy.deepcopy(st)
        queries_to_factors(st)
        factors_to_domain(st)
        domain_to_factors(st)
        domain_exclusivity(st)
        domain_to_target(st)
        if st == old_st: break
    st.check()
    return st

def pick_query(st: SolverState) -> tuple[int, int]:
    '''given a solver state, pick the next query'''
    # the solver seems to be smart enough so I haven't thought
    # much about this part tbh. I just pick the cell with more
    # factors + the more 'interesting' cell
    # TODO

def main():
    judge = RemoteJudge()
    print(f'Connected: N = {judge.N}, Q = {judge.Q}')

    state = SolverState.initial(N=judge.N)

    while True:
        state = solve(state)
        state.dump()
        if all(c.is_target != None for c in state.cells.values()):
            break

        query = sorted(pick_query(state))
        result = judge.make_query(*query)
        assert result in state.indexes
        print(f'Picked query {query}, received: {result}')
        state.queries[query] = result

    answer = { c for c, cell in state.cells.items() if cell.is_target }
    print(f'Found answer in {len(state.queries)}:', answer)

if __name__ == '__main__': main()
