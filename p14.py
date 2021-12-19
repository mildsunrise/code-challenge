#!/usr/bin/env python3

import sys
import re
from math import gcd
from typing import Literal, Union
from functools import reduce
from z3 import Int, IntVal, Or, Solver, unsat


# PARSING
# -------

def main():
    for i in range(int(input())):
        ans = process_case(input())
        print(f'Case #{i+1}: {ans}')

# an expression is either a string (sequence of letters),
# an int (numeric constant) or a (op, a, b) tuple with `op`
# being one of '+-/*' and `a`, `b` being the operand expressions
Expression = Union[str, int, tuple[str, 'Expression', 'Expression']]

def parse_equation(eq: str) -> Expression:
    # since we only have 2 values, we can write it as a - b = 0
    # and this way we avoid having an Equation type
    exprs = eq.split('=')
    assert len(exprs) == 2
    return ('-',) + tuple(map(parse_expression, exprs))

def parse_expression(expr: str) -> Expression:
    # parse stream of values and operators
    value, expr = parse_value(expr)
    items = [value]
    while expr := expr.lstrip():
        op, expr = expr[0], expr[1:].lstrip()
        if op not in '+-*/':
            raise ValueError('expected operator')
        value, expr = parse_value(expr)
        items.extend([ op, value ])
    # group operators by priority
    for ops in [ '*/', '+-' ]:
        pos = 0
        while pos + 1 < len(items):
            a, op, b = items[pos:pos+3]
            if op in ops:
                items = items[:pos] + [(op, a, b)] + items[pos+3:]
            else:
                pos += 2
    assert len(items) == 1
    return items[0]

def parse_value(expr: str) -> tuple[str, Expression]:
    expr = expr.lstrip()
    if expr.startswith('('):
        if (idx := expr.index(')')) == -1:
            raise ValueError('unclosed parenthesis')
        return parse_expression(expr[1:idx]), expr[idx+1:]
    if m := re.match(r'[A-Z]+', expr):
        return expr[:m.end()], expr[m.end():]
    if m := re.match(r'\d+', expr):
        return int(expr[:m.end()]), expr[m.end():]
    raise ValueError('expected value')


# SIMPLIFICATION
# --------------

# SMT solvers should be able to handle these equations
# except for divisions, which are non-linear, but these
# are trivial to remove from the equation

ExpressionPath = tuple[tuple[str, int, Expression], ...]
ExpressionZipper = tuple[ ExpressionPath, Expression ]
def zip_one(zipper: ExpressionZipper, idx: Literal[0, 1]):
    path, (op, a, b) = zipper
    return path + ((op, idx, [b, a][idx]),), [a, b][idx]
def unzip_one(zipper: ExpressionZipper) -> ExpressionZipper:
    (*path, (op, idx, val)), expr = zipper
    return tuple(path), (op,) + [(expr, val), (val, expr)][idx]
unzip = lambda zipper: zipper[1] if not zipper[0] else unzip(unzip_one(zipper))

def remove_divisions(zipper: ExpressionZipper) -> tuple[ExpressionZipper, list[Expression]]:
    path, expr = zipper
    divisors = []
    if type(expr) is tuple:
        for idx in range(1 if expr[0] == '/' else 2):
            zipper, subdivisors = remove_divisions(zip_one(zipper, idx))
            zipper, divisors = unzip_one(zipper), divisors + subdivisors
        path, (op, dividend, divisor) = zipper
        if op == '/':
            new_val = lambda op, val: val if op == '*' else ('*', val, divisor)
            path = tuple((op, idx, new_val(op, val)) for op, idx, val in path)
            zipper, divisors = (path, dividend), divisors + [divisor]
    return zipper, divisors

def read_factors(expr: Expression) -> list[Expression]:
    if type(expr) == tuple and expr[0] == '*':
        for subexpr in expr[1:3]:
            yield from read_factors(subexpr)
    else:
        yield expr
def sort_factors(x: Expression) -> tuple[int, list[Expression]]:
    integral, others = 1, []
    for f in read_factors(x):
        if type(f) is int:
            integral *= f
        else:
            others.append(f)
    return integral, others
