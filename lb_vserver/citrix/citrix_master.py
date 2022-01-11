# pylint: disable=W1203, C0103, W0631, C0301, W0703, R1710, W0125
"""Citrix Master."""

import os
import json
from citrix.citrix_fun import pull_vip_info, pull_sgrp_info, pull_cert_info
from helper.local_helper import log
from helper.variables_lb import DISREGARD_VIP, NS_DEVICE_FIELDS, DISREGARD_LB_CITRIX, FILTER_VIP
from nautobot.nautobot_master import NautobotClient


def citrix_master(adm, tags, ENV):
    """Gather all NetScaler device list from ADM, run through filter.

    Args:
        adm (obj): ADM Instance.
        tags (lst): List of Tags associated for Nautobot object.
        ENV (str): Enviroment OFD, OFS.
    """
    log.debug("Master Citrix Initiated.. ")
    log.debug(f"Gather Device list for {ENV}..")
    ns_info = ns_device_lst(adm)
    for device in ns_info:
        # Filter to look for Standby, non OFS, and Standalone
        device["mgmt_address"] = device.pop("mgmt_ip_address")
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
            if (device["hostname"] not in DISREGARD_LB_CITRIX) and (
                (
                    device["ha_master_state"] == "Secondary"
                    and device["instance_state"] == "Up"
                    and device["ipv4_address"] != ""
                )
                or ("DEFRA1SLBSFA02A" in device["hostname"] and device["instance_state"] == "Up")
            ):
                # if device.get("hostname") == "AUSYD2SLBSFM01A-D2NR":
                gather_vip_info(device, adm, ENV)
            else:
                NautobotClient(device)


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
        log.debug(f"Netscaler Device count : {len(jresp.get('ns'))}")
        device_info = []
        NS_DEVICE_TO_QUERY = os.environ.get("RD_OPTION_DEVICES", "All")
        for device in jresp["ns"]:
            # For Test or Troubleshooting purpose
            # Filter the devices for which you want to discover VIPs
            if "All" in NS_DEVICE_TO_QUERY or device["hostname"] in NS_DEVICE_TO_QUERY:
                log.debug(f"{device['hostname']}")
                # Filter only the Fields/Keys which match NS_DEVICE_TO_QUERY
                device_info.append(dict((i, device[i]) for i in NS_DEVICE_FIELDS))
        return device_info
    except Exception as err:
        log.error(f"{err}")


def gather_vip_info(device, adm, ENV):
    """Gather VIP information for each devices.

    Args:
        device (dict): Device info.
        adm (object): ADM Instance.
        ENV (str): Enviroment OFD, OFS.
    """
    log.debug(f"{device.get('hostname')}: Gathering VIP Info..")
    vs_lst = pull_vip_info(device, adm).get("lbvserver", [])
    log.debug(f"{device.get('hostname')}: {len(vs_lst)} VIPs...")
    vip_lst = []
    for vs_name in vs_lst:
        if (
            vs_name.get("name")
            and vs_name.get("ipv46") not in DISREGARD_VIP
            and ("All" in FILTER_VIP or vs_name.get("name") in FILTER_VIP)
        ):
            vip_info = dict(
                [
                    ("address", vs_name.get("ipv46")),
                    ("port", vs_name.get("port")),
                    ("protocol", "UDP" if vs_name.get("servicetype") == "UDP" else "TCP"),
                    ("loadbalancer", device.get("hostname")),
                    ("tags", device.get("tags")),
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
    NautobotClient(device)
