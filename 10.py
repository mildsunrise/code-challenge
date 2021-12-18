#!/usr/bin/env python3

from struct import unpack
from dpkt.pcap import Reader

def parse_frame(frame):
    ts, data = frame
    header = b'\xff\xff\xff\xff\xff\xff\x00\x00\x00\x00\x00\x00\x08\x00E\x00\x00\x1d\x00\x01\x00\x00@\x01|\xdd\x7f\x00\x00\x01\x7f\x00\x00\x01\x08\x00'
    assert data.startswith(header)
    data = data[len(header):]
    (checksum, id, seq), payload = unpack('>HHH', data[:6]), data[6:]
    assert len(payload) == 1
    return id, seq, payload[0]

with open('icmps.pcap', 'rb') as raw_cap:
    cap = Reader(raw_cap)
    data = list(map(parse_frame, cap))

# sort by sequence
by_seq = { seq: payload for id, seq, payload in data }
assert len(by_seq) == len(data)
data = bytes( by_seq[x] for x in range(min(by_seq), max(by_seq) + 1) )

with open('icmps.png', 'wb') as f:
    f.write(data)

# parse QR
# 1. parse, pad & scale image so ZBar will be happy
from io import BytesIO
from PIL import Image
orig_image = Image.open(BytesIO(data))
image = Image.new('L', (orig_image.width + 60, orig_image.height + 60), 127)
image.paste(orig_image, [x + 30 for x in orig_image.getbbox()])
image = image.resize((image.width * 15, image.height * 15))
# 2. scan it! (it's so nasty we have to do all this just to parse a QR)
import zbar
scanner = zbar.ImageScanner()
scanner.parse_config('enable')
image = zbar.Image(image.width, image.height, 'Y800', bytes(image.getdata()))
scanner.scan(image)
symbol, = image
print(symbol.data)
