from ftplibtls import FTP_TLS

PORT = 2121

ftp = FTP_TLS()
ftp.connect('localhost', PORT)
ftp.login('joedoe', 'abc123')
ftp.prot_p()
files = ftp.nlst()
print(files)

assert 'test_ftplibtls.py' in files
assert 'pyftpdlib-server.py' in files
assert 'keycert.pem' in files
