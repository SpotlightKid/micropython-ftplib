#!/bin/bash
#
# Install the ESP2866 variant of micropython-ftplib to a MicroPython board
# using the rshell tool

MODULES=('esp/ftplib.py' 'esp/ftplibtls.py' 'esp/ftpadvanced.py' 'ftpupload.py' 'ftpcp.py')
BUILDDIR="build/esp"
DESTDIR="${DESTDIR:-/pyboard/lib}"
RSHELL_CMD="${RSHELL:-rshell} --quiet -b ${BAUD:-115200} -p ${PORT:-/dev/ttyUSB0}"

mkdir -p "$BUILDDIR"
# Create the installation directory
# Will generate errors in the output if it already exists
$RSHELL_CMD mkdir "$DESTDIR"

for py in ${MODULES[*]}; do
    bn="${py##*/}"
    mpy="${bn%.*}.mpy"
    echo "Compiling $py to $BUILDDIR/$mpy"
    ${MPY_CROSS:-mpy-cross} -o "$BUILDDIR/$mpy" "$py"
    $RSHELL_CMD cp "$BUILDDIR/$mpy" "$DESTDIR"
done

