import sys
from cx_Freeze import setup, Executable
exe = Executable(
    script=r"run.py",
    base="Win32GUI",
    )

setup(
    name = "TESTApp",
    version = "0.1",
    description = "An example",
    executables = [exe]
    )