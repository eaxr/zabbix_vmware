#!/usr/bin/env python
# coding: utf-8

import sys
import os
import json
import requests

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

def main():
    zbx_api_user = zabbix_vmware_settings.zbx_api_user
    zbx_api_pass = zabbix_vmware_settings.zbx_api_pass
    zbx_api_url = zabbix_vmware_settings.zbx_api_url

    zb = ZabbixAPI(zbx_api_url, zbx_api_user, zbx_api_pass)
    result = zb.getHost()
    search = result['result'][0]['hosts']
    print("=======================================")
    for hostNum in range(0, len(search)):
        print("Host ID =", search[hostNum]['hostid'])
        print("Host name =", search[hostNum]['host'])
        print("Visible name =", search[hostNum]['name'])
        print("\n")
    print("=======================================")

if __name__ == "__main__":
    main()
