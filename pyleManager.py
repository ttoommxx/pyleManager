import os, sys, termios, tty, time
from platform import system

local_folder = os.path.abspath(os.getcwd()) + '/' # save original path
from settings import *
index = 0 # dummy index
modalities = ['-picker','-manager']

def instructions(mode):
    if mode == '-manager':
        print('''file manager - INSTRUCTIONS:

    leftArrow = previous folder
    rightArrow = open folder
    upArrow = up
    downArrow = down
    q = quit
    h = toggle hidden files
    d = toggle file size
    t = toggle time last modified
    m = toggle order by last modified
    e = edit using command-line editor
    enter = open using the default application launcher

    prefix ■ means folder

press any button to continue''')
    elif mode == '-picker':
        print('''file picker - INSTRUCTIONS:

    leftArrow = previous folder
    rightArrow = open folder
    upArrow = up
    downArrow = down
    h = toggle hidden files
    d = toggle file size
    t = toggle time last modified
    m = toggle order by last modified
    enter = select file
    
    prefix ■ means folder

press any button to continue''')

# RETURN FILE SIZE AS A STRING
def file_size(path):
    size = os.lstat(path).st_size
    i = 0
    while size > 999:
        size = size / 1000
        i = i+1
    metric = ['b','kb','mb','gb']
    return str(round(size,2)) + ' ' + metric[i]

# RETURN MODIFIED TIME
def file_modified_time(path):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.strptime(time.ctime(os.lstat(path).st_mtime)))

# LIST OF FOLDERS AND FILES
def directory():
    dirs = []
    files = []
    if time_order:
        dirs = sorted({x:str(file_modified_time(x)) for x in os.listdir()if os.path.isdir(x) and (hidden or not x.startswith('.') )}.items(), key=lambda x:x[1])
        files = sorted({x:str(file_modified_time(x)) for x in os.listdir() if os.path.isfile(x) and (hidden or not x.startswith('.') )}.items(), key=lambda x:x[1])
        dirs = [dirs[x][0] for x in range(len(dirs))]
        files = [files[x][0] for x in range(len(files))]
    else:
        dirs = sorted([x for x in os.listdir() if os.path.isdir(x) and (hidden or not x.startswith('.') )], key=lambda s: s.lower())
        files = sorted([x for x in os.listdir() if os.path.isfile(x) and (hidden or not x.startswith('.') )], key=lambda s: s.lower())
    return dirs + files

# CLEAN TERMINAL
def clear():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

# INDEX UPDATER
def index_dir():
    global index
    if len(directory()) > 0:
        index = index % len(directory())
    else:
        index = 0

# PRINTING FUNCTION
def dir_printer():
    clear()
    # path directory
    print('press i for instructions\n\n' + os.path.abspath(os.getcwd()) + '/\n')
    # folders and pointer
    if len(directory()) == 0:
        print('**EMPTY FOLDER**')
    else:
        index_dir()
        temp_sel = directory()[index]
        l_file = max([len(x) for x in directory()]) # max length file
        l_size = max([len(file_size(x)) for x in directory()])
        l_time = 19
        max_l = os.get_terminal_size().columns # length of terminal
        print(' ' + '↓'*(time_order == False) + ' '*(time_order == True) + '*NAME*', end='')   
        if dimension and True in [os.path.isfile(x) for x in directory()]:
            print(' '*(max_l - max(l_size,6) - (l_time + 2)*(time_modified == True) - 9) + '*SIZE*', end='')
        if time_modified and True in [os.path.isfile(x) for x in directory()]:
            print(' '*(max(l_size - 3,3)*(dimension == True) + (max_l - 27)*(dimension == False) - 1 - 1*(time_order == True)) + '↓'*(time_order == True) + '*TIME_M*', end='')
        print()
        for x in directory():
            if x == temp_sel:
                print('→', end='')
            else:
                print(' ', end='')
            if os.path.isdir(x):
                print('■', end='')
            else:
                print(' ', end='')
            print(x, end=' ')
            if dimension and os.path.isfile(x):
                print(' '*(max_l - 4 - len(x) - max(l_size,6) - (l_time+2)*(time_modified == True)) + file_size(x), end='')
            if time_modified and os.path.isfile(x):
                print(' '*( (max(l_size,6) - len(file_size(x)) + 2 )*(dimension == True) + (max_l - 23 - len(x))*(dimension == False)) + file_modified_time(x), end='')
            print()

# FETCH KEYBOARD INPUT
def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

# file manager
def main(mode = '-manager'):
    global local_folder
    global index
    global hidden
    global dimension
    global modalities
    global time_modified
    global time_order
    if mode not in modalities:
        input('mode not recognized, selecting manager..\npress enter to continue')
        mode = '-manager'
    dir_printer()
    while True:
        index_dir() # update index
        if len(directory()) > 0:
            selection = directory()[index] # + file name if any
        match getch():
            # quit
            case 'q' if mode == '-manager':
                open(local_folder + 'settings.py','w').write('hidden = ' + str(hidden) + '\ndimension = ' + str(dimension) + '\ntime_modified = ' + str(time_modified) + '\ntime_order = ' + str(time_order)) # save config
                clear()
                os.chdir(local_folder)
                break
            # toggle hidden
            case 'h':
                hidden = not hidden
                if len(directory()) > 0:
                    temp_name = directory()[index]
                    if temp_name in directory(): # update index
                        index = directory().index(temp_name)
                    else:
                        index = 0
            case 'm':
                time_order = not time_order
            # instructions
            case 'i':
                clear()
                instructions(mode)
                getch()
            case 't':
                time_modified = not time_modified
            # size
            case 'd':
                dimension = not dimension
            # command-line editor
            case 'e' if len(directory()) > 0 and mode == '-manager':
                if system() == 'Linux':
                    os.system("$EDITOR " + selection)
            case '\r' if len(directory()) > 0:
                if mode == '-picker' and os.path.isfile(selection):
                    os.chdir(local_folder)
                    return selection
                elif mode == '-manager':
                    if system() == 'Linux':
                        os.system("xdg-open " + selection)
            case '\x1b':
                if getch() == '[':
                    match getch():
                        # up
                        case 'A' if len(directory()) > 0:
                            index = index - 1
                        # down
                        case 'B' if len(directory()) > 0:
                            index = index + 1
                        # right
                        case 'C' if len(directory()) > 0:
                            if os.path.isdir(selection):
                                os.chdir(selection)
                        # left
                        case 'D':
                            os.chdir('..')
                        case _:
                            pass
            case _:
                pass
        dir_printer()

if __name__ == "__main__":
    try:
        main(sys.argv[1])
    except:
        main()
    