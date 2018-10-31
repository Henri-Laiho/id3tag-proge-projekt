from lisad import *
from sys import argv
from prefilled_input import prefilled_input
from getch import getch # 1 täht korraga lugemine
from fs import open_fs

import fs
import eyed3

columns = { 0:'Directory', 1:'Name', 2:'Size', 3:'Modified', 4:'Created', 5:'Sample Rate', 6:'Bit Rate',
            7:'Channels', 8:'Duration', 9:'Title', 10:'Artist', 11:'Album', 12:'Album Artist',
            13:'Contributing Artists', 14:'Track Number', 15:'Year', 16:'Genre', 17:'Composer', 18:'Writer',
            19:'Key', 20:'BPM' }
column_sizes = [3, 24, 8, 16, 16, 8, 9, 7, 9, 8, 8, 8, 8, 8, 4, 4, 10, 8, 8, 3, 4]

drives = get_drives()
b_drives = [drive[0].encode() for drive in drives]

columns_visible = [0, 1, 2, 3, 4]
sorted_by = 1
view_lines = 32
cursor_line = 0
cursor_column = 0
view_position = 0
editing = False
current_dir = '/'
last_dir = ''
path_prefix = '<home>'
message = ''
dir = []

home_fs = open_fs('.')

bell_on = True
def bell():
    if bell_on:
        print('\a')

# loob kirje failide nimekirja lisamiseks; määramata väärtustele paneb väärtuseks '?'
def list_entry(**data):
    return tuple([data.get(y, '?') for x, y in columns.items()])

def pgup():
    global cursor_line, view_position
    cursor_line -= view_lines
    view_position -= view_lines
    if cursor_line < 0: cursor_line = 0
    if view_position < 0: view_position = 0

def pgdown():
    global cursor_line, view_position
    cursor_line += view_lines
    view_position += view_lines
    if cursor_line >= len(dir)-1: cursor_line = len(dir)-2
    if view_position + view_lines >= len(dir)-1: view_position = len(dir)-1-view_lines

#kui kasutaja vajutab nool üles
def up():
    global cursor_line, view_position
    if cursor_line > 0:
        cursor_line -= 1
        if view_position > cursor_line:
            view_position = cursor_line
    else:
        bell()

#kui kasutaja vajutab nool alla
def down():
    global cursor_line, view_position
    if cursor_line < len(dir)-1:
        cursor_line += 1
        if view_position + view_lines <= cursor_line:
            view_position = cursor_line - view_lines + 1
    else:
        bell()

#kui kasutaja vajutab nool paremale
def right():
    global cursor_column
    if cursor_column < len(columns_visible)-1:
        cursor_column += 1

#kui kasutaja vajutab nool vasakule
def left():
    global cursor_column
    if cursor_column > 0:
        cursor_column -= 1

def saveInfo():
    pass

def enter():
    global current_dir, cursor_line, editing, view_position
    
    if editing:
        
        
        
        
        editing = False
    else:
        if dir[cursor_line][0] == 'DIR':
            if cursor_line == 0:
                current_dir = current_dir[:current_dir[:-1].rfind('/') + 1]
                if current_dir == '':
                    current_dir = '/'
            else:
                current_dir += dir[cursor_line][1] + '/'
            cursor_line = 0
            view_position = 0
    
while True:
    cls() # tühjendab ekraani
    if message != '':
        print(message, end='')
        message = ''
    print(path_prefix + current_dir)
    
    # pealkirjad
    print(('  ' if cursor_column == 0 else '') + '    ', end='')
    for col in columns_visible[1:]:
        print(('  ' if cursor_column == col else '') +
            (columns[col] if len(columns[col]) < column_sizes[col] + 1 else columns[col][:column_sizes[col]-3]) +
            ('... ' if len(columns[col])-1 > column_sizes[col] else '' ) +
            ('\33[0m' if editing and cursor_line == i and cursor_column == col else '') + # värvimuutus tagasi
            ' '*(column_sizes[col] - len(columns[col]) + 1), end='')
    print()
    
    # andmete uuendamine
    if last_dir != current_dir:
        try:
            dir = [list_entry(Directory=('DIR' if file.is_dir else 'F  '),
                              Name=file.name,
                              Size=('' if file.is_dir else (metric_prefix(file.size) + 'B')),
                              Modified=datetimeToStr(file.modified),
                              Created=datetimeToStr(file.created)
                              ) for file in home_fs.scandir(current_dir, namespaces=['details'])]
        except (PermissionError, fs.errors.DirectoryExpected):
            message += 'Access denied.\n'
            current_dir = current_dir[:current_dir[:-1].rfind('/') + 1]
            if current_dir == '':
                    current_dir = '/'
            continue
            
        
        if sorted_by < 2:
            dir.sort(key=lambda x: (x[0], x[1].lower()))
        else:
            dir.sort(key=lambda x: x[sorted_by].lower())
        dir.insert(0, list_entry(Directory='DIR', Name='..'))
    
    # ekraanil nähtavad read
    for i in range(view_position, min(view_position + view_lines, len(dir))):4
        for col in columns_visible:
            print(((('> \33[6m' if editing else '> ') if cursor_line == i else '  ') if cursor_column == col else '') +
                  (dir[i][col] if len(dir[i][col]) < column_sizes[col] + 1 else dir[i][col][:column_sizes[col]-3]) +
                  ('... ' if len(dir[i][col])-1 > column_sizes[col] else '' ) +
                  ('\33[0m' if editing and cursor_line == i and cursor_column == col else '') + # värvimuutus tagasi
                  ' '*(column_sizes[col] - len(dir[i][col]) + 1), end='')
        print()
    
    # sisend
    ch = getch()
    special_ch = ch == b'\xe0'
    if special_ch:
        print(ch, end='')
        ch = getch()
    if ch:
        print(ch, end='')
        print()
        if ch == b'q':
            break
        elif ch in b_drives: # Kõvaketta vahetus
            home_fs = open_fs(ch.decode() + ':/')
            current_dir = '/'
            path_prefix = ch.decode() + ':/'
            cursor_line = 0
            view_position = 0
        elif special_ch and ch == b'H':
            up()
        elif special_ch and ch == b'P':
            down()
        elif special_ch and ch == b'M':
            right()
        elif special_ch and ch == b'K':
            left()
        elif special_ch and ch == b'I':
            pgup()
        elif special_ch and ch == b'Q':
            pgdown()
        elif ch == b'\x1b': # esc
            pass
        elif ch == b'\x08': # backspace
            current_dir = current_dir[:current_dir[:-1].rfind('/') + 1]
            if current_dir == '':
                    current_dir = '/'
            cursor_line = 0
            view_position = 0
        elif ch == b'\r':
            enter()








#from pynput import keyboard

# The key combination to check
#COMBINATIONS = [
#    {keyboard.Key.enter}
#]

# The currently active modifiers
#current = set()
#
#def execute(combination):
#    print ("Do Something")
#
#def on_press(key):
#    if any([key in COMBO for COMBO in COMBINATIONS]):
#        current.add(key)
#        if any(all(k in current for k in COMBO) for COMBO in COMBINATIONS):
#            execute(COMBO)
#
#def on_release(key):
#    if any([key in COMBO for COMBO in COMBINATIONS]):
#        current.remove(key)


#with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
#    listener.join()


