"""An FTP subclass which adds FTP-over-TLS support as described in RFC-4217.

Example with FTP-over-TLS. Note that you must call the ``prot_b`` method after
connecting and authentication to actually establish secure communication for
data transfers::

    >>> from ftplibtls import FTP_TLS
    >>> ftp = FTP_TLS('servername')  # default port 21
    >>> ftp.login('username', 'password')
    >>> ftp.prot_p()
    >>> ftp.retrlines('LIST')

"""

# Based on CPython standard library implementation adapted for MicroPython
# by Alexandru Rusu and Christopher Arndt

try:
    import _ssl
except ImportError:
    import ussl as _ssl

try:
    import socket as _socket
except ImportError:
    import usocket as _socket

import ftplib


class FTP_TLS(ftplib.FTP):
    """An FTP subclass which adds FTP-over-TLS support as described in RFC-4217.

    Connect as usual to port 21, implicitly securing the FTP control connection
    before authenticating.

    Securing the data connection requires the user to explicitly ask for it by
    calling the ``prot_p()`` method.

    Note: the ``ssl`` module of the ESP8266 port of MicroPython does not support
    server certficate validation!

    See the module docstring for a usage example.

    """

    def __init__(self, host=None, port=None, user=None, passwd=None, acct=None,
                 timeout=ftplib._GLOBAL_DEFAULT_TIMEOUT, source_address=None,
                 keyfile=None, certfile=None):
        self._prot_p = False
        self.keyfile = keyfile
        self.certfile = certfile
        self._keydata = None
        self._certdata = None
        super().__init__(host, port, user, passwd, acct, timeout, source_address)

    def login(self, user=None, passwd=None, acct=None, secure=True):
        if secure and isinstance(self.sock._sock, _socket.socket):
            self.auth()

        return super().login(user, passwd, acct)

    def auth(self):
        """Set up secure control connection by using TLS/SSL."""
        if not isinstance(self.sock._sock, _socket.socket):
            raise ValueError("Already using TLS")

        resp = self.voidcmd('AUTH TLS')
        self.sock._sock = self._wrap_socket(self.sock._sock)
        self.file = self.sock._sock
        return resp

    def ccc(self):
        """Switch back to a clear-text control connection."""
        if isinstance(self.sock._sock, _socket.socket):
            raise ValueError("Not using TLS")

        resp = self.voidcmd('CCC')
        self.sock._sock = self.sock.unwrap()
        self.file = self.sock._sock
        return resp

    def prot_p(self):
        """Set up secure data connection."""
        # PROT defines whether or not the data channel is to be protected.
        # Though RFC-2228 defines four possible protection levels,
        # RFC-4217 only recommends two, Clear and Private.
        # Clear (PROT C) means that no security is to be used on the
        # data-channel, Private (PROT P) means that the data-channel
        # should be protected by TLS.
        # PBSZ command MUST still be issued, but must have a parameter of
        # '0' to indicate that no buffering is taking place and the data
        # connection should not be encapsulated.
        self.voidcmd('PBSZ 0')
        resp = self.voidcmd('PROT P')
        self._prot_p = True
        return resp

    def prot_c(self):
        """Set up clear text data connection."""
        resp = self.voidcmd('PROT C')
        self._prot_p = False
        return resp

    # Overridden FTP methods

    def ntransfercmd(self, cmd, rest=None):
        conn, size = super().ntransfercmd(cmd, rest)

        if self._prot_p:
            conn._sock = self._wrap_socket(conn._sock)

        return conn, size

    # Internal helper methods

    def _wrap_socket(self, sock):
        if self.keyfile and not self._keydata:
            with open(self.keyfile, 'rb') as f:
                self._keydata = f.read()

        if self.certfile and not self._certdata:
            with open(self.certfile, 'rb') as f:
                self._certdata = f.read()

        return _ssl.wrap_socket(sock, key=self._keydata, cert=self._certdata)
