#!/bin/sh
#
# miniy ftplib module with pyminifier (https://github.com/liftoff/pyminifier)
#
pyminifier -o ftplib_m.py ftplib.py

# and compile for MicroPython
mpy-cross ftplib.py
mpy-cross esp8266/ftplib.py
