#!/usr/bin/env python3
# vim: set fileencoding: UTF-8 -*-

import argparse
import os.path
import sys

import iso639
import ollama
import srt

ISO639_1_CODES = [x.part1 for x in iso639.ALL_LANGUAGES if x.part1 is not None]

class TranslateSRT:
    def __init__(self, input_file, ollama_host_port:str,to_language:str, output_file=None):
        self.input_file = input_file
        self.to_language = to_language
        self.output_file = output_file
        self.ollama_host_port = ollama_host_port

    def __run():
        pass

def buildargparser():
    parser = argparse.ArgumentParser(description='Translate SRT subtitles using Ollama and translategemma model.')
    parser.add_argument('-in', '--input', help = 'The srt file to be translated', required=True, type=str)
    parser.add_argument('-tl', '--to-language'
                        , help = 'The language to be translated to, see ISO639-1 codes: https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes.'
                        , required=False, default='en', type=str, choices=ISO639_1_CODES)
    parser.add_argument('-out', '--output'
                        , help = 'The target srt file to create, by default it will be outputted to stdout.'
                        , required=False, default=None, type=str)
    parser.add_argument('-ollama', '--ollama-host-port', default='127.0.0.1:11434', help = 'The ollama host, by default "127.0.0.1:11434"', type=str)
    return parser

if __name__ == "__main__":
    parser = buildargparser()
    args = parser.parse_args()
    if not os.path.exists(args.input):
        sys.stderr.write(f"Input file does not exist: {args.input}\n")
        sys.exit(1)
    translator = TranslateSRT(args.input, args.to_language, args.output, args.ollama_host_port)
    translator.run()
    