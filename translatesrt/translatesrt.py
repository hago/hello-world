#!/usr/bin/env python3
# vim: set fileencoding: UTF-8 -*-

#requires: pip install python-iso639 ollama srt

import argparse
import logging
import os.path
import re
import sys

import iso639
import ollama
import srt

MODEL_NAME = "translategemma:12b"
ISO639_1_CODES = sorted([x.part1 for x in iso639.ALL_LANGUAGES if x.part1 is not None])
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def if_srt_uses_seconds(secondstr:str) -> bool:
    l = re.findall('(.*)-->(.*)', secondstr)
    if len(l) == 0:
        return False
    else:
        for (s, e) in l[:10]:
            if not re.match(r'^\d+(\.\d+)?$', s.strip()) or not re.match(r'^\d+(\.\d+)?$', e.strip()):
                return False
        return True

def fix_srt_timedelta_to_timecode(srt_content:str) -> str:
    lines = srt_content.splitlines()
    i = 0
    while i < len(lines):
        l = lines[i]
        s = l.strip()
        if s == '':
            i += 1
            continue
        if s.isdigit():
            i += 1
            timeline = lines[i].strip()
            parts = timeline.split(' --> ')
            if len(parts) != 2:
                raise ValueError(f"Expected timeline at line {i+1}, got: {timeline}")
            lines[i] = f"{seconds_to_timecode(parts[0])} --> {seconds_to_timecode(parts[1])}"
            i += 1
            while i < len(lines) and lines[i].strip() != '':
                i += 1
        else:
            raise ValueError(f"Expected subtitle index at line {i+1}, got: {s}")
    return "\n".join(lines)

def seconds_to_timecode(secondstr:str) -> str:
    (p1, p2) = secondstr.split('.')
    seconds = int(p1)
    milliseconds = int(p2)    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}.{milliseconds:03}"

class TranslateSRT:
    def __init__(self, input_file:str, ollama_host_port:str, to_language:str, output_file:str=None, cross_ref_subs_output:str=None):
        self.input_file = input_file
        self.to_language = to_language
        self.output_file = output_file
        self.ollama_host_port = ollama_host_port
        self.cross_ref_subs_output = cross_ref_subs_output
        self.__to_language_name = iso639.Language.from_part1(to_language).name
        self.__init_ollama_client()
        self.__prompt = f"""
        You are an professional interpreter. In the following conversation, translate every sentence directly to {self.__to_language_name} and wrap each result with << and >>.
        If there are multiple possible ways to do it, use the most direct one and do not provide any other options.
        """

    def __init_ollama_client(self):
        self.__client = ollama.Client(host=self.ollama_host_port)
        logging.debug("Ollama client created")

    def __load_srt(self):
        with open(self.input_file, 'r', encoding='utf-8') as f:
            srt_content = f.read()
        if if_srt_uses_seconds(srt_content):
            logging.warning(f'{self.input_file} is not a well formed srt file with seconds instead of timecodes.')
            logging.warning(f'Converting srt file from seconds to timecode format and a converted srt will be saved as {self.input_file}.conv')
            srt_content = fix_srt_timedelta_to_timecode(srt_content)
            with open(f"{self.input_file}.conv", 'w', encoding='utf-8') as f:
                f.write(srt_content)
        return list(srt.parse(srt_content))

    def __translate_text(self, text:str) -> str:
        logging.debug(f"Translating text: {text}")
        rsp = self.__client.chat(
            model = MODEL_NAME,
            messages=[
                {
                    "role": "user", 
                    "content": self.__prompt
                },
                {
                    "role": "user", 
                    "content": text
                }]
        )
        logging.debug(f"Translation response: {rsp}")
        translations = self.__parse_result(rsp)
        if len(translations) != 1 or translations[0] == '':
            messages = [{
                "role": "user", 
                "content": "Your answer does not contain the translation of the input. Please provide translation and wrap each translation with << and >>."
            }]
            rsp = self.__client.chat(
                model = MODEL_NAME,
                messages = messages
            )
            translations = self.__parse_result(rsp)
        if len(translations) == 1:
            logging.debug(f"{text} -> {translations[0]}")
            if translations[0] != '':
                return translations[0]
            else:
                logging.warning(f"Translation result not parsed correctly, returning raw response content: {rsp['message']['content']}")
                return rsp['message']['content']
        elif len(translations) == 0:
            logging.error(f"Failed to translate text: {text}. Response: {rsp}")
            return None
        else:
            logging.warning(f"{text} may have multiple translations.")
            return " 或者 ".join(['"{t}"' for t in translations])

    '''
    rsp is the response from the Ollama chat API, which is a dictionary containing the model's output. 
    The function uses a regular expression to find all occurrences of text wrapped in << and >> in the 'content' field of the 'message' key of the response. 
    It returns a list of these translations.
    '''
    def __parse_result(self, rsp:ollama.ChatResponse) -> list[str]:
        translations = re.findall(r'<<(.+?)>>', rsp['message']['content'])
        return [x.strip() for x in translations]

    def run(self):
        original_subs = self.__load_srt()
        translated_subs = []
        translate_cr_subs = []
        for i in range(len(original_subs)):
            logging.debug(f"Translating subtitle {i+1}")
            while True:
                try:
                    translated = self.__translate_text(original_subs[i].content)
                    break
                except ollama.ResponseError as e:
                    if e.message.contains("prediction aborted, token repeat limit reached"):
                        logging.warning(f"Token repeat limit reached for subtitle {i + 1}, recreate client.")
                        self.__client.close()
                        self.__init_ollama_client()
                        continue
                    else:
                        logging.error(f"Unexpected error during translation for subtitle {i + 1}: {e}")
                        raise e
            if translated == '':
                logging.warning(f"Subtitle {i + 1} translation is empty, using original content.")
            if self.output_file != None:
                translated_subs.append(srt.Subtitle(index=original_subs[i].index, start=original_subs[i].start, end=original_subs[i].end,
                                                    content=translated if translated != None else f'{original_subs[i].content} translation failed'))
            else:
                print(f"subtitle {i}: {original_subs[i].content} --> {translated}")
            if self.cross_ref_subs_output != None:
                translate_cr_subs.append(srt.Subtitle(index=original_subs[i].index, start=original_subs[i].start, end=original_subs[i].end, 
                                                  content=f"{original_subs[i].content}\n{translated}"))
            i += 1
        self.__client.close()
        logging.info(f"Translation completed, writing to output file: {self.output_file}")
        srt_output = srt.compose(translated_subs)
        if self.output_file != None:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write(srt_output)
        if self.cross_ref_subs_output != None:
            cr_srt_output = srt.compose(translate_cr_subs)
            with open(f"{self.cross_ref_subs_output}", 'w', encoding='utf-8') as f:
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
        logging.error(f"Input file does not exist: {args.input}")
        sys.exit(1)
    translator = TranslateSRT(args.input, args.ollama_host_port, args.to_language, args.output, args.cross_ref_subs_output)
    translator.run()
