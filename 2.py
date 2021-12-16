#!/usr/bin/env python3

# you said 'an empty space', but there are many tests using two spaces as separator for the columns

def main():
    for i in range(int(input())):
        P, R, C = map(int, input().split())
        names = [ input() for _ in range(P) ]
        rows = [ input().split() for _ in range(R) ]

        is_letter = lambda x: len(x) == 1 and ('A' <= x <= 'Z')
        assert all(len(row) == C and all(map(is_letter, row)) for row in rows)
        assert all(name and all(map(is_letter, name)) for name in names)

        ans = process_case(names, rows)
        print(f'Case #{i+1}: {ans}')

def process_case(names: list[str], rows: list[list[str]]):
    board = ''.join(sum(rows, []))
    # this is only challenge 2 so I'll just DFS in case there are dead ends.
    # you don't expect me to do something more efficient, I hope
    def remove_pokemon(names: tuple[str, ...], board: str):
        if not names:
            return board
        for idx, name in enumerate(names):
            for substr in (name, name[::-1]):
                if (pos := board.find(substr)) != -1:
                    new_names = names[:idx] + names[idx+1:]
                    new_board = board[:pos] + board[pos+len(substr):]
                    return remove_pokemon(new_names, new_board)
        raise AssertionError('unsolvable map')
    return remove_pokemon(tuple(names), board)

if __name__ == '__main__': main()
