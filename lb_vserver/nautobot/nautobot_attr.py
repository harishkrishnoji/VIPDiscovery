# pylint: disable=W1203, C0103, W0631, W0703
"""Nautobot REST API SDK."""

import os
import requests
import pynautobot
from helper.local_helper import get_nb_keys

requests.urllib3.disable_warnings()


# fmt: off
class NBLogIn:
    url                     = os.environ.get("RD_OPTION_NAUTOBOT_URL")
    token                   = get_nb_keys(url)
    nb                      = pynautobot.api(url, token=token, threading=True)
    nb.http_session.verify  = False


class Device_ATTR(NBLogIn):
    plugins_attr            = getattr(NBLogIn.nb, "plugins")
    extras_attr             = getattr(NBLogIn.nb, "extras")
    dcim_attr               = getattr(NBLogIn.nb, "dcim")
    ipam_attr               = getattr(NBLogIn.nb, "ipam")
    tags_attr               = getattr(extras_attr, "tags")
    ip_addresses_attr       = getattr(ipam_attr, "ip-addresses")
    interfaces_attr         = getattr(dcim_attr, "interfaces")
    sites_attr              = getattr(dcim_attr, "sites")
    devices_attr            = getattr(dcim_attr, "devices")
    device_types_attr       = getattr(dcim_attr, "device-types")
    device_roles_attr       = getattr(dcim_attr, "device-roles")
    manufacturers_attr      = getattr(dcim_attr, "manufacturers")
    regions_attr            = getattr(dcim_attr, "regions")
    platforms_attr          = getattr(dcim_attr, "platforms")


class VIPT_ATTR(Device_ATTR):
    vip_tracker_attr        = getattr(Device_ATTR.plugins_attr, "vip-tracker")
    vip_attr                = getattr(vip_tracker_attr, "vip")
    vip_detail_attr         = getattr(vip_tracker_attr, "vip-detail")
    certificates_attr       = getattr(vip_tracker_attr, "certificates")
    environments_attr       = getattr(vip_tracker_attr, "environments")
    issuer_attr             = getattr(vip_tracker_attr, "issuer")
    members_attr            = getattr(vip_tracker_attr, "members")
    organization_attr       = getattr(vip_tracker_attr, "organization")
    partitions_attr         = getattr(vip_tracker_attr, "partitions")
    policies_attr           = getattr(vip_tracker_attr, "policies")
    pools_attr              = getattr(vip_tracker_attr, "pools")
# fmt: on
