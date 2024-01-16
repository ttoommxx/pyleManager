# REQUIRED MODULES
import os
import sys
import time
import argparse
import itertools
from platform import system

if os.name == "posix":
    import termios
    import tty
elif os.name == "nt":
    from msvcrt import getch as getch_encoded
else:
    sys.exit("Operating system not recognised")


# ARGUMENT PARSER
parser = argparse.ArgumentParser(prog="pyleManager",
                                 description="file manager written in Python")
parser.add_argument("-p", "--picker",
                    action="store_true",
                    help="use pyleManager as a file selector")
args = parser.parse_args() # args.picker contains the modality
picker = args.picker


# GLOBAL VARIABLES
LOCAL_FOLDER = os.path.abspath(os.getcwd()) # save original path
DIMENSION = False
TIME_MODIFIED = False
HIDDEN = False
BEEP = False
PERMISSION = False
INDEX = 0
ORDER = 0
CURRENT_DIRECTORY = None
START_LINE_DIRECTORY = 0
ROWS_LENGTH = os.get_terminal_size().lines
SELECTION = None


def file_size(path: str) -> str:
    """ return file size as a formatted string """
    size = os.lstat(path).st_size
    i = len(str(size)) // 3
    if len(str(size)) % 3 == 0:
        i -= 1
    if i > 3:
        i = 3
    size /= 1000**i
    return f'{size:.2f}{("b","kb","mb","gb")[i]}'


def order_update(stay: bool) -> None:
    """ update order, False stay, True move to the next entry """
    global ORDER
    old_order = ORDER
    # create a vector with (1,a,b) where a,b are one if dimension and TIME_MODIFIED are enabled
    vec = (1,
           DIMENSION * any(os.path.isfile(x) for x in directory()),
           TIME_MODIFIED * any(os.path.isfile(x) for x in directory())
           )
    # search the next 1 and if not found return 0
    ORDER = vec.index(1, ORDER+stay) if 1 in vec[ORDER+stay:] else 0
    if ORDER != old_order:
        # only update if the previous order was changed
        global CURRENT_DIRECTORY
        CURRENT_DIRECTORY = None
    

def directory() -> list[str]:
    """ list of folders and files """
    # return the previous value if exists
    global CURRENT_DIRECTORY
    if CURRENT_DIRECTORY is None:
        directories = os.listdir()
        # order by
        match ORDER:
            # size
            case 1:
                dirs = list( itertools.chain( (x[0] for x in sorted({x:os.lstat(x).st_size for x in directories
                                                                     if os.path.isdir(x) and (HIDDEN or not x.startswith("."))}.items(), key=lambda x: x[1])),
                                    (x[0] for x in sorted({x: os.lstat(x).st_size for x in directories
                                                           if os.path.isfile(x) and (HIDDEN or not x.startswith("."))}.items(), key=lambda x: x[1]))))
            # time modified
            case 2:
                dirs = list( itertools.chain( (x[0] for x in sorted({x:os.lstat(x).st_mtime for x in directories
                                                                     if os.path.isdir(x) and (HIDDEN or not x.startswith("."))}.items(), key=lambda x: x[1])),
                                    (x[0] for x in sorted({x: os.lstat(x).st_mtime for x in directories
                                                           if os.path.isfile(x) and (HIDDEN or not x.startswith("."))}.items(), key=lambda x: x[1]))))
            # name
            case _: # 0 and unrecognised values
                dirs = list( itertools.chain( sorted((x for x in directories
                                                      if os.path.isdir(x) and (HIDDEN or not x.startswith("."))), key=lambda s: s.lower()),
                                    sorted((x for x in directories
                                            if os.path.isfile(x) and (HIDDEN or not x.startswith("."))), key=lambda s: s.lower())))
        CURRENT_DIRECTORY = dirs
    return CURRENT_DIRECTORY


# CLEAN TERMINAL
if os.name == "posix":
    def clear():
        """ clear screen """
        os.system("clear")
elif os.name == "nt":
    def clear():
        """ clear screen """
        os.system("cls")


