import os
from datetime import datetime
from helper.variables_lb import DISREGARD_VIP, DISREGARD_LB_CITRIX, FILTER_VIP
from nautobot.nautobot_main import NautobotClient
from helper.local_helper import glab
from deepdiff import DeepDiff

NS_DEVICE_TO_QUERY = os.environ.get("RD_OPTION_DEVICES", "All")


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
    days = [0, 2]
    if NS_DEVICE_TO_QUERY == "All" and datetime.today().weekday() in days:
        return True


def update_nautobot(devices, env):
    if nautobotday():
        glab.filepath = f"lb-vip/{env}.json"
        ofile = glab.get_file()
        for device in devices:
            if device.get("vips"):
                dev = diffObject(ofile, device)
                NautobotClient(dev)
                # for vip in device.get("vips"):
                    
                    
def diffObject(ofile, device):
    device_data = device.copy()
    vips = device.get("vips")
    print(len(vips))
    for of in ofile:
        for i, vip in enumerate(vips):
            if vip == of:
                del(vips[i])

'''
a = [1,23,4,5,6,7,4,2,1,45]
b = [2,3,4,5,6,7,8,9,45,23]
for ai1, ai in enumerate(a):
    for bi1, bi in enumerate(b):
        if ai == bi:
            print(str(ai), str(bi))
            print(str(ai1), str(bi1))
            del(a[ai1])

'''