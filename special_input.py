from getch import getch, getwch # 1 täht korraga lugemine
from colorama import init, Fore, Back, Style
        
import os, sys
if os.name == 'nt':
    import msvcrt
    import ctypes
    import win32api

    class _CursorInfo(ctypes.Structure):
        _fields_ = [("size", ctypes.c_int),
                    ("visible", ctypes.c_byte)]

def hide_cursor():
    if os.name == 'nt':
        ci = _CursorInfo()
        handle = ctypes.windll.kernel32.GetStdHandle(-11)
        ctypes.windll.kernel32.GetConsoleCursorInfo(handle, ctypes.byref(ci))
        ci.visible = False
        ctypes.windll.kernel32.SetConsoleCursorInfo(handle, ctypes.byref(ci))
    elif os.name == 'posix':
        sys.stdout.write("\033[?25l")
        sys.stdout.flush()

def show_cursor():
    if os.name == 'nt':
        ci = _CursorInfo()
        handle = ctypes.windll.kernel32.GetStdHandle(-11)
        ctypes.windll.kernel32.GetConsoleCursorInfo(handle, ctypes.byref(ci))
        ci.visible = True
        ctypes.windll.kernel32.SetConsoleCursorInfo(handle, ctypes.byref(ci))
    elif os.name == 'posix':
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()

def getShiftDown():
    if os.name == 'nt':
        return win32api.GetAsyncKeyState(0x10)
    return False


init()

# colorama värvid
color_select = Fore.BLACK + Back.WHITE + Style.NORMAL
color_reset = Fore.RESET + Back.RESET + Style.RESET_ALL
color_guess = Fore.YELLOW + Back.RESET + Style.DIM
color_cursor = Fore.RESET + Back.RESET + Style.BRIGHT

