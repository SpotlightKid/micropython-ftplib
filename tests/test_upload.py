from ftplib import FTP
from ftpupload import upload

def upload_file(host, filename, remote_name=None, debuglevel=1):
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

        if hasattr(ssl, "create_default_context"):
            ctx = ssl.create_default_context(cafile="tests/keycert.pem")
        else:
            ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            ctx.verify_mode = ssl.CERT_REQUIRED
            ctx.load_verify_locations(cafile="tests/cert.der")

        ftp = FTP_TLS(ssl_context=ctx, server_hostname="example.com")
    else:
        ftp = FTP()

    with ftp:
        ftp.set_debuglevel(debuglevel)
        ftp.connect(host, port)
        ftp.login('joedoe', 'abc123')

        if use_ssl:
            ftp.prot_p()

        #ftp.set_pasv(False)
        print(upload(ftp, filename, remote_name, blocksize=2048))
        ftp.close()


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: example_upload.py <hostname> <file> [<remote name>]")
        sys.exit(2)

    upload_file(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) >= 4 else None)
