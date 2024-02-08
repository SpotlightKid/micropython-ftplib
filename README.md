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

The code has been tested under the following MicroPython ports against the FTP
server from the [pyftpdlib] package.

* unix
* stm32 (using W5500 ethernet module)
* esp8266
* esp32
* rp2 (Raspberry Pi Pico W)

For the *esp8266* port the code needed to be slighty altered to make it work
with the `ssl` module there and to reduce the memory usage. This version can
be found in the [esp](./esp) directory (this version also works with the
*esp32* port, but there you should be able to use the normal version too).


## FTP over TLS

FTP-over-TLS support is available in a separate `ftplibtls` module:

```
>>> from ftplibtls import FTP_TLS
>>> ftp = FTP_TLS('example.com')  # default port 21
>>> ftp.login('username', 'password')
>>> ftp.prot_p()
>>> ftp.retrlines('LIST')
```

Note that you must call the `prot_b` method after connecting and
authentication to actually establish secure communication for data transfers.

If you require server certficate validation (recommended)::

```
>>> from ftplib import FTP_TLS, ssl
>>> ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
>>> ctx.verify_mode = ssl.CERT_REQUIRED
>>> ctx.load_verify_locations(cafile="cert.der")  # Certificate file must be in DER format
>>> ftp = FTP_TLS(ssl_context=ctx, server_hostname="example.com")
>>> ftp.connect('example.com')
>>> ftp.prot_p()
>>> ftp.retrlines('LIST')
```

Use the `server_hostname` constructor argument if the common name in the
server's certificate differs from the host name used for connecting.

Note: the version of `ftplibtls` in the `esp` directory does not support the
`ssl_context` and `server_hostname` constructor arguments, since the `ssl`
module of the esp2866 port unfortunately does not support server certificate
validation.


### Testing FTP over TLS

The `tests` directory contains the `pyftplib-server.py` script to start an FTP
server, which is based on the [pyftpdlib] library for CPython and which
supports FTP over TLS.

To run this script with TLS support enabled, you first need to create a server
certificate. For testing, a self-signed certificate can be used and created
with:

    openssl req -new -x509 -nodes -out cert.pem -keyout tests/key.pem

Specify the country, code, location, organization and common name, when
prompted. (Note: the test scripts in the `tests` directory assume that the
common name you choose is `example.com`. If you choose a different common name,
these scripts will fail with an error due to certificte verification failure.)

Combine the server certificate and the key into one file:

    cat tests/key.pem tests/cert.pem > tests/keycert.pem

The `ftplibtls` module needs the server certificate in DER format, so convert
it with:

    openssl x509 -in tests/cert.pem -out tests/cert.der -outform DER

Now you can start the test FTP server:

    mkdir -p tests/ftproot
    python3 tests/pyftpdlib-server.py -w -s -p 2121 -c tests/keycert.pem tests/ftproot

The FTP server will listen on port 2121, support TLS using the certificate in the
file 'tests/keycert.pem` and allow clients to read files from the direcory
`tests/ftproot` and also upload files there.

To upload a file to the test FTP server using the `ftplibtls` module, run the
`tests/test_upload.py` script:

    MICROPYPATH=`pwd` micropython tests/test_upload.py ftps://localhost:2121 <filename>

This should upload the file `<filename>` to the FTP server using FTP over TLS
and the file should appear in the `tests/ftproot` directory.


[ftplib]: https://docs.python.org/3/library/ftplib.html
[pyftpdlib]: https://github.com/giampaolo/pyftpdlib/
