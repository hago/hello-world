#!/usr/bin/env python3
# vim: set fileencoding: UTF-8 -*-

import argparse
import os
import re
import shutil

def buildargparser():
    parser = argparse.ArgumentParser(description='apply directory name to files in it')
    parser.add_argument('-n', '--dry-run', default=False, help = 'print operations to be perform, yet not execute them', action = 'store_true')
    parser.add_argument('-p', '--path', default='./', help = 'path to look into')
    parser.add_argument('-x', '--exclude', default=[], help = 'exclude files with specified extensions', nargs='*')
    return parser

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
        for f in files:
            if any([re.match(x, f) != None for x in arg.exclude]):
                print('skip %s' % f)
                continue
            newfiles = []
            dot0pos = f.find('.')
            fileext = '' if dot0pos < 0 else f[dot0pos:]
            of = os.path.join(pathname, f)
            nf = os.path.join(pathname, '%s%s' % (os.path.basename(pathname), fileext))
            nameconflict = nf in newfiles
            if nameconflict:
                print('error: file name to be renamed conflicted "%s/%s" <-> "%s/%s", will skip' % (pathname, f, pathname, nf))
            else:
                newfiles.append(nf)
            if arg.dry_run:
                print('mv "%s" "%s"' % (of, nf))
            else:
                if not nameconflict:
                    shutil.move(of, nf)