def merge_factors(factors: tuple[tuple[int, list[Expression]]]):
    integral, others = zip(*factors)
    c_integral = gcd(*integral)
    integral = [ x // c_integral for x in integral ]
    c_others = []
    while tmp := set.intersection(*map(set, others)):
        for f in tmp:
            for o in others:
                o.remove(f)
            c_others.append(f)
    join_factors = lambda fs: ([] if fs[0] == 1 else [fs[0]]) + fs[1]
    return join_factors((c_integral, c_others)), tuple(map(join_factors, zip(integral, others)))
def common_factor(expr: Expression) -> Expression:
    if type(expr) is tuple:
        expr = expr[:1] + tuple(map(common_factor, expr[1:]))
        if expr[0] == '+' or expr[0] == '-':
            factors = tuple(map(sort_factors, expr[1:3]))
            common, operands = merge_factors(factors)
            build_factors = lambda fs: reduce(lambda expr, f: ('*', expr, f), fs or [1])
            expr = (expr[0],) + tuple(map(build_factors, operands))
            expr = build_factors(common + [expr])
    return expr

def remove_constants(expr: Expression) -> Expression:
    if type(expr) is tuple:
        expr = expr[:1] + tuple(map(remove_constants, expr[1:]))
        ident = { '+': 0, '-': 0, '*': 1, '/': 1 }[expr[0]]
        if expr[2] == ident: return expr[1]
        if expr[0] in '+*':
            if expr[1] == ident: return expr[2]
        if expr[0] in '*' and expr[1] == 0 or expr[2] == 0:
            return 0
        if type(expr[1]) is int and type(expr[2]) is int:
            return eval_expr(expr, None)
    return expr

def simplify(expr: Expression) -> tuple[Expression, list[Expression]]:
    divisors = []
    while (result := remove_divisions(((), expr)))[1]:
        (_, expr), subdivisors = result
        divisors += subdivisors    

    def simplify_pass(expr: Expression) -> Expression:
        (_, expr) = common_factor(((), expr))
        return remove_constants(expr)
        # FIXME: combine constants (in sums only) and negates
    while (tmp := simplify_pass(expr)) != expr:
        expr = tmp

    return expr, divisors


# SOLVING
# -------

def process_case(equation: str) -> int:
    # transform parsed equation into Z3 LIA equation

    variables = {}
    def get_variable(x: str):
        if x not in variables:
            variables[x] = Int(x)
        return variables[x]
    zero_forbidden = set()

    def transform_expression(x: Expression):
        if type(x) is str:
            if len(x) > 1:
                zero_forbidden.add(x[0])
            return reduce(lambda out, var: out * 10 + var, map(get_variable, x))
        if type(x) is tuple:
            op, *vs = x
            a, b = map(transform_expression, vs)
            return { '+': lambda: a + b, '-': lambda: a - b, '*': lambda: a * b }[op]()
        if type(x) is int:
            return IntVal(x)
        raise AssertionError()

    # set up the solver with the transformed equation + constraints

    expr = original_expr = parse_equation(equation)
    expr, divisors = simplify(expr)

    solver = Solver()
    solver_expr = Or(*(transform_expression(factor) == 0
        for factor in set(read_factors(expr))))
    solver.add(solver_expr)
    for divisor in divisors:
        solver.add(transform_expression(divisor) != 0)

    for l, var in variables.items():
        solver.add( var >= (1 if l in zero_forbidden else 0) )
        solver.add( var < 10 )

    assert len(variables) <= 10
    keys = list(variables)
    for idx1 in range(len(keys)):
        for idx2 in range(idx1):
            solver.add(variables[keys[idx1]] != variables[keys[idx2]])

    # enumerate possible solutions

    solutions = []
    while True:
        status = solver.check()
        if status == unsat: break
        assert status == sat, f'solver returned {sat}'

        model = solver.model()
        trans = { l: str(model.eval(var)) for l, var in variables.items() }
        solution = ''.join( trans.get(l, l) for l in equation )
        if check_expr(original_expr, trans):
            solutions.append(solution)
        else:
            print(f'WARNING: skipping solution {solution} as it does not verify...', file=sys.stderr)

        solver.add(Not(And(*( var == model.eval(var) for var in variables.values() ))))

    return ';'.join(sorted(solutions)) if solutions else 'IMPOSSIBLE'

def eval_expr(expr: Expression, trans: dict[str, str]) -> int:
    if type(expr) is str:
        assert len(expr) == 1 or trans[expr[0]] != 0
        return int(''.join( trans[x] for x in expr ))
    if type(expr) is int:
        return expr
    if type(expr) is tuple:
        a, b = (eval_expr(x, trans) for x in expr[1:])
        def safe_div():
            q, m = divmod(a, b)
            if m: raise ValueError('invalid division')
            return q
        ops = { '+': lambda: a + b, '-': lambda: a - b, '*': lambda: a * b, '/': safe_div }
        return ops[expr[0]]()
    raise AssertionError()

def check_expr(expr: Expression, trans: dict[str, str]):
    assert len(set(trans.values())) == len(trans)
    assert all(len(v) == 1 for v in trans.values())
    try:
        return eval_expr(expr, trans) == 0
    except ValueError:
        return False

if __name__ == '__main__': main()
