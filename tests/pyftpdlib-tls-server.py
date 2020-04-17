#!/usr/bin/env python
#
# Source:  https://pyftpdlib.readthedocs.io/en/latest/tutorial.html#ftps-ftp-over-tls-ssl-server
#
"""An RFC-4217 asynchronous FTPS server supporting both SSL and TLS.

Requires PyOpenSSL module (http://pypi.python.org/pypi/pyOpenSSL).

"""

from pyftpdlib.servers import FTPServer
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import TLS_FTPHandler


def main(args=None):
    if args:
        port = int(args[0])
    else:
        port = 21

    authorizer = DummyAuthorizer()
    authorizer.add_user('user', '12345', '.', perm='elradfmwMT')
    authorizer.add_anonymous('.')
    handler = TLS_FTPHandler
    handler.certfile = 'keycert.pem'
    handler.authorizer = authorizer
    # requires SSL for both control and data channel
    handler.tls_control_required = True
    handler.tls_data_required = True
    server = FTPServer(('', port), handler)
    server.serve_forever()


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv[1:]) or 0)
