# -*- coding: utf-8 -*-

import ftplib


def ftpcp(source, sourcename, target, targetname='', type='I'):
    """Copy file from one FTP-instance to another."""
    if not targetname:
        targetname = sourcename

    type = 'TYPE ' + type
    source.voidcmd(type)
    target.voidcmd(type)
    sourcehost, sourceport = ftplib.parse227(source.sendcmd('PASV'))
    target.sendport(sourcehost, sourceport)
    # RFC 959: the user must "listen" [...] BEFORE sending the
    # transfer request.
    # So: STOR before RETR, because here the target is a "user".
    treply = target.sendcmd('STOR ' + targetname)

    if treply[:3] not in {'125', '150'}:
        raise ftplib.error_proto  # RFC 959

    sreply = source.sendcmd('RETR ' + sourcename)
    if sreply[:3] not in {'125', '150'}:
        raise ftplib.error_proto  # RFC 959

    source.voidresp()
    target.voidresp()