def dir_printer(position:str = "beginning") -> None:
    """ printing function """
    global START_LINE_DIRECTORY
    global INDEX

    # first check if I only have to print the index:
    if position == "up":
        INDEX -= 1
        if INDEX >= START_LINE_DIRECTORY:
            # print up when we are in the range of visibility
            sys.stdout.write('\033[2A')
            print()
            return # exit the function
        
        # else print up one
        START_LINE_DIRECTORY -= 1
        position = "beginning" # return the cursor up

    elif position == "down":
        INDEX += 1
        if INDEX < ROWS_LENGTH - 3 + START_LINE_DIRECTORY:
            # print down when we are in the range of visibility
            print()
            return # exit the function
        
        # else print down 1
        START_LINE_DIRECTORY += 1

    clear()
    # length of columns
    columns_len = os.get_terminal_size().columns
    # path directory
    to_print = ["### pyleManager --- press i for instructions ###"[:columns_len], "\n"]
    # name folder
    to_print.append( f"{'... ' if  len(os.path.abspath(os.getcwd())) > columns_len else ''}{os.path.abspath(os.getcwd())[-columns_len+5:]}" )
    if not to_print[-1].endswith(os.sep):
        to_print.append(os.sep)
    to_print.append("\n")
    # folders and pointer
    if len(directory()) == 0:
        to_print.append( " **EMPTY FOLDER**" )
        position = None
    else:
        order_update(0)
        l_size = max((len(file_size(x)) for x in directory()))
    
        # write the description on top
        to_print.append(f" {'v' if ORDER == 0 else ' '}*NAME*")
        columns = ""
        if DIMENSION and any(os.path.isfile(x) for x in directory()):
            columns += f" |{'v' if ORDER == 1 else ' '}*SIZE*{' '*(l_size-6)}"
        if TIME_MODIFIED:
            columns += f" |{'v' if ORDER == 2 else ' '}*TIME MODIFIED*{' '*4}"
        if PERMISSION:
            columns += " | *PERM*"

        to_print.append( f"{' '*(columns_len - len(columns)-8)}{columns}" )

        if position == "index":
            INDEX = min(INDEX, len(directory())-1)
            if INDEX < ROWS_LENGTH - 3:
                pass
            else:
                START_LINE_DIRECTORY = INDEX - (ROWS_LENGTH - 3) + 1

        for x in itertools.islice(directory(), START_LINE_DIRECTORY, START_LINE_DIRECTORY + ROWS_LENGTH - 3):
            to_print.append( f"\n {'<' if os.path.isdir(x) else ' '}" )

            # add extensions
            columns = ""
            if DIMENSION and os.path.isfile(x):
                columns += f" | {file_size(x)}{' '*(l_size - len(file_size(x)))}"
            if TIME_MODIFIED:
                columns += f" | {time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(time.ctime(os.lstat(x).st_mtime)))}"
            if PERMISSION:
                read_x = os.access(x, os.R_OK)
                write_x = os.access(x, os.W_OK)
                execute_x = os.access(x, os.X_OK)
                columns += f" | {'r' if read_x else '-'} {'w' if write_x else '-'} {'x' if execute_x else '-'} "
                
            name_x = f"{f'... {x[-(columns_len - 6 - len(columns)):]}' if len(x) > columns_len - 2 - len(columns) else x}"
            to_print.append( f"{name_x}{' '*(columns_len-len(name_x)-len(columns) - 2)}{columns}" )

    print("".join(to_print), end = "\r")

    if position == "beginning":
        sys.stdout.write(f'\033[{ min(len(directory()), ROWS_LENGTH-3)  }A')
        print()
    elif position == "index":
        if INDEX < ROWS_LENGTH - 3:
            sys.stdout.write(
                f'\033[{min(len(directory()), ROWS_LENGTH-3) - INDEX}A')
            print()


# FETCH KEYBOARD INPUT
if os.name == "posix":
    def getch() -> str:
        """ read raw terminal input """
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch
    
    conv_arrows = {"D":"left", "C":"right", "A":"up", "B":"down"}
    def get_key() -> str:
        """ process correct string for keyboard input """
        key_pressed = getch()
        match key_pressed:
            case "\r":
                return "enter"
            case "\x1b":
                if getch() == "[":
                    return conv_arrows.get(getch(), None)
            case _:
                return key_pressed
elif os.name == "nt":
    def getch() -> str:
        """ read raw terminal input """
        letter = getch_encoded()
        try:
            return letter.decode('ascii')
        except:
            return letter
    
    conv_arrows = {"K":"left", "M":"right", "H":"up", "P":"down"}
    def get_key() -> str:
        """ process correct string for keyboard input """
        key_pressed = getch()
        match key_pressed:
            case "\r":
                return "enter"
            case b"\xe0":
                return conv_arrows.get(getch(), None)
            case _:
                return key_pressed


def beeper() -> None:
    """ make a beep """
    if BEEP:
        sys.stdout.write('\033[2A')
        print("\a\n")


def dir_printer_reset(refresh:bool = False, restore_position:str = "beginning") -> None:
    """ print screen after resetting directory attributes """
    global START_LINE_DIRECTORY
    global INDEX
    global ROWS_LENGTH
    if refresh:
        global CURRENT_DIRECTORY
        CURRENT_DIRECTORY = None

    ROWS_LENGTH = os.get_terminal_size().lines
    START_LINE_DIRECTORY = 0
    if restore_position == "index":
        pass
    elif restore_position == "selection":
        if SELECTION in directory():
            INDEX = directory().index(SELECTION)
        else:
            INDEX = 0
        restore_position = "index"
    else:
        INDEX = 0
    
    dir_printer(position = restore_position)


