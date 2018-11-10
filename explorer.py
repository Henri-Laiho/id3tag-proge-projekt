from lisad import *
from sys import argv
from prefilled_input import prefilled_input
from getch import getch # 1 täht korraga lugemine
from fs import open_fs
from mutagen.easyid3 import EasyID3
from colorama import init, Fore, Back
init()

import os
import fs
import mutagen

colors = True

extensions = (".mp3", ".aac", ".flac", ".m4a", ".mka", ".mp4", ".mxmf", ".ogg", ".wav", ".webm")
columns = { 0:'Directory', 1:'Name', 2:'Size', 3:'Modified', 4:'Created', 5:'Sample Rate', 6:'Bit Rate',
            7:'Channels', 8:'Duration', 9:'Title', 10:'Artist', 11:'Album', 12:'Album Artist',
            13:'Genre', 14:'Track Number', 15:'Year', 16:'Conductors', 17:'Composer', 18:'Writer',
            19:'Key', 20:'BPM' }
mutagen_names = { 0:'', 1:'', 2:'', 3:'', 4:'', 5:'samplerate', 6:'bitrate',
            7:'channels', 8:'duration', 9:'title', 10:'artist', 11:'album', 12:'albumartist',
            13:'genre', 14:'tracknumber', 15:'date', 16:'conductor', 17:'composer', 18:'writer',
            19:'key', 20:'bpm' }
# veergude laiused tähemärkides
#               0   1   2   3   4   5   6  7  8   9  10  11  12  13 14 15  16  17  18 19 20
column_sizes = [3, 24, 10, 16, 16, 11, 11, 8, 9, 16, 16, 10, 10, 10, 8, 5, 10, 10, 10, 4, 4]

drives = get_drives()
b_drives = [drive[0].encode() for drive in drives]

# hetkel nähtaval olevad veerud, numbrid vastavad võtmetele sõnastukus 'columns'
columns_visible = [0, 1, 2, 3, 6, 8, 9, 10, 11, 13, 15, 16, 17, 19, 20]
sorted_by = 1     # veeru number, mille järgi sorteeritakse failid
view_lines = 32   # korraga ekraanil olevate ridade arv, suurem arv teeb programmi aeglasemaks
view_position = 0 # esimese rea number, mis on ekraanil näha
cursor_line = 0   # kursori rida
cursor_column = 0 # kursori veerg
editing = False   # kas hetkel muudetakse mingit väärtust

# esialgse kausta valimine
current_dir = os.getcwd().replace('\\', '/') + '/'
path_prefix = current_dir[0] + ':/' # sisaldab ketta nime nt 'C:/'
last_prefix = ''
current_dir = current_dir[2:]
last_dir = '' # viimati avatud kaust, kui on sama, mis current_dir, siis ei hakata uuesti kausta läbi lugema
message = '' # sõnum, mida kuvatakse esimesel real 1 kord; sobib veateadete kuvamiseks
dir = [] # avatud kausta sisu, mida kuvatakse ekraanil

home_fs = open_fs(path_prefix)

# tekitab helisignaali; vaigistamiseks: bell_on = False
bell_on = True
def bell():
    if bell_on:
        print('\a')

# loob kirje failide nimekirja lisamiseks; määramata väärtustele paneb väärtuseks ''
def list_entry(**data):
    return [data.get(y, '') for x, y in columns.items()]

# kui kasutaja vajutab pageup
def pgup():
    global cursor_line, view_position
    cursor_line -= view_lines
    view_position -= view_lines
    if cursor_line < 0: cursor_line = 0
    if view_position < 0: view_position = 0

# kui kasutaja vajutab pagedown
def pgdown():
    global cursor_line, view_position
    cursor_line += view_lines
    view_position += view_lines
    if cursor_line >= len(dir)-1: cursor_line = len(dir)-2
    if view_position + view_lines >= len(dir)-1: view_position = len(dir)-1-view_lines

# kui kasutaja vajutab nool üles
def up():
    global cursor_line, view_position
    if cursor_line > 0:
        cursor_line -= 1
        if view_position > cursor_line:
            view_position = cursor_line
    else:
        bell()

# kui kasutaja vajutab nool alla
def down():
    global cursor_line, view_position
    if cursor_line < len(dir)-1:
        cursor_line += 1
        if view_position + view_lines <= cursor_line:
            view_position = cursor_line - view_lines + 1
    else:
        bell()

