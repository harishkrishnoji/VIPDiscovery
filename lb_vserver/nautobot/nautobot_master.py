# pylint: disable=W1203, C0103, W0631, W0703
"""Nautobot Master."""

from nautobot.nautobot_fun import LB_DEVICE, LB_VIP
from helper.local_helper import log


def NautobotClient(lb_data):
    """Nautobot Object create function.

    Args:
        lb_data (dict): LB Data.
    """
    device_data = lb_data.copy()
    device_data.pop("vips", "")
    log.info(f"[Device] Updated {lb_data.get('hostname')} : {len(lb_data.get('vips', []))}")
    device = LB_DEVICE(device_data)
    device.device()
    loadbalancer_uuid = device.loadbalancer_uuid
    tag_uuid = device.tag_uuid
    for vip in lb_data.get("vips", []):
        try:
            vip_object = LB_VIP(vip, loadbalancer_uuid, tag_uuid)
            vip_object.main_fun()
        except Exception as err:
            log.error(f"[VIP] {vip.get('name')} : {err}")