#!/usr/bin/env python3
# vim: set fileencoding: UTF-8 -*-

import argparse
from genericpath import isfile
import logging
import os
import os.path
import re

logging.basicConfig(level=logging.DEBUG)
NUMBER_PATTERN = re.compile('^(\\d{6}(-|_)\d+)')
LETTER_PATTERN = re.compile('^(\w{2,5}-\d+)')

def buildargparser():
    parser = argparse.ArgumentParser(description='apply directory name to files in it')
    parser.add_argument('-p', '--path', default=['./'], help = 'path to look into', nargs="*")
    return parser

def calcIdentity(input):
    basename = os.path.basename(input)
    m = NUMBER_PATTERN.search(basename)
    if m != None:
        return m.group(0)
    m = LETTER_PATTERN.search(basename)
    if m != None:
        return m.group(0)
    return None

def findVideoItem(path):
    subs = []
    found = []
    for p in os.listdir(path):
        if p[0] == '.':
            continue
        subpath = os.path.join(os.path.realpath(path), p)
        logging.debug("dealing %s", subpath)
        if not os.path.isfile(subpath):
            subs.append(subpath)
            logging.debug("%s not file", subpath)
            continue
        else:
            id = calcIdentity(subpath)
            if id != None:
                found.append((id, subpath))
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
            logging.info('search in %s', currentpath)
            ret = findVideoItem(currentpath)
            for (id, vfile) in ret[0]:
                if id not in map:
                    map[id] = []
                map[id].append(vfile)
            for subp in ret[1]:
                stack.append(subp)
            
    for k in map.keys():
        logging.info("%s", k)
