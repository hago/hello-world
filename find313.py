#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai

import sys

def isupper(ch):
    return ch >= 'A' and ch <= 'Z'
    
def islower(ch):
    return ch >= 'a' and ch <= 'z'

def loadbuf(fp, buf, n):
    newbuf = buf[n:]
    i = 0
    while i < n:
        while True:
            c = fp.read(1)
            if c!='\r' and c!='\n':
                break
        if c=='':
            break
        newbuf+=c
        i+=1
    print "to read %d loading buf %s" % (n, newbuf)
    return newbuf

def find(fp):
    toread = 7
    buf = ' ' * 7
    ret = []
    while True:
        buf = loadbuf(fp, buf, toread)
        if buf=='' or len(buf)<7:
            break
        if not islower(buf[3]):
            toread = 1
            continue
        if not isupper(buf[0]) or not isupper(buf[1]) or not isupper(buf[2]):
            toread = 4
            continue
        if not isupper(buf[4]):
            toread = 5
            continue
        if not isupper(buf[5]):
            toread = 6
            continue
        if not isupper(buf[6]):
            toread = 7
            continue
        ret.append(buf)
        toread = 4
    return ret
    
if __name__=="__main__":
    fp = open(sys.argv[1], "rb")
    x = find(fp)
    fp.close()
    print x