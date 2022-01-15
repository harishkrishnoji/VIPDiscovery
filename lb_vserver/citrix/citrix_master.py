# pylint: disable=W1203, C0103, W0631, C0301, W0703, R1710, W0125
"""Citrix Master."""

import os
import time
import json
from citrix.citrix_fun import pull_vip_info, pull_sgrp_info, pull_cert_info
from helper.local_helper import log, uploadfile, MongoDB
from helper.variables_lb import DISREGARD_VIP, NS_DEVICE_FIELDS, DISREGARD_LB_CITRIX, FILTER_VIP
from nautobot.nautobot_master import NautobotClient
import concurrent.futures

dbp = os.environ.get("RD_OPTION_DB_PWD")
dbu = os.environ.get("RD_OPTION_DB_USER")
dbh = os.environ.get("RD_OPTION_DB_HOST")
db = MongoDB(dbu, dbp, dbh)


def citrix_master(adm, tags, ENV):
    """Gather all NetScaler device list from ADM, run through filter.

    Args:
        adm (obj): ADM Instance.
        tags (lst): List of Tags associated for Nautobot object.
        ENV (str): Enviroment OFD, OFS.
    """
    log.debug("Master Citrix Initiated.. ")
    log.debug(f"Gather Device list for {ENV}..")
    with concurrent.futures.ThreadPoolExecutor() as executor:
        ns_info = ns_device_lst(adm)
        sas_vip_info = []
        filename = f"RUNDECK_{ENV}-{time.strftime('%m%d%Y-%H%M')}.json"
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
                    device["vips"] = gather_vip_info(device, adm, ENV)
                    sas_vip_info.extend(device["vips"])
                    executor.submit(db.vip_collection, device["vips"])
                executor.submit(NautobotClient, device)
        with open(filename, "w+") as json_file:
            json.dump(sas_vip_info, json_file, indent=4, separators=(",", ": "), sort_keys=True)
        resp = uploadfile(filename)
        log.info(resp.strip())
    log.info("Job done")


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
    vs_lst = pull_vip_info(device, adm).get("lbvserver", [])
    log.debug(f"{device.get('hostname')}: {len(vs_lst)} VIPs...")
    vip_lst = []

    def concurrent_vip(vs_name):
        """Get concurrent vips and return future object."""
        if (
            vs_name.get("name")
            and vs_name.get("ipv46") not in DISREGARD_VIP
            and ("All" in FILTER_VIP or vs_name.get("name") in FILTER_VIP)
        ):
            vip_info = dict(
                [
                    ("name", vs_name.get("name")),
                    ("address", vs_name.get("ipv46")),
                    ("port", vs_name.get("port")),
                    ("protocol", "UDP" if vs_name.get("servicetype") == "UDP" else "TCP"),
                    ("loadbalancer", device.get("hostname")),
                    ("tags", device.get("tags")),
                    ("environment", ENV),
                ]
            )
            pool_to_nautobot = pull_sgrp_info(vs_name, adm)
            if pool_to_nautobot:
                vip_info.update(pool_to_nautobot)
            if vs_name.get("servicetype") == "SSL" or vs_name.get("servicetype") == "SSL_TCP":
                cert_to_nautobot = pull_cert_info(vs_name, adm)
                if cert_to_nautobot:
                    vip_info["cert"] = cert_to_nautobot
            return vip_info

    with concurrent.futures.ThreadPoolExecutor() as vip_executor:
        results = [vip_executor.submit(concurrent_vip, vs_name) for vs_name in vs_lst]
    for f in concurrent.futures.as_completed(results):
        if f.result():
            vip_lst.append(f.result())
    return vip_lst
