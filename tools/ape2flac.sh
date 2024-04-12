#!/bin/sh

if [ $# -eq 0 ]
then
	echo "Usage: $0 apefile cuefile"
	exit 1
fi
ffmpeg -i "$1" "$1.flac"
if [ $# -gt 1 ]
then
	shntool split -f "$2" -t "%n_%t" -o flac "$1.flac"
	rm "$1.flac"
	if [ -f 00_pregap.flac ]
	then
		rm 00_pregap.flac
	fi
fi
