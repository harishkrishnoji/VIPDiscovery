"""F5 filter functions."""

from helper.variables_lb import DISREGARD_LB_F5, F5_STANDALONE, DISREGARD_VIP, FILTER_VIP
from helper import deviceToQuery


def filter_device(device):
    """Device filter."""
    if "All" in deviceToQuery or device["hostname"] in deviceToQuery:
        return True


def filter_device1(item):
    """Device filter."""
    for i in enumerate(DISREGARD_LB_F5):
        if DISREGARD_LB_F5[i[0]] in item["hostname"]:
            return True


def filter_standalone(item):
    """Device filter."""
    for i in enumerate(F5_STANDALONE):
        if F5_STANDALONE[i[0]] in item["hostname"]:
            return True


def filter_vips(addr, vip):
    """VIP filters."""
    if addr not in DISREGARD_VIP and vip.get("pool") and ("All" in FILTER_VIP or vip.get("name") in FILTER_VIP):
        return True
