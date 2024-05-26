#!/usr/bin/env python3
# vim: set fileencoding: UTF-8 -*-

'''
This script is to create a batch of ffmpeg commands those will convert all video files from specified
directory to an mp4 with video encoded in H.265, with bitrate set as 2 / 3 of the original for H.264,
and 50% for the other video codecs.
'''

import argparse
import logging
import math
import os
import os.path
import re

from pyffprobe import probe, codec

VIDEO_FILE_TYPES = ['.mkv', '.mp4', 'avi', '.rmvb']

class command:
    def __init__(self, comment, cmd):
        self.comment = comment
        self.cmd = cmd

class pathrunner():
    def __init__(self, arg) -> None:
        self.cmds = []
        self.defaultratio = arg.default_bitrate_ratio
        self.brdict ={'h264': arg.h264_bitrate_ratio}
        self.root = os.path.realpath(arg.directory)
        self.h264subregexes = [re.compile(re.escape(s), re.I) for s in ["h264", "x264", "avc"]]
        self.skiplist = [] if arg.skip==None else [os.path.realpath(x) for x in arg.skip]
        self.bash = not arg.win
        self.enc = arg.encoding
        if not os.path.exists(self.root):
            raise FileExistsError('%s not existed or not accessible' % self.root)

    def parsefile(self, f: str):
        if f.endswith('.hevc.mp4'):
            return
        ext = os.path.splitext(f)[1].lower()
        if ext not in VIDEO_FILE_TYPES:
            logging.warning("skip file %s", f)
            return
        logging.info("run %s", f)
        info = probe(f)
        for st in info.streams:
            if not st.isvideo() and not st.isaudio():
                logging.warning("skip codec %s", st.codec.name)
                continue
            if st.isaudio():
                if st.codec.name not in ('mp3', 'aac'):
                    logging.warning('warn: audio codec %s', st.codec.name)
                continue
            if st.codec.name == 'hevc':
                logging.info('%s is encoded using hevc', f)
                return
            (fn0, ext) = os.path.splitext(f)
            fn = fn0.replace('"', '\\"')
            if st.codec.bitrate == None:
                logging.error("unknown bit rate: %s for a video stream, skip", st.codec.bitrate)
                continue
            br265 = self.__calch265btr(st.codec, int(st.codec.bitrate))
            cmd = '''ffmpeg -i "%s%s" -map 0 -c:v hevc -b:v %dk -metadata:s:v:0 BPS="%dk" -c:a copy -c:s copy "%s.hevc%s"''' % (fn, ext, br265, br265, self.__targetname(fn), ext)
            comment = "File is encoded by %s with %f" % (st.codec.name, st.codec.bitrate)
            logging.debug("ffmpeg cli: %s", cmd)
            self.cmds.append(command(comment, cmd))
            break

    def __targetname(self, filename: str):
        (path, basename) = os.path.split(filename)
        for reg in self.h264subregexes:
            if reg.search(basename) != None:
                newbasename = reg.sub("x265", basename)
                return os.path.join(path, newbasename)
        return filename

    def __calch265btr(self, codec: codec, originalbtr: int, roundto100kb = True):
        ratio = self.brdict[codec.name] if codec.name in self.brdict else self.defaultratio
        btr = originalbtr * ratio / 1000
        logging.info('ratio %s used, target br set as %f' % (ratio, btr))
        return btr if not roundto100kb else math.ceil(btr / 100) * 100

    def run(self):
        for (p, dirs, files) in os.walk(self.root):
            logging.debug("enter %s" % p)
            #print(p, dirs, files)
            files.sort()
            for f in files:
                fullfn = os.path.join(p, f)
                if fullfn in self.skiplist:
                    continue
                fn = os.path.join(p, f)
                self.parsefile(fn)
            logging.debug("leave %s" % p)
        self.__writesh()

    def __writesh(self):
        if self.bash:
            self.__writebash()
        else:
            self.__writecmd()

    def __writebash(self):
        sep = '\n'.encode(self.enc)
        with open("h265.sh", "wb") as fp:
            fp.write(b"#!/bin/sh\n\n")
            for cmd in self.cmds:
                fp.write(('#%s' % cmd.comment).encode(self.enc))
                fp.write(sep)
                fp.write(cmd.cmd.encode(self.enc))
                fp.write(sep)
                fp.write('sleep 10'.encode(self.enc))
                fp.write(sep)
        pass

    def __writecmd(self):
        sep = '\r\n'.encode(self.enc)
        with open("h265.cmd", "wb") as fp:
            for cmd in self.cmds:
                fp.write(('REM %s' % cmd.comment).encode(self.enc))
                fp.write(sep)
                fp.write(cmd.cmd.encode(self.enc))
                fp.write(sep)
        pass

def buildargparser():
    parser = argparse.ArgumentParser(description='Generate a script which run ffmpeg to encode video files in a directory with hevc.')
    parser.add_argument('directory', help = 'the directory to search in')
    parser.add_argument('-h264br', '--h264-bitrate-ratio', help = 'target bit rate ratio for original H.264 video', default=2/3, type=float)
    parser.add_argument('-br', '--default-bitrate-ratio', help = 'target bit rate ratio for any other original video codecs', default=0.5, type=float)
    parser.add_argument('-s', '--skip', help = 'skip files', nargs='*')
    parser.add_argument('-w', '--win', help = 'output script in windows bacth', action='store_true', default=False)
    parser.add_argument('-enc', '--encoding', help = 'encoding of the output file', default='utf-8')
    parser.add_argument('-l', '--log-level', default = logging.INFO, help = '''setting log level: CRITICAL, FATAL, ERROR, WARNING, WARN = WARNING, INFO, DEBUG, NOTSET''')
    return parser

if __name__=='__main__':
    parser = buildargparser()
    arg = parser.parse_args()
    logging.basicConfig(level=arg.log_level)
    pathrunner(arg).run()
