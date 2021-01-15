#!/usr/bin/env python
# coding: utf-8

import sys
import os
import os.path
import json
import requests
import logging

import zabbix_vmware_settings

class ZabbixAPI:
    def __init__(self, api_url, api_user, api_pass):
        self.api_url = api_url
        self.headers = {"Content-Type": "application/json"}
        self.token = self.getToken(api_url, api_user, api_pass)

    def postReq(self, payload):
        return requests.post(self.api_url, headers=self.headers, json=payload).json()

    def getToken(self, api_url, api_user, api_pass):
        method = "user.login"
        payload = {"jsonrpc": "2.0", "method": method, "params": {"user": api_user,"password": api_pass}, "id": 1}
        return self.postReq(payload)

    def getHost(self):
        method = "template.get"
        payload = {"jsonrpc": "2.0", "method": method, "params": { "output": "extend", "selectHosts": "extend", "filter": { "host": [ "Template VM VMware Guest" ] } }, "auth": self.token['result'], "id": 1}
        return self.postReq(payload)

    def getItem(self, hostid, key, name):
        method = "item.get"
        payload = {"jsonrpc": "2.0", "method": method, "params": { "output": ["itemid", "name", "lastvalue", "state"], "hostids": hostid, "search": { "key": key }, "sortfield": "name", "filter": { "name": [ name ] } }, "auth": self.token['result'], "id": 1}
        return self.postReq(payload)

    def getItemState(self, hostid):
        method = "item.get"
        payload = {"jsonrpc": "2.0", "method": method, "params": { "output": ["itemid", "name", "status"], "hostids": hostid, "sortfield": "name", "filter": { "state": "1" } }, "auth": self.token['result'], "id": 1}
        return self.postReq(payload)

    def updateItem(self, itemid, status):
        method = "item.update"
        payload = {"jsonrpc": "2.0", "method": method, "params": { "itemid": itemid, "status": status }, "auth": self.token['result'], "id": 1}
        return self.postReq(payload)

    def updateList(self, search2, status, check, zbx_logger, hostname, visname, hostid):
        for itemNum in range(0, len(search2)):
            itemid = search2[itemNum]['itemid']
            itemStatus = search2[itemNum]['status']
            #print("Item ID =", itemid)
            #print("Item =", search2[itemNum])
            if itemid and itemStatus == check:
                self.updateItem(itemid, status)
                if status == 1:
                    msg = "Disable Item with ID = {} for {} ({}), Host ID = {}".format(itemid, hostname, visname, hostid)
                elif status == 0:
                    msg = "Enable Item with ID = {} for {} ({}), Host ID = {}".format(itemid, hostname, visname, hostid)
                print(msg)
                zbx_logger.warning(msg)

def main():
    zbx_api_user = zabbix_vmware_settings.zbx_api_user
    zbx_api_pass = zabbix_vmware_settings.zbx_api_pass
    zbx_api_url = zabbix_vmware_settings.zbx_api_url
    zbx_log_path = zabbix_vmware_settings.zbx_log_path

    zbx_logger = logging.getLogger()
    zbx_logger.setLevel(logging.WARN)
    formatter = logging.Formatter('%(process)d:%(asctime)s [Zabbix_VMware] %(message)s', datefmt='%Y%m%d:%H%M%S.%03d')
    zbx_logfile = logging.FileHandler(zbx_log_path)
    zbx_logfile.setFormatter(formatter)
    zbx_logger.addHandler(zbx_logfile)

    zb = ZabbixAPI(zbx_api_url, zbx_api_user, zbx_api_pass)
    result = zb.getHost()
    search = result['result'][0]['hosts']
    print("=======================================")
    #zbx_logger.warning("zabbix_vmware start")
    for hostNum in range(0, len(search)):
        hostid = search[hostNum]['hostid']
        print("Host ID =", hostid)
        hostname = search[hostNum]['host']
        print("Host name =", hostname)
        visname = search[hostNum]['name']
        print("Visible name =", visname)
        powerState = zb.getItem(hostid, 'vmware.vm.powerstate[{$VMWARE.URL},{HOST.HOST}]', 'VMware: Power state')
        print("Power State =", powerState['result'][0]['lastvalue'])
        if powerState['result'][0]['lastvalue'] == "0":
            itemState = zb.getItemState(hostid)
            search2 = itemState['result']
            zb.updateList(search2, 1, "0", zbx_logger, hostname, visname, hostid)
        elif powerState['result'][0]['lastvalue'] == "1":
            itemState = zb.getItemState(hostid)
            search2 = itemState['result']
            zb.updateList(search2, 0, "1", zbx_logger, hostname, visname, hostid)
        print("\n")
    print("=======================================")
    #zbx_logger.warning("zabbix_vmware finish")

if __name__ == "__main__":
    main()
