# pylePicker

Very simple file picker (path) written in python.

## requirements

First install the module 'pynput' via
```pip install pynput```
and then run the script through python. After selecting a file, a new file containing the path will be created, named "file_picked".

## compatibility

For the moment, pynput supports X11 and Windows. Linux Wayland won't work, so you can run the script through xterm (Xwayland).

## to do

- add option to open files, for example via xdg-open (see windows for similar), nano etc, or save the path locally