import pxssh
s = pxssh.pxssh()
if not s.login ('10.200.0.116', 'oracle', 'oracle'):
    print "SSH session failed on login."
    print str(s)
else:
    s.sendline('ls -l')
    s.prompt()
    print  '\n'.join(str(s.before).split('\n')[1::])
    s.logout()
    
#We can also execute multiple command like this:
#s.sendline ('uptime;df -h')
