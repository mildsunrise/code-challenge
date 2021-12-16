#!/usr/bin/env python3

from enum import Enum
import socket
from io import TextIOWrapper
from re import fullmatch
from collections import deque
from typing import Callable

SERVER = ('codechallenge-daemons.0x14.net', 4321)

# light vector type / math

Point = tuple[int, int]
point_add: Callable[[Point, Point], Point] = lambda x, y: (x[0] + y[0], x[1] + y[1])
point_sub: Callable[[Point, Point], Point] = lambda x, y: (x[0] - y[0], x[1] - y[1])
point_neg: Callable[[Point], Point] = lambda x, k: (-x[0], -x[1])
point_scale: Callable[[Point, int], Point] = lambda x, k: (x[0] * k, x[1] * k)

# communication layer

def safe_fullmatch(pattern, x):
    m = fullmatch(pattern, x)
    assert m != None, f'{repr(x)} does not match pattern {repr(pattern)}'
    return m

conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
conn.settimeout(5)
conn.connect(SERVER)
connfile = conn.makefile('wr', buffering=2048, encoding='ascii')

banner = connfile.readline() + connfile.readline()
assert banner == '''
Welcome, my friend! You are at the beginning of a long dark dungeon. What do you want to do? Enter order (empty line or 'bye' for finish):
north - south - east - west - look - where am I - go to x,y - is exit? - bye
'''[1:], f'banner is {repr(banner)}'

def send_command(command: str) -> str:
    connfile.write(command + '\n')
    connfile.flush()
    line = connfile.readline()
    assert line[-1] == '\n', 'unexpected EOF'
    timeout_message = 'Oh, no! You took too much time to exit. An orc caught you. The beast nails his orc sword in your chest. You die in the darkness of the maze...'
    assert line != timeout_message, 'ran out of time'
    return line[:-1]

class Direction(Enum):
    west  = (+1,  0)
    east  = (-1,  0)
    north = ( 0, +1)
    south = ( 0, -1)

def look() -> set[Direction]:
    output = send_command('look')
    dirs, = safe_fullmatch(r'Well, well, well, my friend. You could do these movements: (.+)', output).groups()
    dirs = [ Direction[x] for x in dirs.split() ]
    dirs_set = set(dirs)
    assert len(dirs) == len(dirs_set)
    return dirs_set

def move(direction: Direction) -> Point:
    assert isinstance(direction, Direction)
    output = send_command(direction.name)
    if output == "Ouch. It seems you can't go there":
        raise ValueError('invalid direction')
    x, y = safe_fullmatch(r'Great movement\. Here is your new position: \((\d+), (\d+)\)', output).groups()
    return (int(x), int(y))

def goto(dest: Point):
    output = send_command(f'go to {dest[0]},{dest[1]}')
    if output == "Not allowed. You can't go to a not checked position":
        raise ValueError('invalid position, not checked')
    x, y = safe_fullmatch(r'Great movement\. Here is your new position: \((\d+), (\d+)\)', output).groups()
    assert dest == (int(x), int(y))

def where_am_i() -> Point:
    output = send_command('where am I')
    x, y = safe_fullmatch(r'\((\d+), (\d+)\)', output).groups()
    return (int(x), int(y))

def is_exit() -> bool:
    output = send_command('is exit?')
    return {
        'No. Sorry, traveller...': False,
        'Yes. Congratulations, you found the exit door': True,
    }[output]

# now, the search. given that we don't know the exit coordinates
# there's no heuristic, so the safest bet is probably to do a BFS:

start = where_am_i()
checked: dict[Point, Point] = { start: None }
pending: deque[Point] = deque([start])

while pending:
    node = pending.popleft()
    goto(node)
    if is_exit(): break
    for direction in look():
        dest = point_add(node, direction.value)
        if dest in checked: continue
        checked[dest] = node
        pending.append(dest)
else:
    raise AssertionError('exit is not reachable')

# print path to start

path = [node]
while node := checked[path[-1]]:
    path.append(node)
print(', '.join(map(str, path[::-1])))
