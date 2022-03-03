# pylint: disable=W1203, C0103, W0631, C0301, W0703, R1710, W0125
"""Citrix Master."""

import json
import sys
from citrix.citrix_fun import CITIRIX_FUN
from helper.local_helper import log, uploadfile
from helper.variables_lb import NS_DEVICE_FIELDS
# from nautobot.nautobot_main import NautobotClient
from citrix.citrix_filters import filter_device, filter_vip, update_nautobot


class CITIRIX_MAIN:
    """Gather all NetScaler device list from ADM, run through filter."""

    def __init__(self, adm, tags, env) -> None:
        """Initialize."""
        self.adm = adm
        self.tags = tags
        self.env = env
        self.sas_vip_info = []
        self.hlpfun = CITIRIX_FUN(self.adm)
        self.citrix_main()

    def citrix_main(self):
        """Gather all NetScaler device list from ADM, run through filter."""
        for device in self.ns_device_lst():
            device["mgmt_address"] = device.get("ipv4_address")
            device["tags"] = self.tags
            if "OFS_Netscaler" in self.env:
                if device["ha_ip_address"].startswith("11."):
                    device["ipv4_address"] = device["ipv4_address"].replace("10", "11", 1)
                    device["environment"] = self.env
            elif "OFD_Netscaler" in self.env:
                if device["ha_ip_address"].startswith("10.") or device["ha_ip_address"].startswith("167."):
                    device["environment"] = self.env
            if filter_device(device, self.env):
                device["vips"] = self.gather_vip_info(device)
                if device.get("vips"):
                    self.sas_vip_info.extend(device.get("vips"))
                    # update_nautobot(device)
                    # if nautobotday():
                    #     NautobotClient(device)
        log.info(uploadfile(self.sas_vip_info, self.env))
        update_nautobot(device, self.env)
        log.info("Job done")

    def ns_device_lst(self):
        """Get device list function."""
        try:
            jresp = json.loads(self.adm.adm_api_call().text)
            log.info(f"ADC Netscaler Device count : {len(jresp.get('ns'))}")
            device_info = [dict((i, device[i]) for i in NS_DEVICE_FIELDS) for device in jresp.get("ns")]
            return device_info
        except Exception as err:
            log.error(f"{sys._getframe().f_code.co_name}: {err}")
            return []

    def gather_vip_info(self, device):
        """Gather VIP information for each devices."""
        vs_lst = self.hlpfun.pull_vip_info(device).get("lbvserver", [])
        log.info(f"{device.get('hostname')}: {len(vs_lst)} VIPs")
        vip_lst = []
        for vs_name in vs_lst:
            if filter_vip(vs_name):
                vip_info = self.vip_tempate(vs_name, device)
                pool_info = self.hlpfun.pull_sgrp_info(vs_name)
                if pool_info:
                    vip_info.update(pool_info)
                if vs_name.get("servicetype") == "SSL" or vs_name.get("servicetype") == "SSL_TCP":
                    cert_info = self.hlpfun.pull_cert_info()
                    if cert_info:
                        vip_info["cert"] = cert_info
                vip_lst.append(vip_info)
        return vip_lst

    def vip_tempate(self, vs_name, device):
        vip_info = dict(
            [
                ("name", vs_name.get("name")),
                ("address", vs_name.get("ipv46")),
                ("port", vs_name.get("port")),
                ("protocol", "UDP" if vs_name.get("servicetype") == "UDP" else "TCP"),
                ("loadbalancer", device.get("hostname")),
                ("tags", device.get("tags")),
                ("environment", self.env),
            ]
        )
        return vip_info
