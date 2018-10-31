import os

def cls():
    os.system('cls' if os.name=='nt' else 'clear')
    
def metric_prefix(value):
    prefixes = ('', 'k', 'M', 'G', 'T', 'P')
    for i in range(len(prefixes)-1, -1, -1):
        if 10**(i*3) < value:
            return str(round(value / 10**(i*3), 2)) + ' ' + prefixes[i]
    return str(value) + ' '

from datetime import datetime
def datetimeToStr(date):
    return (' ' if date.day < 10 else '') + str(date.day) + '/' + ('0' if date.month < 10 else '') + str(date.month) + '/' + str(date.year) + ('  ' if date.hour < 10 else ' ') + str(date.hour) + (':0' if date.minute < 10 else ':') + str(date.minute)

import os, re
def get_drives():
    return [drive[:-1] for drive in re.findall(r"[A-Z]+:.*$",os.popen("mountvol /").read(),re.MULTILINE)]

def progressBar(value, endvalue, bar_length=20):
        percent = float(value) / endvalue
        arrow = '-' * int(round(percent * bar_length)-1) + '>'
        spaces = ' ' * (bar_length - len(arrow))

        print("\rPercent: [{0}] {1}%".format(arrow + spaces, int(round(percent * 100))), end='')