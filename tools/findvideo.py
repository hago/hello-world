#!/usr/bin/env python3
# vim: set fileencoding: UTF-8 -*-

import argparse
import logging
import os
import os.path
import sys

from pyffprobe import probe, streaminfo

def buildargparser():
    parser = argparse.ArgumentParser(description='find video files by meta info')
    parser.add_argument('-p', '--path', default=['./'], help = 'path to look into', nargs="*")
    parser.add_argument('-c', '--codec', help = 'find files by codecs, use - prefix to exclude', nargs="*")
    parser.add_argument('-ce', '--codec-exclude', help = 'find files by codecs, use - prefix to exclude', nargs="*")
    parser.add_argument('-b', '--bit-rate', help = 'find files by bitrate, use + or - to indicate bit rate range', nargs="*")
    parser.add_argument('-l', '--log-level', default = logging.INFO, help = '''setting log level: CRITICAL, FATAL, ERROR, WARNING, WARN = WARNING, INFO, DEBUG, NOTSET''')
    return parser

class argfilter:
    def __init__(self, arg) -> None:
        self.includecodes = {}
        if arg.codec != None:
            for c in arg.codec:
                self.includecodes[c] = 1
        self.excludecodecs = {}
        if arg.codec_exclude != None:
            for c in arg.codec_exclude:
                self.excludecodecs[c] = 1
        if len(self.includecodes) > 0 and len(self.excludecodecs) > 0:
            raise Exception("inclusive and exclusive restrictions can't be used at same time")
        if len(self.includecodes or self.excludecodecs) != len(self.includecodes) + len(self.excludecodecs):
            raise Exception("conflict for included and excluded codecs: %s %s" % (self.includecodes.keys(), self.excludecodecs.keys()))
        self.brmax = 0
        self.brmin = 0
        if arg.bit_rate != None:
            for r in arg.bit_rate:
                x = self.__calcbr(r)
                if x == None:
                    continue
                if x > 0 and x > self.brmax:
                    self.brmax = x
                elif x < 0:
                    x = abs(x)
                    if self.brmin == 0 or self.brmin > x:
                        self.brmin = x

    def __calcbr(self, strbr: str) -> int:
        s = strbr.lower().strip()
        units = 1
        if s.endswith("k"):
            units = 1024
            s = s[:-1]
        elif s.endswith('m'):
            units = 1024 * 1024
            s = s[:-1]
        elif s.endswith('g'):
            units = 1024 * 1024 * 1024
            s = s[:-1]
        try:
            x = int(s)
            return x * units
        except ValueError:
            logging.warning("invalid bitrate %s, ignored", strbr)
            return None

    def test(self, sinfo: streaminfo):
        return self.__codectest(sinfo) and self.__brtest(sinfo)
    
    def __codectest(self, sinfo: streaminfo):
        codechit = False
        logging.debug(sinfo.codec.name)
        logging.debug("%s %s", self.includecodes, self.excludecodecs)
        if len(self.includecodes) == 0 and len(self.excludecodecs) == 0:
            codechit = True
        elif len(self.includecodes) > 0 and sinfo.codec.name in self.includecodes:
            codechit = True
        elif len(self.excludecodecs) > 0 and sinfo.codec.name not in self.excludecodecs:
            codechit = True
        logging.debug(codechit)
        return codechit
    
    def __brtest(self, sinfo: streaminfo):
        brhit = False
        if self.brmax == 0 and self.brmin == 0:
            brhit = True
        elif self.brmax !=0 and self.brmin != 0:
            brhit = sinfo.codec.bitrate >= self.brmin and sinfo.codec.bitrate <= self.brmax
        elif self.brmax != 0:
            brhit = sinfo.codec.bitrate <= self.brmax
        else:
            brhit = sinfo.codec.bitrate >= self.brmin
        return brhit

if __name__=='__main__':
    parser = buildargparser()
    arg=parser.parse_args()
    logging.basicConfig(level=arg.log_level)
    logging.debug("arg: %s", arg)
    if arg.codec == None and arg.bit_rate == None and arg.codec_exclude == None:
        logging.warning("no filter specified")
        sys.exit()
    filter = argfilter(arg)
    for p in arg.path:
        fullpath = os.path.realpath(p)
        for (root, dirs, files) in os.walk(fullpath):
            for f in files:
                fn = os.path.join(root, f)
                logging.debug("probe: %s", fn)
                vinfo = probe(fn)
                matched = False
                for sinfo in vinfo.streams:
                    if not sinfo.isvideo():
                        continue
                    if filter.test(sinfo):
                        matched = True
                        logging.info("Found: %s", fn)
                        break
                if not matched:
                    logging.debug("Not macth: %s", fn)
