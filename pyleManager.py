import os, sys, time, argparse
from platform import system
from itertools import chain

if os.name == "nt":
    from msvcrt import getch
elif os.name == "posix":
    import termios, tty
else:
    sys.exit("Operating system not recognised")

parser = argparse.ArgumentParser(prog="pyleManager", description="file manager written in Python")
parser.add_argument("-p", "--picker", action="store_true", help="use pyleManager as a file selector")
args = parser.parse_args() # args.picker contains the modality
picker = args.picker


local_folder = f"{os.path.abspath(os.getcwd())}/" # save original path
index = 0 # dummy index
dimension = False 
time_modified = False
hidden = False
order = 0
current_directory = None
from_file = 0
rows_len = 0

# RETURN FILE SIZE AS A STRING
def file_size(path):
    size = os.lstat(path).st_size
    i = len(str(size)) // 3
    if len(str(size)) % 3 == 0:
        i -= 1
    if i > 3:
        i = 3
    size /= 1000**i
    return f'{size:.2f}{("b","kb","mb","gb")[i]}'


# UPDATE ORDER, 0 stay 1 next
def order_update(j):
    global order, current_directory
    vec = (1, int(dimension)*(True in (os.path.isfile(x) for x in directory())),
            int(time_modified)*(True in (os.path.isfile(x) for x in directory())))
    order = vec.index(1,order+j) if 1 in vec[order+j:] else 0
    current_directory = None
    

# LIST OF FOLDERS AND FILES
def directory():
    global current_directory
    # return the previous value if exists
    if current_directory is None:
        # order by
        match order:
            # size
            case 1:
                dirs = list( chain( (x[0] for x in sorted({x:os.lstat(x).st_size for x in os.listdir() if os.path.isdir(x) and (hidden or not x.startswith(".") )}.items(), key=lambda x:x[1])), \
                                    ( x[0] for x in sorted({x:os.lstat(x).st_size for x in os.listdir() if os.path.isfile(x) and (hidden or not x.startswith(".") )}.items(), key=lambda x:x[1])) ) )
            # time modified
            case 2:
                dirs = list(chain( (x[0] for x in sorted({x:os.lstat(x).st_mtime for x in os.listdir() if os.path.isdir(x) and (hidden or not x.startswith(".") )}.items(), key=lambda x:x[1])), \
                                    (x[0] for x in sorted({x:os.lstat(x).st_mtime for x in os.listdir() if os.path.isfile(x) and (hidden or not x.startswith(".") )}.items(), key=lambda x:x[1])) ) )
            # name
            case _: # 0 and unrecognised values
                dirs = list( chain( sorted( (x for x in os.listdir() if os.path.isdir(x) and (hidden or not x.startswith(".") ) ), key=lambda s: s.lower()),\
                                    sorted((x for x in os.listdir() if os.path.isfile(x) and (hidden or not x.startswith(".") )), key=lambda s: s.lower()) ) )
        current_directory = dirs
    return current_directory


# CLEAN TERMINAL
def clear():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")

# INSTRUCTION PRINTER
def instructions():
    clear()
    print(f"""INSTRUCTIONS:

    prefix < means folder

    leftArrow = previous folder
    rightArrow = open folder
    upArrow = up
    downArrow = down
    q = quit
    h = toggle hidden files
    d = toggle file size
    t = toggle time last modified
    m = change ordering
    enter = {
        'select file' if picker else 'open using the default application launcher'}
    e = {'--disabled--' if picker else 'edit using command-line editor'}

press any button to continue""", end="")


# PRINTING FUNCTION
def dir_printer(position = True):
    global rows_len
    clear()
    # path directory
    to_print = ["### pyleManager --- press i for instructions ###\n"]
    columns_len = os.get_terminal_size().columns # length of terminal columns
    rows_len = os.get_terminal_size().lines  # length of terminal rows
    # name folder
    to_print.append( f"{'... ' if  len(os.path.abspath(os.getcwd())) > columns_len else ''}{os.path.abspath(os.getcwd())[-columns_len+5:]}/\n" )
    # folders and pointer
    if len(directory()) == 0:
        to_print.append( " **EMPTY FOLDER**" )
    else:
        order_update(0)
        l_size = max((len(file_size(x)) for x in directory()))
    
        to_print.append( f" {'v' if order == 0 else ' '}*NAME*" )
        columns = ""
        if dimension and True in (os.path.isfile(x) for x in directory()):
            columns += f" |{'v' if order == 1 else ' '}*SIZE*{' '*(l_size-6)}"
        if time_modified and True in (os.path.isfile(x) for x in directory()):
            columns += f" |{'v' if order == 2 else ' '}*TIME_M*{' '*11}"

        to_print.append( f"{' '*(columns_len - len(columns)-8)}{columns}" )

        for x in directory()[from_file: from_file + rows_len - 3]:
            to_print.append( f"\n {'<' if os.path.isdir(x) else ' '}" )
            columns = ""
            if dimension and os.path.isfile(x):
                columns += f" | {file_size(x)}{' '*(l_size - len(file_size(x)))}"
            if time_modified and os.path.isfile(x):
                columns += f" | {time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(time.ctime(os.lstat(x).st_mtime)))}"
            name_x = f"{f'... {x[-(columns_len - 6 - len(columns)):]}' if len(x) > columns_len - 2 - len(columns) else x}"
            to_print.append( f"{name_x}{' '*(columns_len-len(name_x)-len(columns) - 2)}{columns}" )
    print("".join(to_print), end = "\r")
    if position:
        sys.stdout.write(f'\033[{ min(len(directory()), rows_len-3)  }A')
        print()
    

