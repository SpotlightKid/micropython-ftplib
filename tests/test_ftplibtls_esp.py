from ftplibtls import FTP_TLS

PORT = 2121

ftp = FTP_TLS()
ftp.connect('localhost', PORT)
ftp.login('joedoe', 'abc123')
ftp.prot_p()
files = []
ftp.retrlines('LIST', callback=files.append)
print("\n".join(files))

assert [line for line in files if 'README.md' in line]
