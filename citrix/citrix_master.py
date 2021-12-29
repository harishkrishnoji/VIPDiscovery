import os
import json
from helper.script_conf import *
from citrix_fun import *
from citrix_adm.client import ADMClient
from helper.db_fun import MongoDB

log = LOG("citrix_master")

ENV = os.environ.get("RD_OPTION_ENV")
svcp = os.environ.get("RD_OPTION_SVC_PWD")
svcu = os.environ.get("RD_OPTION_SVC_USER")
dbp = os.environ.get("RD_OPTION_DB_PWD")
dbu = os.environ.get("RD_OPTION_DB_USER")
dbh = os.environ.get("RD_OPTION_DB_HOST")
db = MongoDB(dbu, dbp, dbh, log)


def citrix_master(adm):
    """Gather all NetScaler device list from ADM, run through filter.

    Args:
        adm (object): ADM Instance.
    """
    ns_info = ns_device_lst(adm)
    for device in ns_info:
        # Filter to look for Standby, non OFS, and Standalone
        var = device["ha_ip_address"].startswith("10.") or device["ha_ip_address"].startswith("167.")
        device["tags"] = ["ofd", "netscaler"]
        device["environment"] = ENV
        if "OFS_Netscaler" in ENV:
            var = device["ha_ip_address"].startswith("11.")
            device["ipv4_address"] = device["ipv4_address"].replace("10", "11", 1)
            device["tags"] = ["ofs", "netscaler"]
        db.host_collection(device)
        if (
            f"{var} is True and (device['hostname'] not in DISREGARD_LB_CITRIX)) and "
            "((device['ha_master_state'] == 'Secondary' and device['instance_state'] == 'Up' and device['ipv4_address'] != '') or "
            "('DEFRA1SLBSFA02A' in device['hostname'] and device['instance_state'] == 'Up')"
        ):
            gather_vip_info(device, adm)


def ns_device_lst(adm):
    """Get device list function.

    Args:
        adm (Class): ADM Instance.

    Returns:
        Return dict of devices.
    """
    resp = adm.adm_api_call()
    log.debug(f"NS Device list Status code : {resp.status_code}")
    jresp = json.loads(resp.text)
    return list(dict((i, j[i]) for i in NS_DEVICE) for j in jresp["ns"])


def gather_vip_info(device, adm):
    """Gather VIP information for each devices.

    Args:
        device (dict): Device info.
        adm (object): ADM Instance.
    """
    vs_lst = pull_vip_info(device, adm).get("lbvserver", [])
    log.debug(f"[{len(vs_lst)}] VIPs...")
    vip_lst = []
    for vs_name in vs_lst:
        if vs_name.get("name") and vs_name.get("ipv46") not in DISREGARD_VIP:
            vip_info = dict(
                [
                    ("address", vs_name.get("ipv46")),
                    ("port", vs_name.get("port")),
                    ("protocol", "UDP" if vs_name.get("servicetype") == "UDP" else "TCP"),
                    ("loadbalancer", device.get("hostname")),
                    ("tag", device.get("tags")),
                    ("environment", ENV),
                ]
            )
            if (pool_to_nautobot := pull_sgrp_info(vs_name, adm)) is not None:
                vip_info.update(pool_to_nautobot)
            if vs_name.get("servicetype") == "SSL" or vs_name.get("servicetype") == "SSL_TCP":
                if (cert_to_nautobot := pull_cert_info(vs_name, adm)) is not None:
                    vip_info["cert"] = cert_to_nautobot
            vip_lst.append(vip_info)
    device["vips"] = vip_lst
    db.host_collection(device)
    for vip in device.get("vips", []):
        db.vip_collection(vip)


if __name__ == "__main__":
    adm = ADMClient("https://adc.1dc.com/nitro/v1/", svcu, svcp)
    citrix_master(adm)
