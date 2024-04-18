#!/usr/bin/env python3
# vim: set fileencoding: UTF-8 -*-

'''
This script is to create a batch of ffmpeg commands those will convert all video files from specified
directory to an mp4 with video encoded in H.265, with bitrate set as 2 / 3 of the original for H.264,
and 50% for the other video codecs.
'''

import argparse
import math
import os
import os.path
import re

from pyffprobe import probe, codec

VIDEO_FILE_TYPES = ['.mkv', '.mp4', 'avi', '.rmvb']

class pathrunner():
    def __init__(self, arg) -> None:
        self.cmds = []
        self.defaultratio = arg.default_bitrate_ratio
        self.brdict ={'h264': arg.h264_bitrate_ratio}
        self.root = os.path.realpath(arg.directory)
        self.h264subregexes = [re.compile(re.escape(s), re.I) for s in ["h264", "x264", "avc"]]
        if not os.path.exists(self.root):
            raise FileExistsError('%s not existed or not accessible' % self.root)

    def parsefile(self, f: str):
        if f.endswith('.hevc.mp4'):
            return
        ext = os.path.splitext(f)[1].lower()
        if ext not in VIDEO_FILE_TYPES:
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
            if st.codec.name == 'hevc':
                print('%s is encoded using hevc' % f)
                return
            (fn0, ext) = os.path.splitext(f)
            fn = fn0.replace('"', '\\"')
            if st.codec.bitrate == None:
                print("unknown bit rate: %s for a video stream, skip\r\n" % st.codec.bitrate)
                continue
            br265 = self.__calch265btr(st.codec, int(st.codec.bitrate))
            cmd = '''ffmpeg -i "%s%s" -c:v hevc -b:v %dk -c:a copy "%s.hevc.mp4"''' % (fn, ext, br265, self.__targetname(fn))
            print(cmd)
            self.cmds.append("#File is encoded by %s with %f" % (st.codec.name, st.codec.bitrate))
            self.cmds.append(cmd)
            self.cmds.append("sleep 10")
            break

    def __targetname(self, basename: str):
        for reg in self.h264subregexes:
            if reg.search(basename) != None:
                return reg.sub("x265", basename)
        return basename

    def __calch265btr(self, codec: codec, originalbtr: int, roundto100kb = True):
        ratio = self.brdict[codec.name] if codec.name in self.brdict else self.defaultratio
        btr = originalbtr * ratio / 1000
        print('ratio %s used, target br set as %f' % (ratio, btr))
        return btr if not roundto100kb else math.ceil(btr / 100) * 100

    def run(self):
        for (p, dirs, files) in os.walk(self.root):
            print("enter %s" % p)
            #print(p, dirs, files)
            files.sort()
            for f in files:
                fn = os.path.join(p, f)
                self.parsefile(fn)
            print("leave %s" % p)
        self.__writesh()

    def __writesh(self):
        with open("h265.sh", "wb") as fp:
            fp.write(b"#!/bin/sh\n\n")
            for cmd in self.cmds:
                fp.write(cmd.encode('utf8'))
                fp.write(b'\n')
        pass

def buildargparser():
    parser = argparse.ArgumentParser(description='Generate ffmpeg commands')
    parser.add_argument('directory', help = 'the directory to search in')
    parser.add_argument('-h264br', '--h264-bitrate-ratio', help = 'target bit rate ratio for original H.264 video', default=2/3, type=float)
    parser.add_argument('-br', '--default-bitrate-ratio', help = 'target bit rate ratio for any other original video codecs', default=0.5, type=float)
    return parser

if __name__=='__main__':
    parser = buildargparser()
    arg = parser.parse_args()
    #print(arg)
    pathrunner(arg).run()
