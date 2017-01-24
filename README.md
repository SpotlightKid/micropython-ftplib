# micropython-ftplib

An FTP client library for MicroPython.

This is an adaption of the 'ftplib' module from the CPython standard library to
MicroPython. Apart from making it compatible with the 'socket' module
implementation of MicroPython and removing the use of the 're' library, some
parts of the original library have been removed and the code and docstrings
have been cleaned up somewhat.

The 'FTP_SSL' class has been removed completely and so has the 'all_errors'
module variable. The test code has been moved to a separate script and reworked
too. The 'ftpcp' function has been moved to the 'ftpcp.py' module.

The code has been tested only under the Unix port of MicroPython so far and
against the FTP server from the 'pyftpdlib' package.
