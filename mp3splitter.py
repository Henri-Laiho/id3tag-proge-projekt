from __future__ import print_function
import struct
import sys

from pydub import AudioSegment
from time import time
from subprocess import call

def fill0(t):
    return '0' + str(t) if t < 10 else str(t)

def hmsToMS(hms):
    s = hms.split(':')
    return int(s[0]) * 3600000 + int(s[1]) * 60000 + int(s[2]) * 1000

def msToHMS(ms):
    return fill0(ms//3600000) + ':' + fill0((ms//60000) % 60) + ':' + fill0((ms//1000) % 60)

def getFileDurationMS(file):
    return AudioSegment.from_mp3(file).duration_seconds * 1000

def extract_mp3_segment(src_file, start = 0, end = -1):
    outfile = 'temp/segment_' + str(int(time()*10000) % 1000000000) + '.mp3'
    if end < 0:
        end = getFileDurationMS(src_file) + end
        if end < 0: end = 0
    call("ffmpeg -y -i " + src_file + " -ss " + msToHMS(start) + " -t " + msToHMS(end-start) + " -map 0 -c:v libmp3lame -c:a copy " + outfile)
    return outfile

def merge_mp3_segments(sources):
    tempfile = 'temp/mergedata_' + str(int(time()*10000) % 1000000000) + '.txt'
    file = open(tempfile, 'w+')
    for src in sources:
        file.write("file '" + src + "'\n")
    file.close()
    outfile = 'temp/segment_' + str(int(time()*10000) % 1000000000) + '.mp3'
    call("ffmpeg -y -f concat -i " + tempfile + " -c copy " + outfile)
    return outfile

#def trim_mp3_segment(file, start, end):
#    call("ffmpeg -y -i " + file + " -ss " + msToHMS(start) + " -t " + msToHMS(end-start) + " -map 0 -c:v libmp3lame -c:a copy " + file)

def insert_mp3_segment(source, target, position):
    dur = getFileDurationMS(file)
    if position > 0 and position != -1 and position < dur:
        return merge_mp3_segments([extract_mp3_segment(target, 0, position), source, extract_mp3_segment(target, position, dur)])
    elif position == 0 and position != -1 and position < dur:
        return merge_mp3_segments([source, extract_mp3_segment(file, position, dur)])
    elif position > 0 and (position == -1 or position >= dur):
        return merge_mp3_segments([extract_mp3_segment(file, 0, position), source])
    return target

def delete_mp3_segment(file, start, end):
    dur = getFileDurationMS(file)
    if start > 0 and end != -1 and end < dur:
        return merge_mp3_segments([extract_mp3_segment(file, 0, start), extract_mp3_segment(file, end, dur)])
    elif start == 0 and end != -1 and end < dur:
        return extract_mp3_segment(file, end, dur)
    elif start > 0 and (end == -1 or end >= dur):
        return extract_mp3_segment(file, 0, start)
    elif start == 0 and (end == -1 or end >= dur):
        return extract_mp3_segment(file)
    return file


