class DevVap():
    def __init__(self, vap):
        self._name = vap["name"]
        self._mac_addr = vap["MAC addr"]
        self._state = vap["state"]
        self._hive = vap["Hive"]
        self._ssid = vap["SSID"]
        self._auth = vap["auth"]
    
class DevRadio():
    def __init__(self, iface):
        self._name = iface["name"]
        self._mode = iface["mode"]
        self._phy = iface["phy"]
        self._channel = iface["channel"]
        self._chan_width = iface["channel-width"]
        self._txpower = iface["txpower"]
        self._vap = []
        for vap in iface["vap"]:
            self._vap.append(DevVap(vap))
    