# kui kasutaja vajutab nool paremale
def right():
    global cursor_column
    if cursor_column < len(columns_visible)-1:
        cursor_column += 1

# kui kasutaja vajutab nool vasakule
def left():
    global cursor_column
    if cursor_column > 0:
        cursor_column -= 1

def saveInfo():
    pass

# ütleb, kas praegu kursori all olev lahter on muudetav
def isCellEditable():
    return (columns_visible[cursor_column] == 1
            or any(dir[cursor_line][1].endswith(ext) for ext in extensions)
            and columns_visible[cursor_column] > 8)

# kui kasutaja vajutab enter
def enter():
    global current_dir, cursor_line, view_position, dir
    
    if isCellEditable():
        file = dir[cursor_line]
        column = columns_visible[cursor_column]
        # ümbernimetamine
        if column == 1:
                        try:
                prevname=file[1]
                newname=input()
                os.rename(path_prefix + current_dir + file[column],newname)
                file[1]=newname
            except:
                message= "File with that name already exists in directory"
        # tag'i muutmine
        elif file[0] != 'DIR':
            # faili avamine
            try:
                audio = mutagen.File(path_prefix + current_dir + file[1])
            except mutagen.MutagenError:
                message = "Can't edit tags"
                return
            if audio != None:
                if isinstance(audio.tags, mutagen.id3.ID3):
                    audio = EasyID3(path_prefix + current_dir + file[1])
                    if audio == None:
                        message = 'ID3 error\n'
                        return
                    
                # andmete sisestamine
                audio[mutagen_names[column]] = [x.strip() for x in
                                                prefilled_input(columns[column] + ': ',
                                                               '; '.join(audio[mutagen_names[column]])
                                                               if mutagen_names[column] in audio
                                                               else '').split(';')
                                                ]
                file[column] = audio[mutagen_names[column]]
                if isinstance(file[column], list):
                    file[column] = '; '.join(file[column])
                # andmete salvestamine
                audio.save()
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
        elif isCellEditable():
            pass
        elif any([dir[cursor_line][1].endswith(x, -6) for x in extensions]):
            play(path_prefix + current_dir + dir[cursor_line][1])
            
    
