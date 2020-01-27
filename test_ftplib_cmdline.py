#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Simple test FTP client using ftplib.

Usage::

    ftp [-d] [user[:passwd]@]host[:port] [-l[dir]] [-d[dir]] [-p] [file...]

    -d dir
    -l list
    -p activate passive mode

A nice test that reveals some of the network dialogue would be::

    python ftplib.py -d localhost -l -p -l

"""

import sys
import ftplib


def ftpcmd(*args):
    # XXX: very crude command line parsing to avoid additional dependencies
    if len(args) < 1:
        print(__doc__)
        return -2

    args = list(args)
    debugging = 0

    while args[0] == '-d':
        debugging += 1
        del args[0]

    host = args.pop(0)
    try:
        userid, host = host.split('@', 1)
    except:
        if debugging:
            print("No credentials given: using anonymous login.")
        userid = passwd = ''
    else:
        try:
            userid, passwd = userid.split(':')
        except:
            passwd = ''

    if ':' in host:
        host, port = host.rsplit(':', 1)
        port = int(port)
    else:
        port = None

    ftp = ftplib.FTP()
    ftp.set_debuglevel(debugging)
    if debugging:
        print("Connecting to %s port %s..." % (host, port))
    ftp.connect(host, port)
    ftp.set_pasv(False)

    if debugging:
        print("Logging in as user '%s' with passwd '%s'." % (userid, passwd))
    ftp.login(userid, passwd)

    for file in args:
        if file == '--':
            continue
        elif file[:2] == '-l':
            ftp.dir(file[2:])
        elif file[:2] == '-d':
            cmd = 'CWD'

            if file[2:]:
                cmd = cmd + ' ' + file[2:]

            ftp.sendcmd(cmd)
        elif file == '-p':
            ftp.set_pasv()
        elif not file.startswith('-'):
            try:
                ftp.retrbinary('RETR ' + file, print, 1024)
            except ftplib.Error as exc:
                print("Could not retrieve '%s': %s" % (file, exc))
        else:
            print("Unknown command: %s" % file)

    ftp.quit()


if __name__ == '__main__':
    sys.exit(ftpcmd(*sys.argv[1:]) or 0)
