try:
 import usocket as _socket
except ImportError:
 import socket as _socket
__all__=("Error","FTP","error_perm","error_proto","error_reply","error_temp")
MSG_OOB=0x1
FTP_PORT=21
MAXLINE=8192
CRLF='\r\n'
B_CRLF=b'\r\n'
MIN_PORT=40001
MAX_PORT=40100
_GLOBAL_DEFAULT_TIMEOUT=object()
_SSLSocket=None
class Error(Exception):
 pass
class error_reply(Error):
 pass
class error_temp(Error):
 pass
class error_perm(Error):
 pass
class error_proto(Error):
 pass
def _resolve_addr(addr):
 if isinstance(addr,(bytes,bytearray)):
  return addr
 family=_socket.AF_INET
 if len(addr)!=2:
  family=_socket.AF_INET6
 if not addr[0]:
  host="127.0.0.1" if family==_socket.AF_INET else "::1"
 else:
  host=addr[0]
 return _socket.getaddrinfo(host,addr[1],family)
if getattr(_socket,'SocketType',None):
 socket=_socket.socket
else:
 class socket:
  def __init__(self,*args,**kw):
   if args and isinstance(args[0],_socket.socket):
    self._sock=args[0]
   else:
    self._sock=_socket.socket(*args,**kw)
  def accept(self):
   s,addr=self._sock.accept()
   return self.__class__(s),addr
  def bind(self,addr):
   return self._sock.bind(_resolve_addr(addr))
  def connect(self,addr):
   return self._sock.connect(_resolve_addr(addr))
  def sendall(self,*args):
   return self._sock.send(*args)
  def __getattr__(self,name):
   return getattr(self._sock,name)
  def __enter__(self):
   return self
  def __exit__(self,*args):
   self._sock.close()
