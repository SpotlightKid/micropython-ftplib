from ftplib_tls import FTP_TLS
from ftpupload import upload

ftp = FTP_TLS('192.168.42.180', 2121)
ftp.login('joedoe', 'abc123')
ftp.prot_p()
gc.collect()
upload(ftp, 'boot.py', blocksize=2048)
