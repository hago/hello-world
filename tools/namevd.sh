#!/bin/bash
#find those directories that contains only one file, then:
#1. move the file to ../
#2. rename it to the directory, keeping extension name unchanges
#3. remove the empty directory

if [ $# -lt 1 ]; then
	echo "usage $0 [-c] dir dir ..."
	exit 2
fi
if [[ "$1" != "-c" ]]; then
	RED='\033[0;31m'
	GREEN='\033[0;32m'
else
	shift
	RED=''
	GREEN=''
fi
IFS=$'\n'
shopt -s nocasematch
while (( "$#" )); do
	p=${1%/}
	#echo "p: $p"
	for f in `ls $1`
	do
		ext=''
		#echo "f: $f"
		if [[ $f == *.hevc.mp4 ]]; then
			ext=".hevc.mp4"
		elif [[ $f == *.mp4 ]]; then
			ext=".mp4"
		elif [[ $f == *.mkv ]]; then
			ext=".mkv"
		elif [[ $f == *.thumb.jpg ]]; then
			ext=".thumb.jpg"
		elif [[ $f == *.jpg ]]; then
			ext=".jpg"
		elif [[ $f == *.thumb.png ]]; then
			ext=".thumb.png"
		elif [[ $f == *.png ]]; then
			ext=".png"
		else
			echo -e "${RED}skip: $f" >&2
		fi
		if [[ "$ext" != "" ]]; then
			t="$p/$p$ext"
			#echo "t: $t"
			if [ -f "$t" ]; then
				echo -e "${RED}EXISTED and skip: $t" >&2
			else
				echo -e "${GREEN}mv \"$p/$f\" \"$p/$p$ext\""
			fi
		fi
	done
	shift
done
