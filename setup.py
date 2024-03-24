"""setup file for pyle_manager"""

from setuptools import setup

from mypyc.build import mypycify

setup(
    name="pyle_manager",
    author="Tommaso Seneci",
    url="https://github.com/ttoommxx/pyleManager",
    license="MIT",
    description="Terminal file manager",
    version="2.1",
    install_requires=[
        "mypy",
        "os",
        "time",
        "ctypes",
        "itertools",
        "platform",
        "unicurses",
    ],
    ext_modules=mypycify(["pyle_manager.py"]),
    python_requires=">=3.10",
)


# import argparse

# import unicurses as uc  # type: ignore
