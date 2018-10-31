import os
import re
import subprocess
from datetime import datetime

def fill0(t):
    return '0' + str(t) if t < 10 else str(t)

def hmsToMS(hms):
    s = hms.split(':')
    return int(s[0]) * 3600000 + int(s[1]) * 60000 + int(s[2]) * 1000

def msToHMS(ms):
    return fill0(ms//3600000) + ':' + fill0((ms//60000) % 60) + ':' + fill0((ms//1000) % 60)

def cls():
    os.system('cls' if os.name=='nt' else 'clear')
    
def play(audio_file_path):
    subprocess.call(["ffplay", "-volume", "7", "-showmode", "1", "-autoexit", audio_file_path])
    
def metric_prefix(value):
    prefixes = ('', 'k', 'M', 'G', 'T', 'P')
    for i in range(len(prefixes)-1, -1, -1):
        if 10**(i*3) < value:
            return str(round(value / 10**(i*3), 2)) + ' ' + prefixes[i]
    return str(value) + ' '

def durationToStr(duration):
    duration = int(round(duration))
    ret = ((str(duration//3600)+':'+fill0(duration//60%60)) if duration//3600 else fill0(duration//60)) + ':' + fill0(duration%60)
    return ' '*max(8-len(ret), 0) + ret

def datetimeToStr(date):
    return (' ' if date.day < 10 else '') + str(date.day) + '/' + ('0' if date.month < 10 else '') + str(date.month) + '/' + str(date.year) + ('  ' if date.hour < 10 else ' ') + str(date.hour) + (':0' if date.minute < 10 else ':') + str(date.minute)

def get_drives():
    return [drive[:-1] for drive in re.findall(r"[A-Z]+:.*$",os.popen("mountvol /").read(),re.MULTILINE)]

#def progressBar(value, endvalue, bar_length=20):
#        percent = float(value) / endvalue
#        arrow = '-' * int(round(percent * bar_length)-1) + '>'
#        spaces = ' ' * (bar_length - len(arrow))
#
#        print("\rPercent: [{0}] {1}%".format(arrow + spaces, int(round(percent * 100))), end='')
