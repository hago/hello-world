#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import os.path
import shutil
import sys

class files_grouper:
    def __init__(self, args):
        self.cfg = args
        self.rootpath = os.path.realpath(args.path)

    def run(self):
        with os.scandir(self.rootpath) as l:
            files = [f.name for f in l if f.is_file()]
        print(files)
        self.__runfilesgrouping(files)

    def __runfilesgrouping(self, files):
        groupmap = self.__buildgroup(files)
        with os.scandir(self.rootpath) as l:
            dirs = [f.name for f in l if f.is_dir()]
            for d in dirs:
                if d in groupmap:
                    sys.stderr.write('directory %s existed, aborting.%s' % (os.path.join(self.rootpath, d), os.sep))
                    sys.exit(-1)
        for d in groupmap:
            path = os.path.join(self.rootpath, d)
            print('mkdir %s' % path)
            if not self.cfg.dry_run:
                os.mkdir(path)
            for f in groupmap[d]:
                oldfile = os.path.join(self.rootpath, f)
                newfile = os.path.join(self.rootpath, d, f)
                print('mv %s %s' % (oldfile, newfile))
                if not self.cfg.dry_run:
                    shutil.move(oldfile, newfile)
    
    def __buildgroup(self, files):
        keyprepare = lambda f: [segment.strip() for segment in (f.split('.') if self.cfg.groupby == 'dotslice' else f)]
        keystringify = lambda sl: '.'.join(sl) if self.cfg.groupby == 'dotslice' else sl
        amap = {}
        for f in files:
            slices = keyprepare(f)
            rawk = slices[:self.cfg.count] if self.cfg.count > 0 else slices[self.cfg.count:]
            k = keystringify(rawk)
            if k in amap:
                amap[k].append(f)
            else:
                amap[k] = [f]
        return amap

if __name__=='''__main__''':
    parser = argparse.ArgumentParser('groupfiles', 'Group files by parts of the names')
    parser.add_argument('-g', '--groupby', choices=['dotslice', 'chars'], required=True)
    parser.add_argument('-c', '--count', type=int, default=1, help='number of units to grouping by, nagative means counting reversely')
    parser.add_argument('path', default="./", nargs="?")
    parser.add_argument('-n', '--dry-run', action='store_true', default=False)
    args = parser.parse_args()
    print(args)
    files_grouper(args).run()
