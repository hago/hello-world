#!/usr/bin/env python3
# vim: set fileencoding: UTF-8 -*-

'''
This script is to create a batch of ffmpeg commands those will convert all video files from specified
directory to an mp4 with video encoded in H.265, with bitrate set as 2 / 3 of the original for H.264,
and 50% for the other video codecs.
'''

import argparse
import logging
import os
import os.path
import re

from pyffprobe import probe, codec, videoinfo

VIDEO_FILE_TYPES = ['.mkv', '.mp4', 'avi', '.rmvb']
IMAGE_CODECS_IN_VIDEO_STREAM = ['jpeg2000', 'jpegls', 'mjpeg', 'png', 'sgi', 'tiff', 'webp', 'ppm']

class command:
    def __init__(self, comments, cmd):
        self.comments = comments
        self.cmd = cmd

class pathrunner():
    def __init__(self, arg) -> None:
        self.cmds = []
        self.defaultratio = arg.default_bitrate_ratio
        self.brdict = {'h264': arg.h264_bitrate_ratio}
        self.x265br = arg.x265_bitrate_ratio
        self.root = os.path.realpath(arg.directory)
        self.h264subregexes = [re.compile(re.escape(s), re.I) for s in ["h264", "x264", "avc", "h.264"]]
        self.skiplist = [] if arg.skip==None else [os.path.realpath(x) for x in arg.skip]
        self.bash = not arg.win
        self.enc = arg.encoding
        self.target = os.path.realpath(arg.target)
        self.podman = arg.podman
        self.filterfunc = lambda fn: True if len(arg.filter)==0 else any([re.search(p, fn, re.I) != None for p in arg.filter])
        if not os.path.exists(self.root):
            raise FileExistsError('source path %s not existed or not accessible' % self.root)
        if not os.path.exists(self.target):
            raise FileExistsError('target path %s not existed or not accessible' % self.target)

    def parsefile(self, f: str):
        if f.endswith('.hevc.mp4'):
            return
        ext = os.path.splitext(f)[1].lower()
        if ext not in VIDEO_FILE_TYPES:
            logging.warning("skip file %s", f)
            return
        logging.info("run %s", f)
        info = probe(f)
        (codecstr, comments) = self.__createcodecoptions(info)
        if not self.podman:
            cmd = 'ffmpeg -i "%s" %s "%s"' % (self.__escapefn(f), codecstr, self.__targetname(f))
        else:
            (fpath, f0) = os.path.split(f)
            dest = self.__targetrawname(f0)
            cmd = 'podman run --rm -v "%s":/config linuxserver/ffmpeg -i "/config/%s" %s "/config/%s"' % \
                (self.__escapefn(fpath), self.__escapefn(f0), codecstr, self.__escapefn(dest))
        logging.debug("ffmpeg cli: %s", cmd)
        self.cmds.append(command(comments, cmd))

    def __escapefn(self, f:str)->str:
        return f.replace('"', '\\"')

    def __createcodecoptions(self, info: videoinfo) -> tuple[str, list]:
        comments = []
        vindex = -1
        codecoptstr = "-map 0 -c:a copy -c:s copy"
        for i in range(len(info.streams)):
            st = info.streams[i]
            if not st.isvideo():
                logging.debug("not video stream, skip stream %d", i)
                continue
            vindex += 1
            if st.codec.name == 'hevc':
                if self.x265br == None:
                    logging.debug('video stream %d is already encoded using hevc, copy used', i)
                    codecoptstr += ' -c:v:%d copy ' % vindex
                else:
                    logging.debug('video stream %d is to re-encode in hevc', i)
                    x265br = int(st.codec.bitrate * self.x265br)
                    comments.append("Stream %d is encoded by hevc with %f" % (vindex, st.codec.bitrate))
                    codecoptstr += ' -c:v:%d hevc -b:v:%d %s -metadata:s:v:%d BPS="%s" ' % (vindex, vindex, x265br, vindex, x265br)
                continue
            if st.codec.name in IMAGE_CODECS_IN_VIDEO_STREAM:
                logging.debug('video stream %s is image, copy used', i)
                codecoptstr += ' -c:v:%d copy ' % vindex
                continue
            if st.codec.bitrate == None:
                logging.error("unknown bit rate: %s for a video stream, skip", st.codec.bitrate)
                continue
            else:
                br265 = self.__calch265btr(st.codec, int(st.codec.bitrate))
                comments.append("Stream %d is encoded by %s with %f" % (vindex, st.codec.name, st.codec.bitrate))
                codecoptstr += ' -c:v:%d hevc -b:v:%d %s -metadata:s:v:%d BPS="%s" ' % (vindex, vindex, br265, vindex, br265)
        return (codecoptstr, comments)

    def __targetname(self, filename: str)->str:
        (srcpath, basename) = os.path.split(filename)
        return os.path.join(self.target, self.__targetrawname(basename))
    
    def __targetrawname(self, rawname: str)->str:
        for reg in self.h264subregexes:
            if reg.search(rawname) != None:
                newname = reg.sub("x265", rawname)
                return self.__addx265inname(newname)
        return self.__addx265inname(rawname)
    
    def __addx265inname(self, name:str) -> str:
        (fn, ext) = os.path.splitext(name)
        return "%s.hevc%s" % (fn, ext)

    def __calch265btr(self, codec: codec, originalbtr: int):
        ratio = self.brdict[codec.name] if codec.name in self.brdict else self.defaultratio
        btr = int(originalbtr * ratio)
        logging.info('ratio %s used, target br set as %f' % (ratio, btr))
        return btr

    def run(self):
        for (p, dirs, files) in os.walk(self.root):
            logging.debug("enter %s" % p)
            #print(p, dirs, files)
            files.sort()
            for f in files:
                if not self.filterfunc(f):
                    logging.debug("skip %s" % f)
                    continue
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
        with open(os.path.join(self.target, "h265.sh"), "wb") as fp:
            fp.write(b"#!/bin/sh\n\n")
            for cmd in self.cmds:
                for comment in cmd.comments:
                    fp.write(('#%s' % comment).encode(self.enc))
                    fp.write(sep)
                fp.write(cmd.cmd.encode(self.enc))
                fp.write(sep)
                fp.write(sep)
                fp.write('sleep 10'.encode(self.enc))
                fp.write(sep)
                fp.write(sep)
        pass

    def __writecmd(self):
        sep = '\r\n'.encode(self.enc)
        with open(os.path.join(self.target, "h265.cmd"), "wb") as fp:
            for cmd in self.cmds:
                for comment in cmd.comments:
                    fp.write(('REM %s' % comment).encode(self.enc))
                    fp.write(sep)
                fp.write(cmd.cmd.encode(self.enc))
                fp.write(sep)
                fp.write(sep)
        pass

