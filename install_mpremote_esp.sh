#!/bin/bash
#
# Install the ESP2866 variant of micropython-ftplib to a MicroPython board
# using the mpremote tool

MODULES=('esp/ftplib.py' 'esp/ftplibtls.py' 'esp/ftpadvanced.py' 'ftpupload.py' 'ftpcp.py')
BUILDDIR="build/esp"
DESTDIR="${DESTDIR:-:/lib}"

mkdir -p "$BUILDDIR"
# Create the installation directory
# Will generate errors in the output if it already exists
#
# Traceback (most recent call last):
#   File "<stdin>", line 2, in <module>
# OSError: [Errno 17] EEXIST
mpremote ${PORT:+connect $PORT} mkdir "$DESTDIR"

for py in ${MODULES[*]}; do
    bn="${py##*/}"
    mpy="${bn%.*}.mpy"
    echo "Compiling $py to $BUILDDIR/$mpy"
    ${MPY_CROSS:-mpy-cross} -o "$BUILDDIR/$mpy" "$py"
    ${MPREMOTE:-mpremote} ${PORT:+connect $PORT} cp "$BUILDDIR/$mpy" "$DESTDIR/$mpy"
done

