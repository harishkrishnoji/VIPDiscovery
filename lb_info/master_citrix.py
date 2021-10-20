from helper.nautobot_fun import nautobot_fun
from helper.script_conf import *
from helper.citrix_fun import *

log = LOG("master_citrix")


def citrix_master(adm, NB, ENV):
    ns_info = ns_device_lst(adm)
    # Get NS VIP details
    for device in ns_info:
        # Filter to look for Standby,NON OFS, and Standalone
        var = device["ha_ip_address"].startswith("10.") or device["ha_ip_address"].startswith("167.")
        if "OFS_Netscaler" in ENV:
            var = device["ha_ip_address"].startswith("11.")
            device["ipv4_address"] = device["ipv4_address"].replace("10", "11", 1)
        if (
            f"{var} is True and (device['hostname'] not in DISREGARD_LB_CITRIX)) and "
            "((device['ha_master_state'] == 'Secondary' and device['instance_state'] == 'Up' and device['ipv4_address'] != '') or "
            "('DEFRA1SLBSFA02A' in device['hostname'] and device['instance_state'] == 'Up')"
        ):
            gather_vip_info(device, adm, NB, ENV)


def ns_device_lst(adm):
    # Get NS Device list
    resp = adm.adm_api_call()
    log.debug(f"NS Device list Status code : {resp.status_code}")
    jresp = json.loads(resp.text)
    return list(dict((i, j[i]) for i in NS_DEVICE) for j in jresp["ns"])


def gather_vip_info(device, adm, NB, ENV):
    vs_lst = pull_vip_info(device, adm).get("lbvserver", [])
    count = 0
    for vs_name in vs_lst:
        if vs_name.get("name") and vs_name.get("ipv46") not in DISREGARD_VIP:
            vip_to_nautobot = dict(
                [
                    ("address", vs_name.get("ipv46")),
                    ("port", vs_name.get("port")),
                    ("loadbalancer", device.get("hostname")),
                    ("ns_info", device),
                    ("tag", "ofd"),
                    ("environment", ENV),
                ]
            )
            if (pool_to_nautobot := pull_sgrp_info(vs_name, adm)) is not None:
                vip_to_nautobot.update(pool_to_nautobot)
            if vs_name.get("servicetype") == "SSL" or vs_name.get("servicetype") == "SSL_TCP":
                if (cert_to_nautobot := pull_cert_info(vs_name, adm)) is not None:
                    vip_to_nautobot.update(cert_to_nautobot)
            if count % 10 == 0 or count == 0:
                log.info(f"[{len(vs_lst)-count}/{len(vs_lst)}] VIPs...")
            nbf = nautobot_fun(NB)
            nbf.write_data(vip_to_nautobot)
            count += 1