# FETCH KEYBOARD INPUT
if os.name == "posix":
    def getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch
    conv_arrows = {"D":"left", "C":"right", "A":"up", "B":"down"}
    def get_key():
        key_pressed = getch()
        match key_pressed:
            case "\r":
                return "enter"
            case "\x1b":
                if getch() == "[":
                    return conv_arrows[getch()]
            case _:
                return key_pressed
else:
    conv_table = {
        b"q":"q", b"h":"h", b"m":"m", b"i":"i", b"t":"t", b"d":"d", b"e":"e", b"\r":"enter",
        b"\xe0":"arrows"
        }
    conv_arrows = {b"K":"left", b"M":"right", b"H":"up", b"P":"down"}
    def get_key():
        key_pressed = conv_table[getch()]
        if key_pressed != "arrows":
            return key_pressed
        else:
            return conv_arrows[getch()]
        


# FILE MANAGER
def main(*args):
    global index, dimension, time_modified, picker, from_file, current_directory
    
    if args and args[0] in ["-p", "--picker"]:
        picker = True
    
    dir_printer()
    while True:
        if len(directory()) > 0:
            selection = directory()[index] # + file name if any
        match get_key():
            # quit
            case "q":
                clear()
                os.chdir(local_folder)
                return
            # toggle hidden
            case "h":
                hidden = not hidden
                current_directory = None
                from_file = 0
                index = 0
                dir_printer()
            # change order
            case "m":
                order_update(1)
                from_file = 0
                index = 0
                dir_printer()
            # instructions
            case "i":
                instructions()
                getch()
                from_file = 0
                index = 0
                dir_printer()
            case "t":
                time_modified = not time_modified
                from_file = 0
                index = 0
                dir_printer()
            # size
            case "d":
                dimension = not dimension
                from_file = 0
                index = 0
                dir_printer()
            # command-line editor
            case "e" if len(directory()) > 0 and not picker:
                selection = selection.replace("\"", "\\\"")
                match system():
                    case "Linux":
                        os.system(f"$EDITOR \"{selection}\"")
                    case "Windows":
                        clear()
                        print("Windows does not have any built-in command line editor, press any button to continue")
                        getch()
                    case "Darwin":
                        os.system(f"open -e \"{selection}\"")
                    case _:
                        clear()
                        print("system not recognised, press any button to continue")
                        getch()
            # enter
            case "enter" if len(directory()) > 0:
                if picker:
                    path = f"{os.getcwd()}/{selection}{'/' if  os.path.isdir(selection) else ''}"
                    os.chdir(local_folder)
                    return path
                elif not picker:
                    selection = selection.replace("\"", "\\\"")
                    match system():
                        case "Linux":
                            os.system(f"xdg-open \"{selection}\"")
                        case "Windows":
                            os.system(selection)
                        case "Darwin":
                            os.system(f"open \"{selection}\"")
                        case _:
                            clear()
                            print("system not recognised, press any button to continue")
                            getch()
            # up
            case "up" if len(directory()) > 0:
                if index > 0:
                    index -= 1
                    if index >= from_file:
                        sys.stdout.write('\033[2A')
                        print()
                    else:
                        from_file -= 1
                        dir_printer("beginning")
            # down
            case "down" if len(directory()) > 0:
                if index < len(directory())-1:
                    index += 1
                    if index < rows_len - 3:
                        print()
                    else:
                        from_file += 1
                        dir_printer(False)
            # right
            case "right" if len(directory()) > 0:
                if os.path.isdir(selection):
                    os.chdir(selection)
                    current_directory = None
                    from_file = 0
                    index = 0
                    dir_printer()
            # left
            case "left":
                os.chdir("..")
                current_directory = None
                from_file = 0
                index = 0
                dir_printer()
            case _:
                pass

        
if __name__ == "__main__":
    main()
    sys.exit(0)