#!/usr/bin/env python3
# vim: set fileencoding: UTF-8 -*-

import argparse
from genericpath import isfile
import logging
import os
import os.path
import re

logging.basicConfig(level=logging.INFO)
PATTERNS = (
    ('TH_PATTERN', re.compile('^(th\d+(-|_)\d+(-|_)\d+)', re.I)),
    ('NUMBER_PATTERN', re.compile('^(\d{6}(-|_)\d+)', re.I)),
    ('LETTER_PATTERN', re.compile('^(\w{2,5}-\d+)', re. I)),
    ('N_PATTERN', re.compile('^((n|k)\d+)', re.I))
)

def buildargparser():
    parser = argparse.ArgumentParser(description='apply directory name to files in it')
    parser.add_argument('-p', '--path', default=['./'], help = 'path to look into', nargs="*")
    return parser

def calcIdentity(input):
    basename = os.path.basename(input)
    for (name, pattern) in PATTERNS:
        m = pattern.search(basename)
        if m != None:
            return m.group(0).lower()
    return None

def findVideoItem(path):
    subs = []
    found = []
    for p in os.listdir(path):
        if p[0] == '.':
            continue
        subpath = os.path.join(os.path.realpath(path), p)
        logging.debug("dealing %s", subpath)
        id = calcIdentity(subpath)
        if id != None:
            found.append((id, subpath))
            continue
        if not os.path.isfile(subpath):
            subs.append(subpath)
            logging.debug("%s s directory", subpath)
    return (found, subs)

if __name__=='__main__':
    parser = buildargparser()
    arg=parser.parse_args()
    logging.info(arg)
    map = {}
    for p in arg.path:
        fullpath = os.path.realpath(p)
        stack = [fullpath]
        while len(stack) > 0:
            currentpath = stack.pop()
            logging.debug('search in %s', currentpath)
            ret = findVideoItem(currentpath)
            for (id, vfile) in ret[0]:
                if id not in map:
                    map[id] = []
                map[id].append(vfile)
            for subp in ret[1]:
                stack.append(subp)
    duplicated = {k: v for (k, v) in map.items() if len(v)>1 }            
    for k in duplicated:
        logging.info("%s is duplicated", k)
        for i in duplicated[k]:
            logging.warning(i)
