#!/bin/bash
#
# Install micropython-ftplib to a MicroPython board

MODULES=('ftplib.py' 'ftplibtls.py' 'ftpupload.py' 'ftpcp.py')

for py in ${MODULES[*]}; do
    echo "Compiling $py to ${py%.*}.mpy"
    ${MPY_CROSS:-mpy-cross} "$py"
    ${RSHELL:-rshell} --quiet \
        -b ${BAUD:-9600} \
        -p ${PORT:-/dev/ttyACM0} \
        cp "${py%.*}".mpy "${DESTDIR:-/pyboard}"
done
