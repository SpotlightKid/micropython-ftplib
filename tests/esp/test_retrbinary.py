from ftplibtls import FTP_TLS

FTP_HOST = "192.168.0.1"
FTP_PORT = 990
FTP_USER = "joedoe"
FTP_PASS = "abc123"

ftp = FTP_TLS(FTP_HOST, FTP_PORT)
ftp.login(FTP_USER, FTP_PASS)
ftp.prot_p()
filename = "test.txt"

with open(filename, "wb") as fp:
    result = ftp.retrbinary(f"RETR {filename}", fp.write)
    print(f"FTP download of '{filename}', status: {result}")

