"""Citrix Filters."""

import os
from helper.variables_lb import DISREGARD_VIP, DISREGARD_LB_CITRIX, FILTER_VIP
from helper import deviceToQuery


def filter_device(device, ENV):
    """Device filters."""
    if (
        device.get("environment") == ENV
        and device.get("hostname") not in DISREGARD_LB_CITRIX
        and ("All" in deviceToQuery or device.get("hostname") in deviceToQuery)
        and filter_HA_state(device)
    ):
        return True


def filter_HA_state(device):
    """Device HA state filters."""
    if (
        device.get("ha_master_state") == "Secondary"
        and device.get("instance_state") == "Up"
        and device.get("ipv4_address")
    ) or ("DEFRA1SLBSFA02A" in device["hostname"] and device["instance_state"] == "Up"):
        return True


def filter_vip(vs_name):
    """VIP filters."""
    if (
        vs_name.get("name")
        and vs_name.get("ipv46") not in DISREGARD_VIP
        and ("All" in FILTER_VIP or vs_name.get("name") in FILTER_VIP)
    ):
        return True
