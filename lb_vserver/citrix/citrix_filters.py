import os
from datetime import datetime
from helper.variables_lb import DISREGARD_VIP, DISREGARD_LB_CITRIX, FILTER_VIP

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
