# micropython-ftplib

An FTP client library for MicroPython.

This is an adaption of the [ftplib] module from the CPython standard library to
MicroPython. Apart from making it compatible with the `socket` module
implementation of MicroPython and removing the use of the `re` library, some
parts of the original library have been removed and the code and docstrings
have been cleaned up somewhat.

The `FTP_TLS` class has been moved to a separate module file (`ftplibtls.py`)
and the `all_errors` module global variable has been removed. The test code has
been moved to a separate script and reworked too. The `ftpcp` function has been
moved to the `ftpcp.py` module file.

The code has been tested only under the *unix*, *esp8266* and *esp32* ports of
MicroPython and against the FTP server from the [pyftpdlib] package.

For the *esp8266* port the code needed to be slighty altered to make it work
with the `ssl` module there and to reduce the memory usage. This version can
be found in the [esp](./esp) directory. See the file `README.md` in that
directory for esp8266-specific instructions. This version also works with the
*esp32* port.


[ftplib]: https://docs.python.org/3/library/ftplib.html
[pyftpdlib]: https://github.com/giampaolo/pyftpdlib/
