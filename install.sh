#!/bin/bash
#
# Install micropython-ftplib to a MicroPython board using the rshell tool

MODULES=('ftplib.py' 'ftplibtls.py' 'ftpupload.py' 'ftpcp.py')
BUILDDIR="build"
DESTDIR="${DESTDIR:-/pyboard/lib}"
RSHELL_CMD="${RSHELL:-rshell} --quiet -b ${BAUD:-9600} -p ${PORT:-/dev/ttyACM0}"

mkdir -p "$BUILDDIR"
# Create the installation directory
# Will generate errors in the output if it already exists
$RSHELL_CMD mkdir "$DESTDIR"

for py in ${MODULES[*]}; do
    mpy="${py%.*}.mpy"
    echo "Compiling $py to $BUILDDIR/$mpy"
    ${MPY_CROSS:-mpy-cross} -o "$BUILDDIR/$mpy" "$py"
    $RSHELL_CMD cp "$BUILDDIR/$mpy" "$DESTDIR"
done

