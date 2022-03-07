import os
import json
from datetime import datetime
from helper.variables_lb import DISREGARD_VIP, DISREGARD_LB_CITRIX, FILTER_VIP, NS_DEVICE_TO_QUERY
from nautobot.nautobot_main import NautobotClient
from helper.local_helper import glab, log
from deepdiff import DeepDiff

# NS_DEVICE_TO_QUERY = os.environ.get("RD_OPTION_DEVICES", "All")
# ovips = glab.get_file()
ovips = json.loads(glab.get_file().decode())


def filter_device(device, ENV):
    if (
        device.get("environment") == ENV
        and device.get("hostname") not in DISREGARD_LB_CITRIX
        and ("All" in NS_DEVICE_TO_QUERY or device.get("hostname") in NS_DEVICE_TO_QUERY)
        and filter_HA_state(device)
    ):
        return True


def filter_HA_state(device):
    if (
        device.get("ha_master_state") == "Secondary"
        and device.get("instance_state") == "Up"
        and device.get("ipv4_address")
    ) or ("DEFRA1SLBSFA02A" in device["hostname"] and device["instance_state"] == "Up"):
        return True


def filter_vip(vs_name):
    if (
        vs_name.get("name")
        and vs_name.get("ipv46") not in DISREGARD_VIP
        and ("All" in FILTER_VIP or vs_name.get("name") in FILTER_VIP)
    ):
        return True


def nautobotday():
    days = [0, 2, 6]
    # if NS_DEVICE_TO_QUERY == "All" and datetime.today().weekday() in days:
    if datetime.today().weekday() in days:
        return True


def update_nautobot(device, env):
    if nautobotday():
        dev = diffObject(device)
        NautobotClient(dev)
                    
                    
def diffObject(device):
    nvips = device.get("vips")
    newdev = device.copy()
    newdev["vips"] = []
    log.info(f"New VIPs count : {len(nvips)}")
    log.info(f"Old VIPs count : {len(ovips)}")
    for nd in nvips:
        newvip = True
        for od in ovips:
            if (
                (od.get("port") == nd.get("port")) and od.get("protocol") == nd.get("protocol")
                and (od.get("address") == nd.get("address")) and (od.get("name") == nd.get("name"))
                and (od.get("pool") == nd.get("pool")) and (od.get("environment") == nd.get("environment"))
            ):
                if not DeepDiff(od, nd, ignore_order=True, exclude_paths=["root['loadbalancer']"]):
                    newvip = False
        if newvip:
            newdev["vips"].append(nd)
    log.info(f"After filter VIPs count : {len(newdev['vips'])}")
    return newdev
