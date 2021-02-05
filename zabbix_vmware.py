#!/usr/bin/env python
# coding: utf-8

import sys
import os
import os.path
import json
import requests
import logging
import time

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

    def getHost(self, name):
        method = "template.get"
        payload = {"jsonrpc": "2.0", "method": method, "params": { "output": "extend", "selectHosts": "extend", "filter": { "host": [ name ] } }, "auth": self.token['result'], "id": 1}
        return self.postReq(payload)

    def getItem(self, hostid, key, name):
        method = "item.get"
        payload = {"jsonrpc": "2.0", "method": method, "params": { "output": ["itemid", "name", "lastvalue", "state", "status"], "hostids": hostid, "search": { "key": key }, "sortfield": "name", "filter": { "name": [ name ] } }, "auth": self.token['result'], "id": 1}
        return self.postReq(payload)

    def getItemDR(self, hostid):
        method = "item.get"
        payload = {"jsonrpc": "2.0", "method": method, "params": { "selectDiscoveryRule": ["itemid", "name"], "hostids": hostid }, "auth": self.token['result'], "id": 1}
        return self.postReq(payload)

    def getItemByID(self, itemid):
        method = "item.get"
        payload = {"jsonrpc": "2.0", "method": method, "params": { "output": ["itemid", "name", "lastvalue", "state", "status"], "itemids": itemid }, "auth": self.token['result'], "id": 1}
        return self.postReq(payload)

    def getDRule(self, hostid, name):
        method = "discoveryrule.get"
        payload = {"jsonrpc": "2.0", "method": method, "params": { "output": ["itemid", "name"], "hostids": hostid, "filter": { "name": name } }, "auth": self.token['result'], "id": 1}
        return self.postReq(payload)

    def getItemState(self, hostid):
        method = "item.get"
        payload = {"jsonrpc": "2.0", "method": method, "params": { "output": ["itemid", "name", "status"], "hostids": hostid, "sortfield": "name", "filter": { "state": "1" } }, "auth": self.token['result'], "id": 1}
        return self.postReq(payload)

    def createTask(self, itemid):
        method = "task.create"
        payload = {"jsonrpc": "2.0", "method": method, "params": { "type": "6", "request": { "itemid": itemid } }, "auth": self.token['result'], "id": 1}
        return self.postReq(payload)

    def updateItem(self, itemid, status):
        method = "item.update"
        payload = {"jsonrpc": "2.0", "method": method, "params": { "itemid": itemid, "status": status }, "auth": self.token['result'], "id": 1}
        return self.postReq(payload)

    def updateItemDR(self, itemid, status, name, hostid, hostname, visname, zbx_logger):
        if status == "1":
            print("Status = Disabled")
            self.updateItem(itemid, "0")
            print("Item ID =", itemid, "has been enabled")
            print('Perform "execute now"')
            task = self.createTask(itemid)
            print('Task = ', task)
            time.sleep(1)
            obj = self.getItemByID(itemid)
            if obj['result'][0]['state'] == "1":
                self.updateItem(itemid, "1")
                print("Item ID =", itemid, "has been disabled")
                msg = "Item {} with ID = {} doesn't receive data, Host {} ({}) ID = {}".format(name, itemid, hostname, visname, hostid)
            elif obj['result'][0]['state'] == "0":
                print("Item ID =", itemid, "began to receive data")
                msg = "Item {} with ID = {} began to receive data, Host {} ({}) ID = {}".format(name, itemid, hostname, visname, hostid)
        elif status == "0":
            print("Status = Enabled")
            self.updateItem(itemid, "1")
            msg = "Item {} with ID = {} has been disabled, Host {} ({}) ID = {}".format(name, itemid, hostname, visname, hostid)
        zbx_logger.warning(msg)

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
    zbx_drule_dict = zabbix_vmware_settings.zbx_drule_dict

    zbx_logger = logging.getLogger()
    zbx_logger.setLevel(logging.WARN)
    formatter = logging.Formatter('%(process)d:%(asctime)s [Zabbix_VMware] %(message)s', datefmt='%Y%m%d:%H%M%S.%03d')
    zbx_logfile = logging.FileHandler(zbx_log_path)
    zbx_logfile.setFormatter(formatter)
    zbx_logger.addHandler(zbx_logfile)

    zb = ZabbixAPI(zbx_api_url, zbx_api_user, zbx_api_pass)
    result = zb.getHost('Template VM VMware Guest')
    search = result['result'][0]['hosts']
    print("=======================================")
    zbx_logger.warning("zabbix_vmware start")
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

    for template, drule in zbx_drule_dict.items():
        result = zb.getHost(template)
        search = result['result'][0]['hosts']

        for hostNum in range(0, len(search)):
            hostid = search[hostNum]['hostid']
            hostname = search[hostNum]['host']
            visname = search[hostNum]['name']

            realDR = zb.getDRule(hostid, drule)
            hostDR = zb.getItemDR(hostid)

            for itemNum in range(0, len(hostDR['result'])):
                if hostDR['result'][itemNum]['discoveryRule']:
                    if hostDR['result'][itemNum]['discoveryRule']['itemid'] == realDR['result'][0]['itemid'] and hostDR['result'][itemNum]['state'] == "1":
                        print("Host ID =", hostid)
                        print("Host name =", hostname)
                        print("Visible name =", visname)
                        print("Item ID =", hostDR['result'][itemNum]['itemid'], "Name = ", hostDR['result'][itemNum]['name'])
                        print("State = ", hostDR['result'][itemNum]['state'], "Error = ", hostDR['result'][itemNum]['error'])
                        zb.updateItemDR(hostDR['result'][itemNum]['itemid'], hostDR['result'][itemNum]['status'], hostDR['result'][itemNum]['name'], hostid, hostname, visname, zbx_logger)
                        print("\r")
    print("=======================================")
    #zbx_logger.warning("zabbix_vmware finish")

if __name__ == "__main__":
    main()
