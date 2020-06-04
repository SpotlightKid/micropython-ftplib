#!/usr/bin/env python
#
# Source:  https://pyftpdlib.readthedocs.io/en/latest/tutorial.html#ftps-ftp-over-tls-ssl-server
#
"""An RFC-4217 asynchronous FTPS server supporting both SSL and TLS.

Requires PyOpenSSL module (http://pypi.python.org/pypi/pyOpenSSL).

"""

import argparse
import logging

from pyftpdlib.servers import FTPServer
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import TLS_FTPHandler


def main(args=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--port", type=int, default=21, help="FTP server port (default: %(default)s)")
    ap.add_argument("-u", "--user", default="joedoe", help="User account name (default: %(default)s)")
    ap.add_argument("-P", "--password", default="abc123", help="User account password (default: %(default)s)")
    ap.add_argument("-c", "--certfile", default="keycert.pem", help="Certificate/Keyfile (default: %(default)s)")
    ap.add_argument("-v", "--verbose", action="store_true", help="Enable verbose (debug) output")

    args = ap.parse_args(args)

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    authorizer = DummyAuthorizer()
    authorizer.add_user(args.user, args.password, '.', perm='elradfmwMT')
    authorizer.add_anonymous('.')
    handler = TLS_FTPHandler
    handler.certfile = args.certfile
    handler.authorizer = authorizer
    # requires SSL for both control and data channel
    handler.tls_control_required = True
    handler.tls_data_required = True
    server = FTPServer(('', args.port), handler)
    server.serve_forever()


if __name__ == '__main__':
    import sys
    sys.exit(main() or 0)
