#!/usr/bin/env python3
# vim: set fileencoding: UTF-8 -*-

import argparse
import logging
import os.path
import sys

import iso639
import ollama
import srt

ISO639_1_CODES = [x.part1 for x in iso639.ALL_LANGUAGES if x.part1 is not None]

class TranslateSRT:
    def __init__(self, input_file, ollama_host_port:str,to_language:str, output_file=None, cross_ref_subs_output=None):
        self.input_file = input_file
        self.to_language = to_language
        self.output_file = output_file
        self.ollama_host_port = ollama_host_port
        self.cross_ref_subs_output = cross_ref_subs_output
        language_name = iso639.to_name(to_language)
        self.__prompt = f"You are an professional interpreter. Translate the following text to {language_name} and put the translation betwen tag pair <result>:\n%s"

    def __load_srt(self):
        with open(self.input_file, 'r', encoding='utf-8') as f:
            srt_content = f.read()
        return list(srt.parse(srt_content))

    def __translate_text(self, text):
        rsp = ollama.chat(
            self.ollama_host_port
            , "translategemma"
            , messages=[
                {
                    "role": "user", 
                    "content": self.__prompt % text
                }
            ]
        )
        logging.debug(f"Translation response: {rsp}")
        return rsp['content'].split('<result>')[1].split('</result>')[0].strip()

    def run(self):
        original_subs = self.__load_srt()
        translated_subs = []
        translate_cr_subs = []
        for sub in original_subs:
            translated_text = self.__translate_text(sub.content)
            translated_subs.append(srt.Subtitle(index=sub.index, start=sub.start, end=sub.end, content=translated_text))
            if self.cross_ref_subs_output != None:
                translate_cr_subs.append(srt.Subtitle(index=sub.index, start=sub.start, end=sub.end, content=f"{sub.content}\n{translated_text}"))
        srt_output = srt.compose(translated_subs)
        if self.output_file:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write(srt_output)
        if self.cross_ref_subs_output != None:
            cr_srt_output = srt.compose(translate_cr_subs)
            if self.output_file:
                with open(f"{self.output_file}.cr", 'w', encoding='utf-8') as f:
                    f.write(cr_srt_output)

def buildargparser():
    parser = argparse.ArgumentParser(description='Translate SRT subtitles using Ollama and translategemma model.')
    parser.add_argument('-in', '--input', help = 'The srt file to be translated', required=True, type=str)
    parser.add_argument('-tl', '--to-language'
                        , help = 'The language to be translated to, see ISO639-1 codes: https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes.'
                        , required=False, default='en', type=str, choices=ISO639_1_CODES)
    parser.add_argument('-out', '--output'
                        , help = 'The target srt file to create, by default it will be outputted to stdout.'
                        , required=False, default=None, type=str)
    parser.add_argument('-crout', '--cross-ref-subs-output', default=None, type=str
                        , help = 'The target srt file for cross reference subtitles, by default it will not create cross reference subtitles.')
    parser.add_argument('-ollama', '--ollama-host-port', default='127.0.0.1:11434', help = 'The ollama host, by default "127.0.0.1:11434"', type=str)
    return parser

if __name__ == "__main__":
    parser = buildargparser()
    args = parser.parse_args()
    if not os.path.exists(args.input):
        sys.stderr.write(f"Input file does not exist: {args.input}\n")
        sys.exit(1)
    translator = TranslateSRT(args.input, args.to_language, args.output, args.ollama_host_port, args.cross_ref_subs_output)
    translator.run()
