import ftplib

class AdvancedFTP(ftplib.FTP):
    def acct(self, password):
        """Send new account name."""
        cmd = 'ACCT ' + password
        return self.voidcmd(cmd)

    def nlst(self, *args):
        """Return a list of files in a given directory

        Defaults to the current directory.
        """
        cmd = 'NLST'
        for arg in args:
            cmd = cmd + (' ' + arg)
        files = []
        self.retrlines(cmd, files.append)
        return files

    def mlsd(self, path="", facts=[]):
        """List a directory in a standardized format by using MLSD command
        (RFC-3659).

        If path is omitted the current directory is assumed. "facts" is a list
        of strings representing the type of information desired (e.g. ["type",
        "size", "perm"]).

        Return a generator object yielding a tuple of two elements for every
        file found in path. First element is the file name, the second one is a
        dictionary including a variable number of "facts" depending on the
        server and whether "facts" argument has been provided.
        """
        if facts:
            self.sendcmd("OPTS MLST " + ";".join(facts) + ";")
        if path:
            cmd = "MLSD %s" % path
        else:
            cmd = "MLSD"

        lines = []
        self.retrlines(cmd, lines.append)

        for line in lines:
            facts_found, _, name = line.rstrip(CRLF).partition(' ')
            entry = {}

            for fact in facts_found[:-1].split(";"):
                key, _, value = fact.partition("=")
                entry[key.lower()] = value

            yield (name, entry)

    def set_debuglevel(self, level):
        """Set the debugging level.

        The required argument level means:

        0: no debugging output (default)
        1: print commands and responses but not body text etc.
        2: also print raw lines read and sent before stripping CR/LF
        """
        self.debugging = level
    debug = set_debuglevel

    # Internal: send one line to the server, appending CRLF
    def putline(self, line):
        line = line + CRLF
        self.sock.sendall(line.encode(self.encoding))

    # Internal: send one command to the server (through putline())
    def putcmd(self, line):
        self.putline(line)

    def storlines(self, cmd, fp, callback=None):
        """Store a file in line mode.

        A new port is created for you.

        Args:
          cmd: A STOR command.
          fp: A file-like object with a readline() method.
          callback: An optional single parameter callable that is called on
                    each line after it is sent.  [default: None]

        Returns:
          The response code.
        """
        self.voidcmd('TYPE A')
        with self.transfercmd(cmd)[0] as conn:
            while 1:
                buf = fp.readline(MAXLINE + 1)
                if len(buf) > MAXLINE:
                    raise Error("got more than %d bytes" % MAXLINE)
                if not buf:
                    break
                if buf[-2:] != B_CRLF:
                    if buf[-1] in B_CRLF:
                        buf = buf[:-1]
                    buf = buf + B_CRLF
                conn.sendall(buf)
                if callback:
                    callback(buf)
            # shutdown ssl layer
            if _SSLSocket is not None and isinstance(conn, _SSLSocket):
                conn.unwrap()

        return self.voidresp()
