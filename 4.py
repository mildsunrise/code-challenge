#!/usr/bin/env python3

import itertools

def main():
    for i in range(int(input())):
        root = parse_note(input())
        scale = parse_scale(input())
        ans = process_case(root, scale)
        print(f'Case #{i+1}: {ans}')


# parse a scale spec (like TTTsTTs) into a list of note offsets

def parse_scale(scale: str) -> int:
    scale = [ { 's': 1, 'T': 2 }[x] for x in scale ]
    *offsets, span = itertools.accumulate(scale)
    assert span == 12 and len(scale) == 7
    return [0] + offsets

MAJOR_SCALE = parse_scale('TTsTTTs')


# parse(/format) a note spec (like A#) into (letter number, shift)
# letter number is an index of C major scale; shift is -1, 0, +1

parse_note = lambda x: (REV_LETTERS[x[0]], REV_SHIFTS[x[1:]])
format_note = lambda x: LETTERS[x[0] % 7] + SHIFTS[x[1]]

LETTERS = [ chr(ord('A') + (n + 2) % 7) for n in range(7) ]
REV_LETTERS = { v: k for k, v in enumerate(LETTERS) }

SHIFTS = { -1: 'b', 0: '', +1: '#' }
REV_SHIFTS = { v: k for k, v in SHIFTS.items() }


# compute a note number (mod 12, centered at C) from a note spec, and vice versa.
# the reverse operation needs a 'base' letter number to select from possible alternatives

spec_to_note = lambda spec: MAJOR_SCALE[spec[0] % 7] + spec[1]
note_to_spec = lambda note, base: (base, note_offset(note, MAJOR_SCALE[base % 7]))

note_offset = lambda note, base: ((note - base) + 6) % 12 - 6
get_possible_bases = lambda note: { i for i, base in enumerate(MAJOR_SCALE)
    if -1 <= note_offset(note, base) <= +1 }


# format a scale from a root note spec

def process_case(root: tuple[int, int], scale: list[int]):
    # they want the root note repeated at the end
    scale = scale + [0]

    # calculate the note number of every note in the scale
    scale = [ spec_to_note(root) + x for x in scale ]

    def format_scale(base):
        # calcuate the specs of each note, using sequential letters starting from base
        specs = [ note_to_spec(note, base + i) for i, note in enumerate(scale) ]
        # if the shifts are all valid, then we can format the scale in this base
        if all(-1 <= spec[1] <= +1 for spec in specs):
            return ''.join(format_note(spec) for spec in specs)

    # if possible, format the scale in the same letter we were given
    bases = get_possible_bases(spec_to_note(root))
    bases = sorted(bases, key=lambda x: x != root[0])
    return next(filter(lambda x: x, map(format_scale, bases)))


if __name__ == '__main__': main()
