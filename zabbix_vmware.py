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
        method = "host.get"
        payload = {"jsonrpc": "2.0", "method": method, "params": { "filter": { "host": [ "zabbix" ] } }, "auth": self.token['result'], "id": 1}
        req = requests.post(self.api_url, headers=self.headers, json=payload).json()
        return req

def main():
    zbx_api_user = zabbix_vmware_settings.zbx_api_user
    zbx_api_pass = zabbix_vmware_settings.zbx_api_pass
    zbx_api_url = zabbix_vmware_settings.zbx_api_url

    zb = ZabbixAPI(zbx_api_url, zbx_api_user, zbx_api_pass)
    result = zb.getHost()
    print("=======================================")
    print("Message =", result)
    print("=======================================")

if __name__ == "__main__":
    main()
