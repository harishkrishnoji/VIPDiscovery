# pylint: disable=W1203, C0103, W0631, W0703
"""Nautobot Master."""

from nautobot.nautobot_device import NB_Device
from nautobot.nautobot_vip_tracker import LB_VIP
from helper import log


def NautobotClient(lb_data):
    """Nautobot Object create function.

    Args:
        lb_data (dict): LB Data.
    """
    device_data = lb_data.copy()
    device_data.pop("vips", "")
    device = NB_Device(device_data)
    device.device()
    if device.device_uuid:
        for vip in lb_data.get("vips"):
            try:
                vip_object = LB_VIP(vip, device.device_uuid, device.tag_uuid)
                vip_object.main_fun()
            except Exception as err:
                log.error(f"[VIP] {vip.get('name')} : {err}")
