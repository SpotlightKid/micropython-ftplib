from ftp_tls import FTP_TLS

PORT = 2121

ftp = FTP_TLS()
ftp.connect('localhost', PORT)
ftp.login()
ftp.prot_p()
files = ftp.nlst()
print(files)

assert 'test_ftplib.py' in files
assert 'pyftpdlib-tls-server.py' in files
assert 'keycert.pem' in files
