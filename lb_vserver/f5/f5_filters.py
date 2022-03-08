import os
from datetime import datetime
from helper.variables_lb import DISREGARD_LB_F5, F5_STANDALONE, DISREGARD_VIP, FILTER_VIP

F5_DEVICE_TO_QUERY = os.environ.get("RD_OPTION_DEVICES", "All")


def filter_device(device):
    if "All" in F5_DEVICE_TO_QUERY or device["hostname"] in F5_DEVICE_TO_QUERY:
        return True


def filter_device1(item):
    for i in enumerate(DISREGARD_LB_F5):
        if DISREGARD_LB_F5[i[0]] in item["hostname"]:
            return True


def filter_standalone(item):
    for i in enumerate(F5_STANDALONE):
        if F5_STANDALONE[i[0]] in item["hostname"]:
            return True


def filter_vips(addr, vip):
    if addr not in DISREGARD_VIP and vip.get("pool") and ("All" in FILTER_VIP or vip.get("name") in FILTER_VIP):
        return True


def nautobotday():
    days = [0, 1, 2]
    # if F5_DEVICE_TO_QUERY == "All" and datetime.today().weekday() in days:
    if datetime.today().weekday() in days:
        return True
