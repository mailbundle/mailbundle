#!/usr/bin/python3
import sys
import email

v = []
m = email.message_from_binary_file(sys.stdin.buffer)
for hdr in ('to', 'from', 'cc'):
    r = m.get_all(hdr, [])
    for addr in r:
        v.append(email.utils.parseaddr(addr))
for realname, addr in v:
    print('%s\t%s' % (addr, realname.replace('\t', ' ')))
