import json
from helper.script_conf import *
from citrix.citrix_fun import *


def citrix_master(adm, tags, ENV, db):
    """Gather all NetScaler device list from ADM, run through filter.

    Args:
        adm (obj): ADM Instance.
        tags (lst): List of Tags associated for Nautobot object.
        ENV (str): Enviroment OFD, OFS.
        db (obj): Mongo DB Instance.
    """
    log.debug("Master Citrix Initiated.. ")
    log.debug(f"Gather Device list for {ENV}..")
    ns_info = ns_device_lst(adm)
    for device in ns_info:
        # Filter to look for Standby, non OFS, and Standalone
        device["tags"] = tags
        if "OFS_Netscaler" in ENV:
            var = device["ha_ip_address"].startswith("11.")
            if var:
                device["ipv4_address"] = device["ipv4_address"].replace("10", "11", 1)
                device["environment"] = ENV
        elif "OFD_Netscaler" in ENV:
            var = device["ha_ip_address"].startswith("10.") or device["ha_ip_address"].startswith("167.")
            if var:
                device["environment"] = ENV

        if device.get("environment") == ENV:
            if (
                "device['hostname'] not in DISREGARD_LB_CITRIX) and "
                "((device['ha_master_state'] == 'Secondary' and device['instance_state'] == 'Up' and device['ipv4_address'] != '') or "
                "('DEFRA1SLBSFA02A' in device['hostname'] and device['instance_state'] == 'Up')"
            ):
                # if device.get("hostname") == "AUSYD2SLBSFM01A-D2NR":
                gather_vip_info(device, adm, ENV, db)
            else:
                db.host_collection(device)


def ns_device_lst(adm):
    """Get device list function.

    Args:
        adm (Class): ADM Instance.

    Returns:
        Return dict of devices.
    """
    try:
        resp = adm.adm_api_call()
        jresp = json.loads(resp.text)
        log.debug(f"NS Device count : {len(jresp.get('ns'))}")
        return list(dict((i, j[i]) for i in NS_DEVICE) for j in jresp["ns"])
    except Exception as err:
        log.error(f"{err}")


def gather_vip_info(device, adm, ENV, db):
    """Gather VIP information for each devices.

    Args:
        device (dict): Device info.
        adm (object): ADM Instance.
        ENV (str): Enviroment OFD, OFS.
        db (obj): Mongo DB Instance.
    """
    log.debug(f"{device.get('hostname')}: Gathering VIP Info..")
    vs_lst = pull_vip_info(device, adm).get("lbvserver", [])
    log.debug(f"{device.get('hostname')}: {len(vs_lst)} VIPs...")
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
    match = db.vip_diff(device)
    log.debug(f"{device.get('hostname')}: Device info DB Update...")
    db.host_collection(device)
    if not match:
        log.debug(f"{device.get('hostname')}: VIP info DB Update...")
        for vip in device.get("vips", []):
            db.vip_collection(vip)
    else:
        log.debug(f"{device.get('hostname')}: NO change in VIP info")
