"""An FTP subclass which adds FTP-over-TLS support as described in RFC-4217.

Example with FTP-over-TLS. Note that you must call the ``prot_b`` method after
connecting and authentication to actually establish secure communication for
data transfers::

    >>> from ftplibtls import FTP_TLS
    >>> ftp = FTP_TLS('example.com')  # default port 21
    >>> ftp.login('username', 'password')
    >>> ftp.prot_p()
    >>> ftp.retrlines('LIST')

If you require server certficate validation (recommended)::

    >>> from ftplib import FTP_TLS, ssl
    >>> ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    >>> ctx.verify_mode = ssl.CERT_REQUIRED
    >>> ctx.load_verify_locations(cafile="cert.der")  # Certificate file must be in DER format
    >>> ftp = FTP_TLS(ssl_context=ctx, server_hostname="example.com")
    >>> ftp.connect('example.com')
    >>> ftp.prot_p()
    >>> ftp.retrlines('LIST')

Use the ``server_hostname`` constructor argument if the common name in the
server's certificate differs from the host name used for connecting.

"""

# Based on CPython standard library implementation adapted for MicroPython
# by Alexandru Rusu and Christopher Arndt

try:
    import ssl
except ImportError:
    import ussl as ssl


import ftplib


class FTP_TLS(ftplib.FTP):
    """An FTP subclass which adds FTP-over-TLS support as described in RFC-4217.

    Connect as usual to port 21, implicitly securing the FTP control connection
    before authenticating.

    Securing the data connection requires the user to explicitly ask for it by
    calling the ``prot_p()`` method.

    See the module docstring for a usage example.

    """

    def __init__(self, host=None, port=None, user=None, passwd=None, acct=None,
                 timeout=ftplib._GLOBAL_DEFAULT_TIMEOUT, source_address=None,
                 ssl_context=None, server_hostname=None):
        self.ssl_context = ssl_context
        self.server_hostname = server_hostname
        self._wrapped = False
        self._prot_p = False
        super().__init__(host, port, user, passwd, acct, timeout, source_address)

    def _wrap_socket(self, sock):
        if self.ssl_context is None:
            if hasattr(ssl, 'create_default_context'):
                self.ssl_context = ssl.create_default_context()
            else:
                self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
                self.ssl_context.verify_mode = ssl.CERT_OPTIONAL

        return self.ssl_context.wrap_socket(sock, server_hostname=self.server_hostname or self.host)

    def login(self, user=None, passwd=None, acct=None, secure=True):
        if secure and not self._wrapped:
            self.auth()
        return super().login(user, passwd, acct)

    def auth(self):
        """Set up secure control connection by using TLS/SSL."""
        if self._wrapped:
            raise ValueError("Already using TLS")

        resp = self.voidcmd('AUTH TLS')
        sock = getattr(self.sock, '_sock', None)

        if sock is None:
            sock = self.sock

        wrapped = self._wrap_socket(sock)

        if hasattr(self.sock, '_sock'):
            self.sock._sock = wrapped
            self.file = self.sock._sock
        else:
             self.sock = wrapped
             self.file = self.sock.makefile('rb')

        self._wrapped = True
        return resp

    def ccc(self):
        """Switch back to a clear-text control connection."""
        if not self._wrapped:
            raise ValueError("not using TLS")
        resp = self.voidcmd('CCC')
        self.sock = self.sock.unwrap()
        self.file = self.sock.makefile('rb')
        self._wrapped = False
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

    # --- Overridden FTP methods

    def ntransfercmd(self, cmd, rest=None):
        conn, size = super().ntransfercmd(cmd, rest)
        if self._prot_p:
            sock = self._wrap_socket(getattr(conn, '_sock', conn))

            if hasattr(conn, '_sock'):
                conn._sock = sock
            else:
                conn = sock

        return conn, size