# eraldi sisendi funktsioon 
# info - informatiivne tekst rea alguses
# prefill - tekst, mis on alguses sisestatud
# options - valik, mida pakutakse kasutajale
# limit - maksimaalne sisestatava teksti pikkus
# tagastab sisestatud sõne nagu input()
def special_input(info = '', prefill = '', options = [], limit = 100):
    hide_cursor()
    undo = []
    redo = []
    clipboard = ''
    buffer = prefill
    options_pos = 0
    last_len = 0
    cursor = len(buffer)
    selection = [0, len(buffer)]
    guess = False
    
    while True:
        print('\r'+' '*last_len+'\r'+info, end='')
        last_len = len(info)
        if selection:
            print(buffer[:max(selection[0], 0)] +
                  color_select + buffer[max(selection[0], 0):min(selection[1], len(buffer))] +
                  color_reset + buffer[min(selection[1], len(buffer)):], end='')
        else:
            print(buffer[:cursor] + color_cursor + (buffer[cursor] + color_reset + buffer[cursor+1:] if cursor < len(buffer) else ('_' if not guess else '') + color_reset), end='')
        last_len += len(buffer)
        if guess:
            last_len += len(guess)
            print(color_guess + guess + color_reset , end='')
        
        last_len += 1
        #dbgch = ''
        
        # sisend
        ch = getwch()
        # windowsis kui kasutaja vajutab ebatavalisi klahve siis getch() tagastab märgi b'\xe0' ja
        # järgmine kord kui getch() kutsutakse siis tagastab ebatavalise klahvi märgi
        special_ch = ch.encode() == b'\xc3\xa0'
        if special_ch:
            #dbgch += str(ch.encode()) + ' '
            ch = getwch()
        if ch:
            #dbgch += str(ch.encode())
            #print('        ch='+dbgch, end='')
            if special_ch and ch == 'H': # nool üles
                #if options_pos < 0: options_pos = len(options)-1
                for i in range(options_pos-1, -1, -1):
                    if i == 0: options_pos = len(options)-1
                    if options[i].lower().startswith(buffer.lower()):
                        guess = options[i][len(buffer):]
                        options_pos = i
                        break
            elif special_ch and ch == 'P': # nool alla
                #if options_pos >= len(options): options_pos = 0
                for i in range(options_pos+1, len(options)):
                    if i == len(options)-1: options_pos = 0
                    if options[i].lower().startswith(buffer.lower()):
                        guess = options[i][len(buffer):]
                        options_pos = i
                        break
            elif special_ch and ch == 'M': # nool paremale
                # liigu paremale
                if cursor < len(buffer):
                    cursor += 1
                if getShiftDown():
                    if selection:
                        i = 0 if abs(selection[0] - cursor+1) <= abs(selection[1] - cursor+1) else 1
                        if selection[int(not i)] == cursor:
                            selection = False
                        else:
                            selection[i] = cursor
                    else:
                        selection = [cursor-1, cursor]
                else:
                    # valiku/märgistuse tühistamine
                    selection = False
                    # pakkumise täitmine
                    if guess:
                        for i in options:
                            if i.lower() == buffer+guess.lower():
                                buffer = i
                        cursor = len(buffer)
                        guess = False
                    # järgmise pakkumise leidmine
                    else:
                        for i in range(options_pos+1, len(options)):
                            if i == len(options)-1: options_pos = 0
                            if options[i].lower().startswith(buffer.lower()):
                                guess = options[i][len(buffer):]
                                options_pos = i
                                break
                
            elif special_ch and ch == 'K': # nool vasakule
                # liigu vasakule
                if cursor > 0:
                    cursor -= 1
                if getShiftDown():
                    if selection:
                        i = 0 if abs(selection[0] - cursor-1) < abs(selection[1] - cursor-1) else 1
                        if selection[int(not i)] == cursor:
                            selection = False
                        else:
                            selection[i] = cursor
                    else:
                        selection = [cursor, cursor+1]
                else:
                    # valiku/märgistuse tühistamine
                    selection = False
            elif ch == '\x1b': # esc, tühista muutmine, tagasta algne väärtus
                # pakkumise tühistamine
                if guess: guess = False
                else:
                    print()
                    show_cursor()
                    return prefill
            elif ch == '\x08': # backspace
                # pakkumise tühistamine
                if guess: guess = False
                # valiku/märgistuse tühistamine
                if selection and selection[0] < selection[1]:
                    cursor = max(selection[0], 0)
                    buffer = buffer[:max(0, selection[0])] + buffer[min(len(buffer), selection[1]):]
                    selection = False
                # 1 täht korraga kustutamine
                if cursor > 0:
                    buffer = buffer[:cursor-1] + buffer[cursor:]
                    cursor -= 1
            elif special_ch and ch == 'S': # delete
                # pakkumise tühistamine
                guess = False
                # valiku/märgistuse kustutamine
                if selection and selection[0] < selection[1]:
                    cursor = max(selection[0], 0)
                    buffer = buffer[:max(0, selection[0])] + buffer[min(len(buffer), selection[1]):]
                    selection = False
                # 1 täht korraga kustutamine
                if cursor < len(buffer):
                    buffer = buffer[:cursor] + buffer[cursor+1:]
            # enter
            elif ch == '\r':
                print()
                show_cursor()
                if guess:
                    for i in options:
                        if i.lower() == buffer+guess.lower():
                            buffer = i
                return buffer
            # home
            elif special_ch and ch == 'G':
                if getShiftDown():
                    if selection:
                        i = 0 if abs(selection[0] - cursor) < abs(selection[1] - cursor) else 1
                        if i:
                            selection[1] = selection[0]
                        selection[0] = 0
                    else:
                        selection = [0, cursor]
                    if selection[0] == selection[1]:
                        selection = False
                else:
                    # valiku/märgistuse tühistamine
                    selection = False
                cursor = 0
            # end
            elif special_ch and ch == 'O':
                if getShiftDown():
                    if selection:
                        i = 0 if abs(selection[0] - cursor) <= abs(selection[1] - cursor) else 1
                        if not i:
                            selection[0] = selection[1]
                        selection[1] = len(buffer)
                    else:
                        selection = [cursor, len(buffer)]
                    if selection[0] == selection[1]:
                        selection = False
                else:
                    # valiku/märgistuse tühistamine
                    selection = False
                cursor = len(buffer)
            # Ctrl+A
            elif ch == '\x01':
                selection = [0, len(buffer)]
            # tab - valib järgmise pakkumise
            elif ch == '\t':
                if options_pos >= len(options): options_pos = 0
                for i in range(options_pos+1, len(options)):
                    if i == len(options)-1: options_pos = 0
                    if options[i].lower().startswith(buffer.lower()):
                        guess = options[i][len(buffer):]
                        options_pos = i
                        break
            else:
                if not special_ch and len(buffer) < limit:
                    if selection:
                        buffer = buffer[:selection[0]] + buffer[selection[1]:]
                        selection = False
                    buffer = buffer[:cursor] + ch + buffer[cursor:]
                    cursor += 1
                    
                    guess = False
                    for i in range(options_pos, len(options)):
                        if i == len(options)-1: options_pos = 0
                        if options[i].lower().startswith(buffer.lower()):
                            guess = options[i][len(buffer):]
                            options_pos = i
                            break
                
            
        
#print('returns: ' + special_input('test in: ', 'fill', ['car', 'Tere Tulemast', 'tervis', 'test', 'testers', 'paper', 'm-skill']))
#input()
