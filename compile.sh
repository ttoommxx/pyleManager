#!/bin/bash


installed_packages=$(pip list)

if echo "$installed_packages" | grep "Uni-Curses"; then
    if echo "$installed_packages" | grep "mypy"; then
        mypy pyle_manager.py
        python3 setup.py build_ext --inplace
    else
        echo "Error: mypyc is not installed via pip, run pip install mypy"
    fi
else
    echo "Error: unicurses is not installed via pip, run pip install uni-curses"
    exit 1
fi
