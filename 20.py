#!/usr/bin/env python3

from typing import BinaryIO, Iterator
from io import BytesIO
import re

import requests
import numpy as np
from PIL import Image
import gzip
import hashlib


# PART 1: Decipher the line

def trace_line(im, start=(81,114), end=None, color_distance_limit=8, overrides={}) -> list[tuple[int, int]]:
    ''' trace a line of pixels on an image, returning a list of positions '''

    neighbors = [ (i, j) for i in [-1,0,+1] for j in [-1,0,+1] if i or j ]
    corners = [ x for x in neighbors if (x[0]^x[1]) & 1 == 0 ]
    cross   = [ x for x in neighbors if (x[0]^x[1]) & 1 == 1 ]

    get_pixel = lambda x: im[tuple(x)[::-1]].astype('int')
    color_distance = lambda c1, c2: ((c1 - c2) ** 2).sum() ** .5
    colors_match = lambda *pixels: color_distance(*map(get_pixel, pixels)) < color_distance_limit

    valid_neighbor = lambda x: tuple(x) not in path[-5:] and colors_match(x, position)
    adjust_offset = lambda dx: \
        np.array(dx)*2 if tuple(position + dx) in path[:-5] and dx in cross else dx
    get_neighbors = lambda xs: \
        [ x for dx in xs if valid_neighbor(x := position + adjust_offset(dx)) ]

    position = np.array(start)
    path = []

    while True:
        path.append(tuple(position))
        if override := overrides.get(tuple(position)):
            position = np.array(override)
            continue
        neighbors = get_neighbors(cross) or get_neighbors(corners)
        if not neighbors: break
        assert len(neighbors) == 1
        position = neighbors[0]

    if end: assert tuple(position) == end
    return path

def decipher_image(url: str, **trace_args) -> bytes:
    # load image
    im = requests.get(url).content
    with open(url.split('/')[-1], 'wb') as f:
        f.write(im)
    im = np.array(Image.open(BytesIO(im), formats=['png']))

    # trace line; assemble LSBs of the traced pixels to get payload
    path = trace_line(im, **trace_args)
    colors = [ im[position[::-1]] for position in path ]
    bits = [ channel & 1 for color in colors for channel in color ]
    data = bytes( int(''.join(map(str, bits[i:i+8])), 2) for i in range(0, len(bits)-7, 8) )

    # unwrap payload
    idx = data.index(b'\n\n')
    header, payload = data[:idx], data[idx+2:]
    size = int(re.fullmatch(r'size_in_bytes: (\d+)', header.decode()).group(1))
    assert size <= len(payload)
    payload, padding = payload[:size], payload[size:]
    return payload

url1 = 'https://codechallenge.0x14.net/resources/img/hidden_toy_story.png'
url2 = 'https://codechallenge.0x14.net/resources/img/9788b1d0ecc849920aae9aa182e8ce54088d3684f2af994d1525223f313318c6.png'
url3 = 'https://codechallenge.0x14.net/resources/img/056deccabd65794ad9f54c379c03912b2c81d60938a5e7c85086e45094e93a5c.png'

payload1 = decipher_image(url1, end=(105,116),
    color_distance_limit=10, overrides={ (119,147): (119,146) })
assert payload1.decode() == f'''
Congratulations, you seem to have the attitude to be a real hacker but luckily for you there seems to be more than one tablet and your thirst for curiosity forces you to inspect this one. The new tablet can be found at {url2}

PS: Every good hacker has to keep learning so you might be interested to see https://www.youtube.com/watch?v=qLCE8spVX9Q
'''[1:]

payload2 = decipher_image(url2, end=(106,117))
payload2 = gzip.decompress(payload2)
assert payload2.decode() == f'''
Even the new color e-books do not have support for such a wide color gamut, although I doubt they will compress the result using gzip. Unfortunately it looks like there is only one more tablet left so the fun is time limited, you can find it at {url3}
'''[1:]

payload3 = decipher_image(url3, end=(106,118))


# PART 2: Softdisk Library Format 'compression'

def dissect(file: BinaryIO) -> Iterator[tuple[bool, bytes]]:
    ''' dissects a stream into literals and pointers '''
    while True:
        block = file.read(1)[0]
        for i in range(8):
            if (block >> i) & 1:
                literal = file.read(1)
                assert len(literal) == 1
                yield True, literal
            else:
                pointer = file.read(2)
                if not pointer:
                    assert not (block >> i)
                    return
                assert len(pointer) == 2
                yield False, pointer

def decompress(file: BinaryIO) -> bytes:
    output = b' ' * 18
    for is_literal, data in dissect(file):
        if is_literal:
            output += data
            continue
        offset, length = decode_command(data)
        offset += 18  # yes, again
        assert 0 <= offset and offset + length <= len(output)
        output += output[offset : offset+length]
    return output[18:]

def decode_command(cmd: bytes) -> tuple[int, int]:
    length = cmd[1] & 0b1111
    offset = (cmd[1] >> 4) << 8 | cmd[0]
    offset |= -(offset >> 11) << 11
    return offset + 18, length + 3

message = decompress(BytesIO(payload3))

assert message.decode() == '''
> Toys in the Attic
>     Jet: Humans are meant to work and sweat to earn a living. Those that try to get rich quick or live at the expense of others, all get divine retributions somewhere along the line. That's the lesson. Unfortunately we quickly forget the lessons we learned. And then we have to learn them all over again.
>     Edward: Lesson lesson. If you see a stranger, follow him.
>     Spike: So that's the story. and what was the real lesson? Don't leave things in the fridge.

And that's it, you've finally made it this far, the secret of life is 42 and the secret of the game the sha256 of this message.

We wait for you in the final n.n

PS: The secret must look like this 90d3d5b1b846e0eec8da94cd171eba31a5da381ac56b4a26f0a82c6c01d29c4a
'''[1:]

print(hashlib.sha256(message).digest().hex())
