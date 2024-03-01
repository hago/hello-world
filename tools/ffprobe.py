#!/usr/bin/env python3
# vim: set fileencoding: UTF-8 -*-

import argparse
import json
import sys

from subprocess import Popen, PIPE

def fetchdictchild(map: dict, *keys: str):
    current = map
    for k in keys:
        if current == None or type(current) != dict or k not in current:
            return None
        current = current[k]
    return current

def toint(v: str, default: int = 0) -> int:
    if v == None:
        return default
    else:
        try:
            return int(v)
        except ValueError:
            return default
        
def compute(v: str, default: float = 0.0) -> float:
    if v == None:
        return default
    else:
        try:
            return eval(v)
        except Exception:
            return default

def tofloat(v: str, default: float = 0.0) -> float:
    if v == None:
        return default
    else:
        try:
            return float(v)
        except ValueError:
            return default

class codec:
    def __init__(self) -> None:
        self.name = None
        self.profile = None
        self.longname = None
        self.type = None
        self.tag = None
        self.tag_string = None
        self.bitrate = None

    def load(self, streammap: dict):
        self.name = fetchdictchild(streammap, 'codec_name')
        self.longname = fetchdictchild(streammap, 'codec_long_name')
        self.bitrate = toint(fetchdictchild(streammap, 'bit_rate'))
        self.profile = fetchdictchild(streammap, 'profile')
        self.type = fetchdictchild(streammap, 'codec_type')
        self.tag = fetchdictchild(streammap, 'codec_tag')
        self.tag_string = fetchdictchild(streammap, 'codec_tag_string')
        
class streaminfo:
    def __init__(self) -> None:
        self.metadata = {}
        self.codec: codec = None

    def load(self, streammap: dict):
        self.codec = codec()
        self.codec.load(streammap)
        self.metadata = fetchdictchild(streammap, "tags")

    def isvideo(self):
        return self.codec != None and self.codec.type == 'video'

    def isaudio(self):
        return self.codec != None and self.codec.type == 'audio'

    def issubtitle(self):
        return self.codec != None and self.codec.type == 'subtitle'

class videoinfo:
    def __init__(self) -> None:
        self.streams = []
        self.metadata = {}

class audiostreaminfo(streaminfo):
    def __init__(self) -> None:
        super().__init__()
        self.samplerate = None
        self.channels = None
        self.samplefmt = None

    def load(self, streammap: dict):
        super().load(streammap)
        self.samplerate = fetchdictchild(streammap, "sample_rate")
        self.channels = fetchdictchild(streammap, "channels")
        self.samplefmt = fetchdictchild(streammap, "sample_fmt")

class videostreaminfo(streaminfo):
    def __init__(self) -> None:
        super().__init__()
        self.width= None
        self.height= None
        self.sar= '1:1'
        self.dar= None
        self.fps= None
        self.pix_fmt = None
        self.bits_per_raw_sample = None

    def load(self, streammap: dict):
        super().load(streammap)
        self.width = fetchdictchild(streammap, "width")
        self.height = fetchdictchild(streammap, "height")
        self.sar = fetchdictchild(streammap, "sample_aspect_ratio")
        self.dar = fetchdictchild(streammap, "display_aspect_ratio")
        fps = fetchdictchild(streammap, "avg_frame_rate")
        self.fps = compute(fps) if fps != None else None
        self.pix_fmt = fetchdictchild(streammap, "pix_fmt")
        self.bits_per_raw_sample = fetchdictchild(streammap, "bits_per_raw_sample")

class subtitlestreaminfo(streaminfo):
    def __init__(self) -> None:
        super().__init__()

    def load(self, streammap: dict):
        super().load(streammap)

def __createsttreaminfo(streammap: dict) -> streaminfo:
    codectype = fetchdictchild(streammap, 'codec_type')
    if codectype == 'audio':
        s = audiostreaminfo()
        s.load(streammap)
        return s
    elif codectype == 'video':
        s = videostreaminfo()
        s.load(streammap)
        return s
    elif codectype == 'subtitle':
        s = subtitlestreaminfo()
        s.load(streammap)
        return s
    else:
        sys.stderr.writelines(["Unknown codec type: %s" % codectype])
        return None

def probe(filename: str) -> videoinfo:
    if not __checkffprobe():
        raise OSError("ffprobe is not installed")
    jsonstr = __callffprobe(filename)
    jsonobj = json.loads(jsonstr)
    vi = videoinfo()
    vi.metadata = fetchdictchild(jsonobj, 'format', 'tags')
    streams = fetchdictchild(jsonobj, 'streams')
    vi.streams = [__createsttreaminfo(s) for s in streams]
    return vi
    
def __callffprobe(filename: str) -> str:
    with Popen(['ffprobe', '-i', filename, '-of', 'json', '-show_streams', '-show_format'], stdout=PIPE, stderr=PIPE) as fp:
        data = fp.stdout.read()
        return data.decode()

def __escapefn(fn: str):
    return fn.replace("'", "\\'").replace('"', '\\"').replace(" ", "\\ ")

def __checkffprobe():
    with Popen(["which", "ffprobe"], stdout=PIPE) as p:
        result = p.stdout.read()
    return result != None and result != ''

def buildargparser():
    parser = argparse.ArgumentParser(description='run ffprobe')
    parser.add_argument('-p', '--path', help = 'media file name', required=True)
    return parser

if __name__=='''__main__''':
    parser = buildargparser()
    arg = parser.parse_args()
    vi = probe(arg.path)
    print(json.dumps(vi, default=lambda s: s.__dict__, indent = 4))
