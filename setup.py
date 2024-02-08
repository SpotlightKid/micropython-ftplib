"""An FTP client library for MicroPython

This is an adaption of the 'ftplib' module from the CPython standard library to
MicroPython. Apart from making it compatible with the 'socket' module
implementation of MicroPython and removing the use of the 're' library, some
parts of the original library have been removed and the code and docstrings
have been cleaned up somewhat.

The 'FTP_SSL' class has been removed completely and so has the 'all_errors'
module variable. The test code has been moved to a separate script and reworked
too. The 'ftpcp' function has been moved to the 'ftpcp.py' module.

A new FTP-over-TLS implementation has been added based on the present
implementation in the CPython standard library, but has been extensively
reworked as well.

The code has been tested under the following MicroPython ports against the FTP
server from the 'pyftpdlib' package.

* unix
* stm32 (using W5500 ethernet module)
* esp8266
* esp32
* rp2 (Raspberry Pi Pico W)

For the esp8266 port, use the specially adapted modules in the the `esp`
sub-directory.

FTP-over-SSL support for esp32 is may or may not actually work, depending on
the installed MicroPython firmware version and the amount of available RAM on
the board used.

"""

from setuptools import setup

setup(
    name='micropython-ftplib',
    version='0.3.0',
    description=__doc__.splitlines()[0],
    long_description="".join(__doc__.splitlines()[2:]),
    url='https://github.com/SpotlightKid/micropython-ftplib',
    author='Guido van Rossum, et al.',
    maintainer='Christopher Arndt',
    maintainer_email='chris@chrisarndt.de',
    license='Python Software Foundation License',
    py_modules=[
        'ftpcp',
        'ftplib',
        'ftplibtls',
        'ftpuload',
    ]
)