def instructions() -> None:
    """ print instructions """
    clear()
    print( f"""INSTRUCTIONS:

the prefix \"<\" means folder

upArrow = up
downArrow = down
rightArrow = open folder
leftArrow = previous folder
q = quit
r = refresh
h = ({'yes' if HIDDEN else 'no'}) toggle hidden files
d = ({'yes' if DIMENSION else 'no'}) toggle file size
t = ({'yes' if TIME_MODIFIED else 'no'}) toggle time last modified
b = ({'yes' if BEEP else 'no'}) toggle beep
p = ({'yes' if PERMISSION else 'no'}) toggle permission
m = ({("NAME", "SIZE", "TIME MODIFIED")[ORDER]}) change ordering
enter = {
        'select file' if picker else 'open using the default application launcher'}
e = {'--disabled--' if picker else 'edit using command-line editor'}

def selection_permission(path):

press any button to continue""", end = "")
    get_key()


def main(*args: list[str]) -> None:
    """ file manager """
    global INDEX
    global DIMENSION
    global TIME_MODIFIED
    global START_LINE_DIRECTORY
    global HIDDEN
    global ROWS_LENGTH
    global BEEP
    global PERMISSION
    global SELECTION
    
    if args and args[0] in ("-p", "--picker"):
        global picker
        picker = True

    dir_printer()

    while True:
        
        if len(directory()) > 0:
            SELECTION = directory()[INDEX]  # + file name if any

        match get_key():
            # up
            case "up":
                if len(directory()) > 0 and INDEX > 0:
                    dir_printer(position = "up")
                else:
                    beeper()

            # down
            case "down":
                if len(directory()) > 0 and INDEX < len(directory())-1:
                    dir_printer(position = "down")
                else:
                    beeper()

            # right
            case "right":
                if len(directory()) > 0 and os.path.isdir(SELECTION) and os.access(SELECTION, os.R_OK):
                    os.chdir(SELECTION)
                    dir_printer_reset(refresh=True, restore_position = "index")
                else:
                    beeper()

            # left
            case "left":
                if os.path.dirname(os.getcwd()) != os.getcwd():
                    os.chdir("..")
                    dir_printer_reset(refresh=True, restore_position = "index")
                else:
                    beeper()

            # quit
            case "q":
                clear()
                os.chdir(LOCAL_FOLDER)
                return

            # refresh
            case "r":
                dir_printer_reset(refresh = True, restore_position = "selection")

            # toggle hidden
            case "h":
                HIDDEN = not HIDDEN
                dir_printer_reset(refresh=True, restore_position="selection")

            # size
            case "d":
                DIMENSION = not DIMENSION
                dir_printer_reset(restore_position="selection")

            # time
            case "t":
                TIME_MODIFIED = not TIME_MODIFIED
                dir_printer_reset(restore_position="selection")

            # beep
            case "b":
                BEEP = not BEEP

            # permission
            case "p":
                PERMISSION = not PERMISSION
                dir_printer_reset(restore_position="selection")

            # change order
            case "m":
                order_update(1)
                dir_printer_reset(restore_position="selection")

            # enter
            case "enter":
                if len(directory()) > 0:
                    if picker:
                        path = os.path.join(os.getcwd(), SELECTION)
                        clear()
                        os.chdir(LOCAL_FOLDER)
                        return path
                    elif not picker:
                        selection_os = SELECTION.replace("\"", "\\\"")
                        match system():
                            case "Linux":
                                os.system(f"xdg-open \"{selection_os}\"")
                            case "Windows":
                                os.system(selection_os)
                            case "Darwin":
                                os.system(f"open \"{selection_os}\"")
                            case _:
                                clear()
                                print("system not recognised, press any button to continue")
                                get_key()
                                dir_printer_reset(restore_position="selection")
                else:
                    beeper()

            # command-line editor
            case "e":
                if len(directory()) > 0 and not picker:
                    selection_os = SELECTION.replace("\"", "\\\"")
                    match system():
                        case "Linux":
                            os.system(f"$EDITOR \"{selection_os}\"")
                        case "Windows":
                            clear()
                            print(
                                "Windows does not have any built-in command line editor, press any button to continue")
                            get_key()
                            dir_printer_reset(restore_position="selection")
                        case "Darwin":
                            os.system(f"open -e \"{selection_os}\"")
                        case _:
                            clear()
                            print(
                                "system not recognised, press any button to continue")
                            get_key()
                            dir_printer_reset(restore_position="selection")
                else:
                    beeper()

            # instructions
            case "i":
                instructions()
                dir_printer_reset(restore_position="selection")

            case _:
                pass


if __name__ == "__main__":
    main()
