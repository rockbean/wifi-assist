import dev_remote
import json


class DevInfo():
    def __init__(self):
        self._dev_remote = dev_remote.DevRemote()
        self._dev_con = False

    def dev_connect(self, ip, usr, pwd):
        conn = self._dev_remote.remote_connect(ip, usr, pwd)
        self._dev_con = conn
        return conn

    def dev_disconnect(self):
        if self._dev_con == True:
            self._dev_remote.remote_close()
            self._dev_con = False

    def dev_is_connect(self):
        return self._dev_con

    def dev_show_log(self, flag):
        show_cmd = "show logging " + flag
        if self._dev_con:
            return self._dev_remote.remote_cmd(show_cmd)
        else:
            return False, ["Device isn't accessable"]

    def dev_get_radio(self, iface):
        show_cmd = "show interface " + iface
        # Todo command result to json file
        iface_file = "test/"+iface
        if self._dev_con:
            iface_file = open(iface_file, 'r')
            iface = json.load(iface_file)
            iface_file.close()
            return iface
        else:
            return False, ["Device isn't accessable"]

    def dev_show_configure(self):
        show_cmd = "show running-config"
        if self._dev_con:
            return self._dev_remote.remote_cmd(show_cmd)
        else:
            return False, ["Device isn't accessable"]

    def dev_add_configure(self):
        pass

    def dev_del_configure(self):
        pass

    def dev_monitor(self):
        if self._dev_con == False:
            return
        pass
