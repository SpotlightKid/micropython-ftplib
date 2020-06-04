import sys


if len(sys.argv) < 3:
    print("Usage: example_upload.py <hostname> <file> [<remote name>]")
    sys.exit(2)

host = sys.argv[1]
use_ssl = False

if host.startswith('ftps://'):
    host = host[7:]
    use_ssl = True
elif host.startswith('ftp://'):
    host = host[6:]

try:
    host, port = host.rsplit(':', 1)
    port = int(port)
except:
    port = 21

if use_ssl:
    from ftplibtls import FTP_TLS, ssl
    ftp = FTP_TLS(keyfile="tests/keycert.pem", certfile="tests/keycert.pem", cert_reqs=ssl.CERT_REQUIRED)
else:
    from ftplib import FTP
    ftp = FTP()

from ftpupload import upload

with ftp:
    ftp.set_debuglevel(2)
    ftp.connect(host, port)
    ftp.login('joedoe', 'abc123')

    if use_ssl:
        ftp.prot_p()

    #ftp.set_pasv(False)
    print(upload(ftp, sys.argv[2], sys.argv[3] if len(sys.argv) >= 4 else None))
