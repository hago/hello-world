#!/usr/bin/env python3
# vim: set fileencoding: UTF-8 -*-

'''
This script is to create a batch of ffmpeg commands those will convert all video files from specified
directory to an mp4 with video encoded in H.265, with bitrate set as 2 / 3 of the original for H.264,
and 50% for the other video codecs.
'''

import math
import os
import os.path
import sys

from pyffprobe import probe

CMDS = []

def parsefile(f: str):
    if f.endswith('.hevc.mp4'):
        return
    if not f.endswith(".mp4") and not f.endswith(".mkv"):
        print("skip file %s" % f)
        return
    print("run %s" % f)
    info = probe(f)
    for st in info.streams:
        if not st.isvideo() and not st.isaudio():
            print("skip codec %s" % st.codec.name)
            continue
        if st.isaudio():
            if st.codec.name not in ('mp3', 'aac'):
                print('warn: audio codec %s' % st.codec.name)
            continue
        if st.codec.name != 'h264':
            print('warn: skip non-h264 codec: %s' % st.codec.name)
            continue
        (fn0, ext) = os.path.splitext(f)
        fn = fn0.replace('"', '\\"')
        if st.codec.bitrate == None:
            print("unknown bit rate: %s for a video stream, skip\r\n" % st.codec.bitrate)
            continue
        br265 = __calch265btr(int(st.codec.bitrate))
        cmd = '''ffmpeg -i "%s%s" -c:v hevc -b:v %dk -c:a copy "%s.hevc.mp4"''' % (fn, ext, br265, fn)
        print(cmd)
        CMDS.append(cmd)
        CMDS.append("sleep 10")
        break

def __calch265btr(h264btr: int, ratio = 2 / 3, roundto100kb = True):
    btr = h264btr * ratio / 1000
    return btr if not roundto100kb else math.ceil(btr / 100) * 100

def rundir(root):
    for (p, dirs, files) in os.walk(root):
        print("enter %s" % p)
        #print(p, dirs, files)
        files.sort()
        for f in files:
            fn = os.path.join(p, f)
            parsefile(fn)
        print("leave %s" % p)

def writesh():
    with open("chn.sh", "wb") as fp:
        fp.write(b"#!/bin/sh\n\n")
        for cmd in CMDS:
            fp.write(cmd.encode('utf8'))
            fp.write(b'\n')
    pass

if __name__=='__main__':
    if len(sys.argv) < 2:
        print('Usage: %s [path]' % sys.argv[0])
        sys.exit(-1)
    path = os.path.realpath(sys.argv[1])
    rundir(path)
    #print(CMDS)
    writesh()
    pass
