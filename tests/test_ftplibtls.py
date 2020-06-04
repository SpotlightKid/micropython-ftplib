from ftplibtls import FTP_TLS

PORT = 2121

ftp = FTP_TLS()
ftp.connect('localhost', PORT)
ftp.login()
ftp.prot_p()
files = ftp.nlst()
print(files)

assert 'test_ftplibtly.py' in files
assert 'pyftpdlib-tls-server.py' in files
assert 'keycert.pem' in files
