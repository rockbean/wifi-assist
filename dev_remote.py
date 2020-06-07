import paramiko

class DevRemote():
    def __init__(self):
        self._remote = paramiko.SSHClient()
        self._remote.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
    def remote_connect(self, ip, usr, pwd):
        try:
            conn = self._remote.connect(ip,22,usr, pwd,timeout=2)
        except:
            return False
        else:
            return True
        
    def remote_cmd(self, cmd):
        stdin, stdout, stderr = self._remote.exec_command(cmd)
        err = stderr.readlines()
        out = stdout.readlines()
        if len(err):
            return False, err
        else:
            return True, out
        
    def remote_close(self):
        self._remote.close()