while True:
    cls() # tühjendab ekraani
    if message != '':
        print(message, end='')
        message = ''
    # väljastab hetkel avatud kausta teekonna
    print(path_prefix + current_dir)
    
    # veergude pealkirjad
    print(('  ' if columns_visible[cursor_column] == 0 else '') + '    ', end='')
    for col in columns_visible[1:]:
        print(('  ' if columns_visible[cursor_column] == col else '') +
            (columns[col] if len(columns[col]) < column_sizes[col] + 1 else columns[col][:column_sizes[col]-3]) +
            ('... ' if len(columns[col])-1 > column_sizes[col] else '' ) +
            ('\33[0m' if editing and cursor_line == i and cursor_column == col else '') + # värvimuutus tagasi
            ' '*(column_sizes[col] - len(columns[col]) + 1), end='')
    print()
    
    # kausta sisu uuendamine
    if last_dir != current_dir or last_prefix != path_prefix:
        try:
            # failide, alamkaustade leidmine
            dir = [list_entry(Directory=('DIR' if file.is_dir else 'F  '),
                              Name=file.name,
                              Size=('' if file.is_dir else (metric_prefix(file.size) + 'B')),
                              Modified=datetimeToStr(file.modified),
                              Created=datetimeToStr(file.created)
                              ) for file in home_fs.scandir(current_dir, namespaces=['details'])]
            
            # metadata, id3 tagide lugemine
            for i in range(len(dir)):
                file = dir[i]
                if file[0] != 'DIR':
                    try:
                        audio = mutagen.File(path_prefix + current_dir + file[1])
                    except mutagen.MutagenError:
                        continue
                    if audio != None:
                        if hasattr(audio.info, 'bitrate') and audio.info.bitrate: file[6] = metric_prefix(audio.info.bitrate) + 'bps'
                        if hasattr(audio.info, 'samplerate') and audio.info.samplerate: file[6] = str(audio.info.samplerate)
                        if hasattr(audio.info, 'length') and audio.info.length: file[8] = durationToStr(audio.info.length)
                        if isinstance(audio.tags, mutagen.id3.ID3):
                            audio = EasyID3(path_prefix + current_dir + file[1])
                            if audio == None:
                                continue
                            
                        for q in range(9, 21):
                            if mutagen_names[q] in audio:
                               file[q] = audio[mutagen_names[q]]
                        #if 'title' in audio: file[9] = audio['title']
                        #if 'artist' in audio: file[10] = audio['artist']
                        #if 'album' in audio: file[11] = audio['album']
                        #if 'albumartist' in audio: file[12] = audio['albumartist']
                        #if 'contributingartists' in audio: file[13] = audio['contributingartists']
                        #if 'tracknumber' in audio: file[14] = audio['tracknumber']
                        #if 'date' in audio: file[15] = audio['date']
                        #if 'genre' in audio: file[16] = audio['genre']
                        #if 'composer' in audio: file[17] = audio['composer']
                        #if 'writer' in audio: file[18] = audio['writer']
                        #if 'key' in audio: file[19] = audio['key']
                        #if 'bpm' in audio: file[20] = audio['bpm']
                        
                
        except (PermissionError, fs.errors.DirectoryExpected):
            message += 'Access denied.\n'
            current_dir = current_dir[:current_dir[:-1].rfind('/') + 1]
            if current_dir == '':
                    current_dir = '/'
            continue
            
        # kui mõni id3-tag on järjend, siis see tehakse sõneks eraldajatega '; ' (ainult ekraanil kuvamise jaoks)
        for i in range(len(dir)):
            for q in range(len(dir[i])):
                if isinstance(dir[i][q], list):
                    dir[i][q] = '; '.join(dir[i][q])
        
        # kausta sorteerimine
        if sorted_by < 2:
            dir.sort(key=lambda x: (x[0], x[1].lower()))
        else:
            dir.sort(key=lambda x: x[sorted_by].lower())
        dir.insert(0, list_entry(Directory='DIR', Name='..'))
    
    # eelmise kausta uuendamine
    last_dir = current_dir
    last_prefix = path_prefix
    
    # colorama värvid
    selected = Fore.BLACK + Back.WHITE
    reset = Fore.RESET + Back.RESET
    edit = Fore.RESET + Back.YELLOW
    
    # ekraanil nähtavad read
    if colors:
        for i in range(view_position, min(view_position + view_lines, len(dir))):
            if cursor_line == i: print(selected, end='')
            for col in columns_visible:
                print(((('> ' + edit if editing else '> ') if cursor_line == i else '  ') if columns_visible[cursor_column] == col else '') +
                      (dir[i][col] if len(dir[i][col]) < column_sizes[col] + 1 else dir[i][col][:column_sizes[col]-3]) +
                      ('... ' if len(dir[i][col]) > column_sizes[col] else '' ) +
                      ((selected if cursor_line == i else reset) if editing and cursor_line == i and columns_visible[cursor_column] == col else '') + # värvimuutus tagasi
                      ' '*(column_sizes[col] - len(dir[i][col]) + 1), end='')
            print(reset)
    else:
        for i in range(view_position, min(view_position + view_lines, len(dir))):
            #if cursor_line == i: print('\33[7m', end='')
            for col in columns_visible:
                print(((('> ' if editing else '> ') if cursor_line == i else '  ') if columns_visible[cursor_column] == col else '') +
                      (dir[i][col] if len(dir[i][col]) < column_sizes[col] + 1 else dir[i][col][:column_sizes[col]-3]) +
                      ('... ' if len(dir[i][col]) > column_sizes[col] else '' ) +
                      (('' if cursor_line == i else '') if editing and cursor_line == i and columns_visible[cursor_column] == col else '') + # värvimuutus tagasi
                      ' '*(column_sizes[col] - len(dir[i][col]) + 1), end='')
            print('')
    
    # sisend
    ch = getch()
    # windowsis kui kasutaja vajutab ebatavalisi klahve siis getch() tagastab märgi b'\xe0' ja
    # järgmine kord kui getch() kutsutakse siis tagastab ebatavalise klahvi märgi
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
            last_prefix = path_prefix
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
        elif ch == b'+': # expand
            if columns_visible[cursor_column]+1 not in columns_visible and columns_visible[cursor_column]+1 < len(columns):
                columns_visible.insert(cursor_column+1, columns_visible[cursor_column]+1)
        elif ch == b'-': # hide
            if cursor_column > 1:
                columns_visible.pop(cursor_column)
                if cursor_column >= len(columns_visible):
                    cursor_column = len(columns_visible)-1
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
        #message += 'Col='+str(cursor_column)+'; '+str(columns_visible)+'\n'








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



