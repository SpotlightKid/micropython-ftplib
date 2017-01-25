#!/usr/bin/env micropython
# -*- coding: utf-8 -*-

import os.path
import ftplib


def upload(ftp, path, remote_path=None, blocksize=8192, callback=None,
           rest=None):
    if remote_path:
        remote_dir, remote_path = os.path.split(remote_path)
        if remote_dir:
            ftp.cwd(remote_dir)

    if not remote_path:
        remote_path = os.path.basename(path)

    with open(path, 'rb') as fp:
        return ftp.storbinary('STOR %s' % remote_path, fp, blocksize=blocksize,
                              callback=callback, rest=rest)


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 3:
        print("Usage: example_upload.py <hostname> <file> [<remote name>]")
        sys.exit(2)

    ftp = ftplib.FTP()
    ftp.connect(sys.argv[1])
    ftp.set_debuglevel(1)
    ftp.login()
    upload(ftp, sys.argv[2], sys.argv[3] if len(sys.argv) >= 4 else None)
