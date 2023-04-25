#!/usr/bin/env python3
# vim: set fileencoding: UTF-8 -*-

import argparse
import os
import re
import shutil

def buildargparser():
    parser = argparse.ArgumentParser(description='apply directory name to files in it')
    parser.add_argument('-X', '--execute', default=False, help = 'Do the actual renaming execution, or only print out actions to be.', action = 'store_true')
    parser.add_argument('-p', '--path', default='./', help = 'path to look into')
    parser.add_argument('-x', '--exclude', default=[], help = 'exclude files with specified extensions', nargs='*')
    parser.add_argument('-n', '--segnum', default=1, help='the number of dot separated part(s) in old name that will be replaced(except the ext). 1 by default, negative number means starting counting from end.', type=int)
    return parser

def newfilename(oldname, replace, segnum):
    parts = oldname.split('.')
    if segnum == 0:
        return '%s.%s' % (replace, oldname)
    elif segnum > 0:
        ext = parts[1] if len(parts) > 1 else ''
        baseparts = parts[:-1] if len(parts) > 1 else parts
        if len(baseparts) <= segnum:
            nf = replace
        else:
            nf = ".".join([replace] + baseparts[segnum:-1])
        return nf if ext == '' else '%s.%s' % (nf, ext)
    else:
        reserve = parts[segnum:] if abs(segnum) <= len(parts) else parts
        #print(reserve)
        return ".".join([replace] + reserve)

if __name__=='__main__':
    parser = buildargparser()
    arg=parser.parse_args()
    print(arg)
    rootpath = os.path.realpath(arg.path)
    for (pathname, dirs, files) in os.walk(rootpath):
        if pathname == rootpath:
            continue
        if os.path.realpath(os.path.join(pathname, os.path.pardir)) != rootpath:
            continue
        print('process %s' % pathname)
        replace = os.path.basename(pathname)
        newfiles = []
        for f in files:
            if any([re.match(x, f) != None for x in arg.exclude]):
                print('skip %s' % f)
                continue
            nrf = newfilename(f, replace, arg.segnum)
            nf = os.path.join(pathname, nrf)
            nameconflict = nf in newfiles
            if nameconflict:
                print('error: file name to be renamed conflicted "%s/%s" <-> "%s/%s", will skip' % (pathname, f, pathname, nf))
            else:
                newfiles.append(nf)
            of = os.path.join(pathname, f)
            if not arg.execute:
                print('mv "%s" "%s"' % (of, nf))
            else:
                if not nameconflict:
                    shutil.move(of, nf)

