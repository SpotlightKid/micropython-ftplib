#!/bin/bash
#
# Install micropython-ftplib to a MicroPython board using the mpremote tool

MODULES=('ftplib.py' 'ftplibtls.py' 'ftpupload.py' 'ftpcp.py')
BUILDDIR="build"
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
    mpy="${py%.*}.mpy"
    echo "Compiling $py to $BUILDDIR/$mpy"
    ${MPY_CROSS:-mpy-cross} -o "$BUILDDIR/$mpy" "$py"
    ${MPREMOTE:-mpremote} ${PORT:+connect $PORT} cp "$BUILDDIR/$mpy" "$DESTDIR/$mpy"
done

