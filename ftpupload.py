#!/usr/bin/env micropython
# -*- coding: utf-8 -*-


def split(path):
    if path == "":
        return ("", "")

    r = path.rstrip("/").rsplit("/", 1)

    if len(r) == 1:
        return ("", path)

    return (r[0] or "/", r[1])


def basename(path):
    return split(path)[1]


def upload(ftp, path, remote_path=None, blocksize=8192, callback=None,
           rest=None):
    if remote_path:
        remote_dir, remote_path = split(remote_path)

        if remote_dir:
            ftp.cwd(remote_dir)

    if not remote_path:
        remote_path = basename(path)

    with open(path, 'rb') as fp:
        return ftp.storbinary('STOR %s' % remote_path, fp, blocksize=blocksize,
                              callback=callback, rest=rest)

