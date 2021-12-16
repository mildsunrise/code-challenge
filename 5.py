src = open('Invictus.txt').read()
password = ''.join( chr(ord(x)-0xE002E) for x in src if not ord(x) < 0x80 )
print(password)