class FTP:
 debugging=0
 host=None
 port=FTP_PORT
 timeout=_GLOBAL_DEFAULT_TIMEOUT
 source_address=None
 maxline=MAXLINE
 sock=None
 file=None
 welcome=None
 passiveserver=1
 encoding="latin-1"
 def __init__(self,host=None,port=None,user=None,passwd=None,acct=None,timeout=_GLOBAL_DEFAULT_TIMEOUT,source_address=None):
  if timeout is not None:
   self.timeout=timeout
  if source_address:
   self.source_address=source_address
  if host:
   self.connect(host,port)
   if user:
    self.login(user,passwd,acct)
 def __enter__(self):
  return self
 def __exit__(self,*args):
  if self.sock is not None:
   try:
    self.quit()
   except(OSError,EOFError):
    pass
   finally:
    if self.sock is not None:
     self.close()
 def _create_connection(self,addr,timeout=None,source_address=None):
  sock=socket()
  addrinfos=_resolve_addr(addr)
  for af,_,_,_,addr in addrinfos:
   try:
    sock.connect(addr)
   except Exception as exc:
    if self.debugging:
     print(exc)
   else:
    if timeout and timeout is not _GLOBAL_DEFAULT_TIMEOUT:
     sock.settimeout(timeout)
    try:
     sock.family=af
    except:
     pass
    return sock
  else:
   raise Error("Could not connect to %r"%(addr,))
 def connect(self,host=None,port=None,timeout=None,source_address=None):
  if host:
   self.host=host
  if port:
   self.port=port
  if timeout is not None:
   timeout=self.timeout
  if not source_address:
   source_address=self.source_address
  self.sock=self._create_connection((self.host,self.port),timeout,source_address)
  self.af=self.sock.family
  self.file=self.sock.makefile('r')
  self.welcome=self.getresp()
  return self.welcome
 def getwelcome(self):
  if self.debugging:
   print('*welcome*',self.sanitize(self.welcome))
  return self.welcome
 def set_debuglevel(self,level):
  self.debugging=level
 debug=set_debuglevel
 def set_pasv(self,val=True):
  self.passiveserver=val
 def sanitize(self,s):
  if s[:5]in{'pass ','PASS '}:
   i=len(s.rstrip('\r\n'))
   s=s[:5]+'*'*(i-5)+s[i:]
  return repr(s)
 def putline(self,line):
  line=line+CRLF
  if self.debugging>1:
   print('*put*',self.sanitize(line))
  self.sock.sendall(line.encode(self.encoding))
 def putcmd(self,line):
  if self.debugging:
   print('*cmd*',self.sanitize(line))
  self.putline(line)
 def getline(self):
  line=self.file.readline(self.maxline+1)
  if len(line)>self.maxline:
   raise Error("got more than %d bytes"%self.maxline)
  if self.debugging>1:
   print('*get*',self.sanitize(line))
  if not line:
   raise EOFError
  return line.rstrip('\r\n')
 def getmultiline(self):
  line=self.getline()
  if line[3:4]=='-':
   code=line[:3]
   while 1:
    nextline=self.getline()
    line=line+('\n'+nextline)
    if nextline[:3]==code and nextline[3:4]!='-':
     break
  return line
 def getresp(self):
  resp=self.getmultiline()
  if self.debugging:
   print('*resp*',self.sanitize(resp))
  self.lastresp=resp[:3]
  c=resp[:1]
  if c in{'1','2','3'}:
   return resp
  if c=='4':
   raise error_temp(resp)
  if c=='5':
   raise error_perm(resp)
  raise error_proto(resp)
 def voidresp(self):
  resp=self.getresp()
  if not resp.startswith('2'):
   raise error_reply(resp)
  return resp
 def abort(self):
  line=b'ABOR'+B_CRLF
  if self.debugging>1:
   print('*put urgent*',self.sanitize(line))
  self.sock.sendall(line,MSG_OOB)
  resp=self.getmultiline()
  if resp[:3]not in{'426','225','226'}:
   raise error_proto(resp)
  return resp
 def sendcmd(self,cmd):
  self.putcmd(cmd)
  return self.getresp()
 def voidcmd(self,cmd):
  self.putcmd(cmd)
  return self.voidresp()
 def sendport(self,host,port):
  hbytes=host.split('.')
  pbytes=[repr(port//256),repr(port%256)]
  bytes=hbytes+pbytes
  cmd='PORT '+','.join(bytes)
  return self.voidcmd(cmd)
 def sendeprt(self,host,port):
  af=0
  if self.af==_socket.AF_INET:
   af=1
  if self.af==_socket.AF_INET6:
   af=2
  if af==0:
   raise error_proto('unsupported address family')
  fields=['',repr(af),host,repr(port),'']
  cmd='EPRT '+'|'.join(fields)
  return self.voidcmd(cmd)
 def makeport(self):
  err=None
  sock=None
  if self.source_address and self.source_address[0]:
   host=self.source_address[0]
  else:
   host="127.0.0.1" if self.af==_socket.AF_INET else "::1"
  for port in range(MIN_PORT,MAX_PORT):
   addrinfo=_socket.getaddrinfo(host,port,self.af)
   for af,socktype,proto,_,addr in addrinfo:
    if af==self.af and socktype==_socket.SOCK_STREAM:
     try:
      sock=socket(af,socktype,proto)
      sock.bind(addr)
     except OSError as _:
      err=_
      if sock:
       sock.close()
      sock=None
      continue
     else:
      try:
       sock.family=af
      except:
       pass
      if isinstance(addr,tuple):
       host=addr[0]
      else:
       try:
        host=_socket.inet_ntop(af,addr[4:8])
       except:
        pass
      break
   if sock:
    break
  if sock is None:
   if err is not None:
    raise err
   else:
    raise OSError("getaddrinfo returns an empty list")
  sock.listen(1)
  if self.af==_socket.AF_INET:
   self.sendport(host,port)
  else:
   self.sendeprt(host,port)
  if self.timeout is not _GLOBAL_DEFAULT_TIMEOUT:
   sock.settimeout(self.timeout)
  return sock
 def makepasv(self):
  if self.af==_socket.AF_INET:
   host,port=parse227(self.sendcmd('PASV'))
  else:
   port=parse229(self.sendcmd('EPSV'))
   try:
    host=self.sock.getpeername()
   except AttributeError:
    host=self.host
  return host,port
 def ntransfercmd(self,cmd,rest=None):
  size=None
  if self.passiveserver:
   host,port=self.makepasv()
   conn=self._create_connection((host,port),self.timeout,self.source_address)
   try:
    if rest is not None:
     self.sendcmd("REST %s"%rest)
    resp=self.sendcmd(cmd)
    if resp[0]=='2':
     resp=self.getresp()
    if resp[0]!='1':
     raise error_reply(resp)
   except:
    conn.close()
    raise
  else:
   sock=self.makeport()
   try:
    if rest is not None:
     self.sendcmd("REST %s"%rest)
    resp=self.sendcmd(cmd)
    if resp[0]=='2':
     resp=self.getresp()
    if resp[0]!='1':
     raise error_reply(resp)
    conn,_=sock.accept()
    if self.timeout is not _GLOBAL_DEFAULT_TIMEOUT:
     conn.settimeout(self.timeout)
   finally:
    sock.close()
  if resp.startswith('150'):
   size=parse150(resp)
  return conn,size
 def transfercmd(self,cmd,rest=None):
  return self.ntransfercmd(cmd,rest)[0]
 def login(self,user='',passwd='',acct=''):
  if not user:
   user='anonymous'
  if not passwd:
   passwd=''
  if not acct:
   acct=''
  if user=='anonymous' and passwd in('','-'):
   passwd='anonymous@'
  resp=self.sendcmd('USER '+user)
  if resp[0]=='3':
   resp=self.sendcmd('PASS '+passwd)
  if resp[0]=='3':
   resp=self.sendcmd('ACCT '+acct)
  if resp[0]!='2':
   raise error_reply(resp)
  return resp
 def retrbinary(self,cmd,callback,blocksize=8192,rest=None):
  self.voidcmd('TYPE I')
  with self.transfercmd(cmd,rest)as conn:
   while 1:
    data=conn.recv(blocksize)
    if not data:
     break
    callback(data)
   if _SSLSocket is not None and isinstance(conn,_SSLSocket):
    conn.unwrap()
  return self.voidresp()
 def retrlines(self,cmd,callback=None):
  if callback is None:
   callback=print
  self.sendcmd('TYPE A')
  with self.transfercmd(cmd)as conn:
   with conn.makefile('r')as fp:
    while 1:
     line=fp.readline(self.maxline+1)
     if not line:
      break
     if len(line)>self.maxline:
      raise Error("got more than %d bytes"%self.maxline)
     if self.debugging>2:
      print('*retr*',repr(line))
     if line[-2:]==CRLF:
      line=line[:-2]
     elif line[-1:]=='\n':
      line=line[:-1]
     callback(line)
    if _SSLSocket is not None and isinstance(conn,_SSLSocket):
     conn.unwrap()
  return self.voidresp()
 def storbinary(self,cmd,fp,blocksize=8192,callback=None,rest=None):
  self.voidcmd('TYPE I')
  with self.transfercmd(cmd,rest)as conn:
   while 1:
    buf=fp.read(blocksize)
    if not buf:
     break
    conn.sendall(buf)
    if callback:
     callback(buf)
   if _SSLSocket is not None and isinstance(conn,_SSLSocket):
    conn.unwrap()
  return self.voidresp()
 def storlines(self,cmd,fp,callback=None):
  self.voidcmd('TYPE A')
  with self.transfercmd(cmd)as conn:
   while 1:
    buf=fp.readline(self.maxline+1)
    if len(buf)>self.maxline:
     raise Error("got more than %d bytes"%self.maxline)
    if not buf:
     break
    if buf[-2:]!=B_CRLF:
     if buf[-1]in B_CRLF:
      buf=buf[:-1]
     buf=buf+B_CRLF
    conn.sendall(buf)
    if callback:
     callback(buf)
   if _SSLSocket is not None and isinstance(conn,_SSLSocket):
    conn.unwrap()
  return self.voidresp()
 def acct(self,password):
  cmd='ACCT '+password
  return self.voidcmd(cmd)
 def nlst(self,*args):
  cmd='NLST'
  for arg in args:
   cmd=cmd+(' '+arg)
  files=[]
  self.retrlines(cmd,files.append)
  return files
 def dir(self,*args,**kw):
  func=kw.get('callback')
  self.retrlines(" ".join(['LIST']+list(args)),func)
 def mlsd(self,path="",facts=[]):
  if facts:
   self.sendcmd("OPTS MLST "+";".join(facts)+";")
  if path:
   cmd="MLSD %s"%path
  else:
   cmd="MLSD"
  lines=[]
  self.retrlines(cmd,lines.append)
  for line in lines:
   facts_found,_,name=line.rstrip(CRLF).partition(' ')
   entry={}
   for fact in facts_found[:-1].split(";"):
    key,_,value=fact.partition("=")
    entry[key.lower()]=value
   yield(name,entry)
 def rename(self,fromname,toname):
  resp=self.sendcmd('RNFR '+fromname)
  if resp[0]!='3':
   raise error_reply(resp)
  return self.voidcmd('RNTO '+toname)
 def delete(self,filename):
  resp=self.sendcmd('DELE '+filename)
  if resp[:3]in{'250','200'}:
   return resp
  else:
   raise error_reply(resp)
 def cwd(self,dirname):
  if dirname=='..':
   try:
    return self.voidcmd('CDUP')
   except error_perm as msg:
    if msg.args[0][:3]!='500':
     raise
  elif dirname=='':
   dirname='.' 
  cmd='CWD '+dirname
  return self.voidcmd(cmd)
 def size(self,filename):
  resp=self.sendcmd('SIZE '+filename)
  if resp[:3]=='213':
   s=resp[3:].strip()
   return int(s)
 def mkd(self,dirname):
  resp=self.voidcmd('MKD '+dirname)
  if not resp.startswith('257'):
   return ''
  return parse257(resp)
 def rmd(self,dirname):
  return self.voidcmd('RMD '+dirname)
 def pwd(self):
  resp=self.voidcmd('PWD')
  if not resp.startswith('257'):
   return ''
  return parse257(resp)
 def quit(self):
  resp=self.voidcmd('QUIT')
  self.close()
  return resp
 def close(self):
  try:
   file=self.file
   self.file=None
   if file is not None:
    file.close()
  finally:
   sock=self.sock
   self.sock=None
   if sock is not None:
    sock.close()
def _find_parentheses(s):
 left=s.find('(')
 if left<0:
  raise ValueError("missing left delimiter")
 right=s.find(')',left+1)
 if right<0:
  raise ValueError("missing right delimiter")
 return left,right
def parse150(resp):
 try:
  left,right=_find_parentheses(resp)
 except ValueError:
  return None
 else:
  try:
   val,_=resp[left+1:right].split(None,1)
   return int(val)
  except(ValueError,TypeError)as exc:
   raise error_proto("Error parsing response '%s': %s"%(resp,exc))
def parse227(resp):
 if not resp.startswith('227'):
  raise error_reply("Unexpected response: %s"%resp)
 try:
  left,right=_find_parentheses(resp)
  numbers=tuple(int(i)for i in resp[left+1:right].split(',',6))
  host='%i.%i.%i.%i'%numbers[:4]
  port=(numbers[4]<<8)+numbers[5]
 except Exception as exc:
  raise error_proto("Error parsing response '%s': %s"%(resp,exc))
 return host,port
def parse229(resp):
 if not resp.startswith('229'):
  raise error_reply("Unexpected response: %s"%resp)
 try:
  left,right=_find_parentheses(resp)
  if resp[left+1]!=resp[right-1]:
   raise ValueError("separator mismatch")
  parts=resp[left+1:right].split(resp[left+1])
  if len(parts)!=5:
   raise ValueError("unexpected number of values")
 except ValueError as exc:
  raise error_proto("Error parsing response '%s': %s"%(resp,exc))
 return int(parts[3])
def parse257(resp):
 if resp[3:5]!=' "':
  return ''
 dirname=''
 i=5
 n=len(resp)
 while i<n:
  c=resp[i]
  i=i+1
  if c=='"':
   if i>=n or resp[i]!='"':
    break
   i=i+1
  dirname=dirname+c
 return dirname
# Created by pyminifier (https://github.com/liftoff/pyminifier)
