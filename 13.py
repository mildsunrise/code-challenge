#!/usr/bin/env python3

import requests
import re
import gzip

from requests.models import HTTPBasicAuth

URL = 'http://codechallenge-daemons.0x14.net:13963/'
CREDS = 'plyba:xvyy_nyy_uhznaf'

# decode credentials

transform_letter = lambda x: (x + 13) % 26
def transform_char(x):
    if not ('a' <= x <= 'z'): return x
    x = ord(x) - ord('a')
    x = transform_letter(x)
    assert 0 <= x < 26
    x = chr(x + ord('a'))
    return x
CREDS = ''.join(map(transform_char, CREDS))

# make request

with requests.Session() as session:
    session.auth = HTTPBasicAuth(*CREDS.split(':'))

    assert session.get(URL).text.strip() == '''
<HTML>
<BODY>
Earth position is <a href="here-is-the-position">here</a>
</BODY>
</HTML>
    '''.strip()

    hexdump = session.get(URL + 'here-is-the-position').text

with open('13.out', 'w') as f:
    f.write(hexdump)

# parse hexdump

data = bytes()
for line in hexdump.splitlines():
    assert len(data) % 16 == 0
    offset, hexdump, junk = re.fullmatch(r'([0-9a-f]{8}): ((?:[0-9a-f ]{4} ){8}) (.{1,16})', line).groups()
    assert int(offset, 16) == len(data)
    hexdump = hexdump.strip()
    hexdump = ''.join( hexdump[i:i+4] for i in range(0, len(hexdump), 5) )
    assert re.fullmatch(r'[0-9a-f]+', hexdump)
    hexdump = bytes( int(hexdump[i:i+2], 16) for i in range(0, len(hexdump), 2) )
    assert len(hexdump) == len(junk) and all(map(str.isprintable, junk))
    data += hexdump

# decode data

data = gzip.decompress(data)
data = data.decode('utf-8')
data = [ x - 0x200b for x in map(ord, data) if x >= 128 and x != 0x2019 ]
assert all(x < 2 for x in data) and len(data) % 8 == 0
data = bytes(int(''.join(map(str, data[i:i+8])), 2) for i in range(0, len(data), 8))
print(data.decode('ascii'))
