# pylint: disable=W1203, C0103, W0631, C0301, W0703, R1710
"""F5 Master."""

import os
import json
import requests
from helper.local_helper import log
from helper.variables_lb import DISREGARD_LB_F5, F5_STANDALONE, F5_DEVICE_FIELDS
from nautobot.nautobot_master import NautobotClient
from f5.f5_fun import F5HelperFun


def f5_master(f5, tags, ENV):
    """F5 Master.

    Check if device is not in DISREGAR_LB_F5 list and HA state to be standby.
    Pass the list to "F5HelperFun" Class to gather all VIP related details.

    Args:
        f5 (Class): F5 API Client.
        tags (list): Tag names.
        ENV (str): Device environment name.
    """
    log.debug("Master F5 Initiated.. ")
    log.debug(f"Gather Device list for {ENV}..")
    for item in device_list(f5):
        discard = False
        item["mgmt_address"] = item.pop("address")
        item["tags"] = tags
        item["type"] = "ltm"
        item["environment"] = ENV
        for i in enumerate(DISREGARD_LB_F5):
            if DISREGARD_LB_F5[i[0]] in item["hostname"]:
                discard = True
        if not discard and item.get("status") == "Active":
            ha_state = device_ha_state(f5, item)
            if ha_state == "active":
                item["ha_master_state"] = ha_state
            elif ha_state == "standby" or ha_state == "Standalone":
                item["ha_master_state"] = ha_state
                f5f = F5HelperFun(f5, item)
                if f5f.apidata:
                    item["vips"] = f5f.gather_vip_info()
                else:
                    log.error(f"{item['hostname']}: Gathering Pool and Cert info")
        NautobotClient(item)


def device_list(f5):
    """Get list of all devices from BIG-IQ.

    Args:
        f5 (class): F5 API Client.

    Returns:
        dict: Device data.
    """
    try:
        resp = f5.bigiq_api_call()
        jresp = json.loads(resp.text)
        log.debug(f"F5 Device count : {len(jresp.get('items'))}")
        device_info = []
        F5_DEVICE_TO_QUERY = os.environ.get("RD_OPTION_DEVICES", "All")
        for device in jresp["items"]:
            # For Test or Troubleshooting purpose
            # Filter the devices for which you want to discover VIPs
            if "All" in F5_DEVICE_TO_QUERY or device["hostname"] in F5_DEVICE_TO_QUERY:
                log.debug(f"{device['hostname']}")
                # Filter only the Fields/Keys which match F5_DEVICE_FIELDS
                device_info.append(dict((i, device[i]) for i in F5_DEVICE_FIELDS))
        return device_stats(f5, device_info)
    except Exception as err:
        log.error(f"{err}")


def device_ha_state(f5, item):
    """Get the HA state for given device.

    Args:
        f5 (class): F5 API Client.
        item (dict): Device info.

    Returns:
        str: Device HA State.
    """
    discard = False
    for i in enumerate(F5_STANDALONE):
        if F5_STANDALONE[i[0]] in item["hostname"]:
            item["status"] = "Standalone"
            discard = True
    if not discard:
        try:
            resp = f5.bigiq_api_call("GET", uuid=item["uuid"], path="/rest-proxy/mgmt/tm/sys/failover")
            return json.loads(resp.text)["apiRawValues"]["apiAnonymous"].split()[1]
        except requests.exceptions.HTTPError:
            log.error(f"Service Unavailable : {item['hostname']}")
        except Exception as err:
            log.error(f"{item['hostname']}: {err}")
    else:
        return "Standalone"


def device_stats(f5, f5_info):
    """Check if list of all devices from BIG-IQ are reachable from BIG-IQ.

    Args:
        f5 (class): F5 API Client.
        f5_info (dict): Device info.

    Returns:
        dict: updated f5_info
    """
    try:
        resp = f5.bigiq_api_call("GET", uuid="stats")
        jresp = json.loads(resp.text)
        for item in f5_info:
            svalue = f"https://localhost/mgmt/shared/resolver/device-groups/cm-bigip-allBigIpDevices/devices/{item['uuid']}/stats"
            if "unavailable" in str(jresp["entries"][svalue]["nestedStats"]["entries"]["health.summary"]):
                item["status"] = "Unreachable"
                log.error(f"Unreachable Device : {item['hostname']}")
            else:
                item["status"] = "Active"
        return f5_info
    except Exception as err:
        log.error(f"{item['hostname']}: {err}")