def buildargparser():
    parser = argparse.ArgumentParser(description='Generate a script which run ffmpeg to encode video files in a directory with hevc.')
    parser.add_argument('-d', '--directory', help = 'the directory to search in', required=True)
    parser.add_argument('-h264br', '--h264-bitrate-ratio', help = 'target bit rate ratio for original H.264 video', default=2/3, type=float)
    parser.add_argument('-x265br', '--x265-bitrate-ratio', help = 'target bit rate ratio for original X.265 video', default=None, type=float)
    parser.add_argument('-br', '--default-bitrate-ratio', help = 'target bit rate ratio for any other original video codecs', default=0.5, type=float)
    parser.add_argument('-s', '--skip', help = 'skip files', nargs='*')
    parser.add_argument('-w', '--win', help = 'output script in windows bacth', action='store_true', default=False)
    parser.add_argument('-enc', '--encoding', help = 'encoding of the output file', default='utf-8')
    parser.add_argument('-l', '--log-level', default = logging.INFO, help = '''setting log level: CRITICAL, FATAL, ERROR, WARNING, WARN = WARNING, INFO, DEBUG, NOTSET''')
    parser.add_argument("-t", "--target", default = './',  help='The target path where to create script file and to store target x265 files by the script')
    parser.add_argument("-p", "--podman", required=False, action='store_true',  help='generate commands using containers, podman or docker')
    parser.add_argument("-ft", "--filter", required=False, nargs='*', help='patterns to filter file names', default=[])
    return parser

if __name__=='__main__':
    parser = buildargparser()
    arg = parser.parse_args()
    logging.basicConfig(level=arg.log_level)
    logging.debug("arg %s", arg)
    pathrunner(arg).run()
