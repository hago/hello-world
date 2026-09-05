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
import multiprocessing
import os
import os.path
import re
import sys

from pyffprobe import probe, codec, videoinfo, audiostreaminfo, videostreaminfo

VIDEO_FILE_TYPES = ['.mkv', '.mp4', '.avi', '.rmvb', '.mov', '.mpg', '.ts', '.wmv']
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
        self.outfilename = arg.output
        self.cpus = arg.cpus
        self.encoder = arg.encoder
        if not os.path.exists(self.root):
            raise FileExistsError('source path %s not existed or not accessible' % self.root)
        if not os.path.exists(self.target):
            raise FileExistsError('target path %s not existed or not accessible' % self.target)

    def parsefile(self, f: str):
        if f.endswith('.hevc.mp4') or f.endswith('.hevc.mkv'):
            return
        ext = os.path.splitext(f)[1].lower()
        if ext not in VIDEO_FILE_TYPES:
            logging.warning("skip file %s", f)
            return
        logging.info("run %s", f)
        info = probe(f)
        if self.encoder == 'HandBrakeCLI':
            (codecstr, comments) = self.__createHBcodecoptions(info)
            dest = self.__targetname(f)
            cmd = 'HandBrakeCLI -i "%s" %s -o "%s"' % (self.__escapefn(f), codecstr, self.__escapefn(dest))
            logging.debug("HandBrakeCLI cli: %s", cmd)
        elif self.encoder == 'ffmpeg':
            (codecstr, comments) = self.__createffmpegcodecoptions(info)
            if not self.podman:
                dest = self.__targetname(f)
                cmd = 'ffmpeg -i "%s" %s "%s"' % (self.__escapefn(f), codecstr, self.__escapefn(dest))
            else:
                (fpath, f0) = os.path.split(f)
                dest = self.__targetrawname(f0)
                cmd = 'podman run %s --rm -v "%s":/config linuxserver/ffmpeg -i "/config/%s" %s "/config/%s"' % \
                    (self.__gencpuparams(), self.__escapefn(fpath), self.__escapefn(f0), codecstr, self.__escapefn(dest))
            logging.debug("ffmpeg cli: %s", cmd)
        else:
            logging.error('unknown encoder: %s' % self.encoder)
            sys.exit(-1)
        self.cmds.append(command(comments, cmd))

    def __gencpuparams(self)->str:
        if self.cpus == None:
            return ""
        else:
            maxcount = multiprocessing.cpu_count() - 1
            return "--cpus %d" % (self.cpus if self.cpus < maxcount else maxcount)

    def __escapefn(self, f:str)->str:
        return f.replace('"', '\\"')

    '''
    When HandBrake is applied, Assumption: only one video stream and only one audio stream in file. 
    '''
    def __createHBcodecoptions(self, info: videoinfo) -> tuple[str, list]:
        (videos, audios, comments) = self.__parsestreams(info)
        if len(videos) > 1 or len(audios) > 1:
            logging.warning("multiple video or audio streams in this file")
        codecoptstr = ""
        br265 = 0
        for vindex in range(len(videos)):
            st = videos[vindex]
            if st.codec.name in IMAGE_CODECS_IN_VIDEO_STREAM:
                logging.warning("video stream %d is image, skip" % vindex)
                continue
            if st.codec.name == 'hevc':
                if self.x265br == None:
                    logging.error('video stream %d is already encoded using hevc, re-encode in 90%% of original bitrate is assumpted', vindex)
                    x265br = int(st.codec.bitrate * 0.9)
                else:
                    logging.debug('video stream %d is to re-encode in hevc', vindex)
                    x265br = int(st.codec.bitrate * self.x265br)
                codecoptstr += ' -e x265 -b %s ' % (math.ceil(x265br / 1024))
            else:
                br265 = self.__calch265btr(st.codec, int(st.codec.bitrate))
                codecoptstr = " -e x265 -b %d " % (math.ceil(br265 / 1024))
            break
        codecoptstr += " -E copy:aac "
        return (codecoptstr, comments)

    def __createffmpegcodecoptions(self, info: videoinfo) -> tuple[str, list]:
        codecoptstr = "-map 0 -c:s copy"
        (videos, audios, comments) = self.__parsestreams(info)
        codecoptstr += " -c:a copy"
        for vindex in list(range(len(videos))):
            st = videos[vindex]
            if st.codec.name == 'hevc':
                if self.x265br == None:
                    logging.debug('video stream %d is already encoded using hevc, copy used', vindex)
                    codecoptstr += ' -c:v:%d copy ' % vindex
                else:
                    logging.debug('video stream %d is to re-encode in hevc', vindex)
                    x265br = int(st.codec.bitrate * self.x265br)
                    codecoptstr += ' -c:v:%d hevc -b:v:%d %s -metadata:s:v:%d BPS="%s" ' % (vindex, vindex, x265br, vindex, x265br)
                continue
            if st.codec.name in IMAGE_CODECS_IN_VIDEO_STREAM:
                logging.debug('video stream %s is image, copy used', vindex)
                codecoptstr += ' -c:v:%d copy ' % vindex
                continue
            if st.codec.bitrate == None:
                logging.error("unknown bit rate: %s for a video stream, skip", st.codec.bitrate)
                continue
            else:
                br265 = self.__calch265btr(st.codec, int(st.codec.bitrate))
                codecoptstr += ' -c:v:%d hevc -b:v:%d %s -metadata:s:v:%d BPS="%s" ' % (vindex, vindex, br265, vindex, br265)
        return (codecoptstr, comments)

    '''
    return a tuple of (video streams, audio streams, comments on encoding info)
    '''
    def __parsestreams(self, info: videoinfo) -> tuple[list, list, list]:
        comments = []
        videostreams = []
        audiostreams = []
        for i in range(len(info.streams)):
            st = info.streams[i]
            if st.isaudio():
                comments.append(self.__genaudioinfocomment(st, i))
                audiostreams.append(st)
                continue
            if not st.isvideo():
                logging.debug("not video stream, skip stream %d", i)
                continue
            videostreams.append(st)
            comments += self.__genvideoinfocomment(st, i)
        return (videostreams, audiostreams, comments)

    def __genaudioinfocomment(self, stream: audiostreaminfo, idx: int)->str:
        return "audio stream %d is encoded with %s at bit rate %d" % (idx, stream.codec.name, stream.codec.bitrate)

    def __genvideoinfocomment(self, stream: videostreaminfo, vindex: int)->list[str]:
        comments = []
        comments.append("Stream %d is encoded by %s with %f" % (vindex, stream.codec.name, stream.codec.bitrate))
        comments.append("resolution: %d %d SAR: %s DAR: %s FPS: %d" % (stream.width, stream.height, stream.sar, stream.dar, stream.fps))
        return comments

    def __targetname(self, filename: str)->str:
        (srcpath, basename) = os.path.split(filename)
        relpath = os.path.relpath(srcpath, self.root)
        targetpath = os.path.realpath(os.path.join(self.target, relpath))
        if not os.path.exists(targetpath):
            os.makedirs(targetpath)
        return os.path.join(targetpath, self.__targetrawname(basename))
    
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
        #for (p, dirs, files) in os.walk(self.root):
        for (p, dirs, files) in self.__walk(self.root):
            #files.sort()
            for f in files:
                if not self.filterfunc(f):
                    logging.debug("skip %s" % f)
                    continue
                fullfn = os.path.join(p, f)
                if fullfn in self.skiplist:
                    continue
                fn = os.path.join(p, f)
                self.parsefile(fn)
        self.__writesh()

    def __walk(self, path: str) -> list[tuple[str, list[str], list[str]]]:
        stack = [path]
        ret = []
        while len(stack) > 0:
            p = stack.pop()
            logging.debug("enter %s" % p)
            dirs = []
            files = []
            for i in os.scandir(p):
                #print(i)
                if i.is_dir():
                    dirs.append(i.name)
                elif i.is_file():
                    files.append(i.name)
                else:
                    logging.warning('unknown stat %s of %s' % (i.stat(), i.path))
            dirs.sort()
            files.sort()
            ret.append((p, dirs, files))
            dirs.reverse()
            stack.extend([os.path.join(p, d) for d in dirs])
            logging.debug("leave %s" % p)
        return ret

    def __writesh(self):
        if self.bash:
            self.__writebash()
        else:
            self.__writecmd()

    def __writebash(self):
        sep = '\n'.encode(self.enc)
        fn = os.path.join(self.target, "%s.sh" % self.outfilename)
        ffmpegcmds = []
        for cmd in self.cmds:
            s = sep.join([('#%s' % comment).encode(self.enc) for comment in cmd.comments])
            s += sep
            s += cmd.cmd.encode(self.enc)
            ffmpegcmds.append(s)
        ss = (b" && \\%s" % sep).join(ffmpegcmds)
        with open(fn, "wb") as fp:
            fp.write(b"#!/bin/sh\n\n")
            fp.write(ss)
            '''
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
            '''
        os.chmod(fn, 0o755)
        pass

    def __writecmd(self):
        sep = '\r\n'.encode(self.enc)
        with open(os.path.join(self.target, "%s.cmd" % self.outfilename), "wb") as fp:
            for cmd in self.cmds:
                for comment in cmd.comments:
                    fp.write(('REM %s' % comment).encode(self.enc))
                    fp.write(sep)
                fp.write(cmd.cmd.encode(self.enc))
                fp.write(sep)
                #fp.write("@IF ERRORLEVEL 1 (".encode(self.enc))
                #fp.write(sep)
                #fp.write("@ECHO 'Error occurs!, EXIT'".encode(self.enc))
                #fp.write(sep)
                #fp.write("@EXIT /B 42".encode(self.enc))
                #fp.write(sep)
                #fp.write(")".encode(self.enc))
                #fp.write(sep)
                #fp.write(sep)
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
    parser.add_argument("-o", "--output", required=False, help='the name for the generated file', default="h265")
    parser.add_argument("-c", "--cpus", required=False, help='maximum amount of the cpu cores(hyper thread counts) to be used, only works with -p', type=int)
    parser.add_argument("-e", "--encoder", required=False, help='the encode tool to use: ffmpeg or HandBrakeCLI', choices=['ffmpeg', 'HandBrakeCLI'], default='ffmpeg')
    return parser

if __name__=='__main__':
    parser = buildargparser()
    arg = parser.parse_args()
    logging.basicConfig(level=arg.log_level)
    logging.debug("arg %s", arg)
    pathrunner(arg).run()
