#!/usr/bin/env python3

import math
import ast

def literal_eval(code: str, ast_fixup=lambda n: n):
    # we can't use ast.literal_eval() directly because it doesn't understand
    # divisions. so convert them to tuples first (which is also nice because
    # we can do fraction math instead of floating point)
    tree = ast.parse(code, mode='eval')
    tree = ast_fixup(RewriteDiv().visit(tree))
    return ast.literal_eval(tree)

class RewriteDiv(ast.NodeTransformer):
    def visit_BinOp(self, node):
        if isinstance(node.op, ast.Div):
            return ast.Tuple([ node.left, node.right ], ast.Load())
        return node

def fix_keywords(node):
    assert not node.body.args
    assert all(isinstance(x, ast.keyword) for x in node.body.keywords)
    xs = { x.arg: x.value for x in node.body.keywords }
    return ast.Dict([ ast.Constant(x) for x in xs.keys() ], list(xs.values()))

def main():
    for i in range(int(input())):
        words, scores = input().split('|')
        scores = scores.strip()
        words = words.split('-')
        assert len(words) == 2

        # parse scores into letter -> (num, denom)
        if scores[0] == '{':
            scores = literal_eval(scores)
        elif scores[0] == '[':
            scores = dict(literal_eval(scores))
        else:
            # this is *almost* valid python, just wrap it in a dict() call
            # and fix the AST because literal_eval doesn't understand it
            scores = literal_eval(f'dict({scores})', ast_fixup=fix_keywords)

        # normalize & validate types
        assert type(scores) is dict
        normalize_frac = lambda f: f if type(f) is tuple else (f, 1)
        scores = { k: normalize_frac(v) for k, v in scores.items() }
        valid_letter = lambda x: type(x) is str and len(x) == 1
        valid_frac = lambda x: type(x) is tuple and len(x) == 2 and all(type(v) is int for v in x) and x[1] != 0
        assert all(valid_letter(k) and valid_frac(v) for k, v in scores.items())

        # take out fractions
        denom = math.lcm(*(d for n, d in scores.values()))
        scores = { k: n * (denom // d) for k, (n, d) in scores.items() }

        # calculate result
        ans = process_case(words, scores)
        print(f'Case #{i+1}: {ans}')

def process_case(words: tuple[str, ...], scores: dict[str, int]):
    compute_score = lambda word: sum(scores[x] for x in word)
    sorted_words = sorted(((compute_score(word), word) for word in words), reverse=True)
    return '-' if sorted_words[0][0] == sorted_words[1][0] else sorted_words[0][1]

if __name__ == '__main__': main()
