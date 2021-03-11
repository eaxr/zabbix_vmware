#!/usr/bin/env python
# coding: utf-8

zbx_api_user = 'zabbix_api'
zbx_api_pass = 'zabbix'
zbx_api_url  = 'https://example.ru/zabbix/api_jsonrpc.php'
zbx_log_path = '/var/log/zabbix_vmware.log'
zbx_wait_time = 900

zbx_drule_dict = {
    "Template VM VMware Guest": "Network device discovery",
    "Template VM VMware Hypervisor": "Datastore discovery"
}
