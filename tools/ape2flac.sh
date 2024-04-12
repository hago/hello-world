#!/bin/bash

if [ $# -eq 0 ]
then
	echo "Usage: $0 apefile cuefile"
	exit 1
fi
enc=`file -bi $2|sed "s/.*charset=//"`
shopt -s nocasematch
if [ $enc != utf-8 ]; then
	iconv -f $enc -t utf-8 -o $2.utf8.cue $2
	cue=$2.utf8.cue
else
	cue=$2
fi
ffmpeg -i "$1" "$1.flac"
if [ $# -gt 1 ]
then
	shntool split -f "$cue" -t "%n_%t" -o flac "$1.flac"
	rm "$1.flac"
	if [ -f 00_pregap.flac ]
	then
		rm 00_pregap.flac
	fi
fi
