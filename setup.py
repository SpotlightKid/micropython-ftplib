"""An FTP client library for MicroPython

This is an adaption of the 'ftplib' module from the CPython standard library to
MicroPython. Apart from making it compatible with the 'socket' module
implementation of MicroPython and removing the use of the 're' library, some
parts of the original library have been removed and the code and docstrings
have been cleaned up somewhat.

The 'FTP_SSL' has been removed completely and so has the 'all_errors' module
varisble. The test code has been moved to a separate script and reworked too.
The 'ftpcp' function has been moved to the 'ftpcp.py' module.

The code has been tested only under the Unix port of MicroPython so far and
against the FTP server from the 'pyftpdlib' package.

"""

from setuptools import setup
#import optimize_upip

setup(
    name='micropython-ftplib',
    version='0.1.0',
    description=__doc__.splitlines()[0],
    long_description="".join(__doc__.splitlines()[2:]),
    url='https://github.com/SpotlightKid/micropython-ftplib',
    author='Guido van Rossum, et al.',
    maintainer='Christopher Arndt',
    maintainer_email='chris@chrisarndt.de',
    license='Python Software Foundation License',
    #cmdclass={'optimize_upip': optimize_upip.OptimizeUpip},
    py_modules=['ftplib']
)
