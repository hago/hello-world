#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparser
import os

class runner():
    def __init__(self, args):
        self.cfg = args

    def run(self):
        f = 

if __name__=='''__main__''':
    parser = Argparser('namingfilesbydir', "rename all files under a directory after the directory's name, only ext differs")
    parser.add_argument('path', nargs="?", default="./")
    parser.add_argument('-n', '--dry-run', action='store_true', default=False)
    args = parser.parse_args()
    runner(args).run()
