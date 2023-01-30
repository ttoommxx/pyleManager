import os
from pynput.keyboard import Key, Listener, KeyCode
import time

local_folder = os.path.abspath(os.getcwd()) + '/'
index = 0

def main():
    print('Select a file')

if __name__ == "__main__":
    main()

def dir_printer():
    global index
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')
    print('INSTRUCTIONS: (leftArrow = previous folder), (rightArrow = open folder\select file), (upArrow = up), (downArrow = down), (q = quit), (* are folders)\n')
    
    print(os.path.abspath(os.getcwd()) + '/' + '\nBACK')
    
    if len(os.listdir()) == 0:
        print('**EMPTY FOLDER**')
    for x in os.listdir():
        if os.listdir().index(x) == index:
            print('->', end='')
        else:
            print('  ', end='')
        if os.path.isdir(os.path.abspath(os.getcwd()) + '/' + x):
            print('*', end='')
        else:
            print(' ', end='')
        print(x)

def on_press(key):
    global index
    if len(os.listdir()) != 0:
        match key:
            case Key.up:
                index = (index - 1) % len(os.listdir())
            case Key.down:
                index = (index + 1) % len(os.listdir())
            case Key.right:
                selection = os.path.abspath(os.getcwd()) + '/' + os.listdir()[index]
                if os.path.isdir(selection):
                    os.chdir(selection)
                elif os.path.isfile(selection):
                    open(local_folder + 'temp','w').write(selection)
                    return False
                index = 0
            case Key.left:
                index = 0
                os.chdir('..')
            case _:
                try:
                    if key.char == ('q'):
                        return False
                except:
                    pass
    else:
        if key == Key.left:
            index = 0
            os.chdir('..')
    dir_printer()

with Listener(on_press=on_press, suppress=True) as listener:
    listener.join()
