from ftpadvanced import AdvancedFTP

PORT = 2121

ftp = AdvancedFTP('192.168.42.180', PORT)
ftp.login('joedoe', 'abc123')
files = ftp.nlst()
print(files)

assert 'test_ftplibtls.py' in files
assert 'pyftpdlib-tls-server.py' in files
assert 'keycert.pem' in files
