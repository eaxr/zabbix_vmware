#!/usr/bin/env python
# coding: utf-8

zbx_api_user = 'zabbix_api'
zbx_api_pass = 'zabbix'
zbx_api_url  = 'https://example.ru/zabbix/api_jsonrpc.php'
zbx_log_path = '/var/log/zabbix_vmware.log'
zbx_wait_time = 3600
zbx_tempname_base = 'VMware Guest'
zbx_tempname_hypervisor = 'VMware Hypervisor'

zbx_drule_dict = {
    "VMware Guest": "Network device discovery",
    "VMware Hypervisor": "Datastore discovery",
    "VMware": "Discover VMware datastores"
}
