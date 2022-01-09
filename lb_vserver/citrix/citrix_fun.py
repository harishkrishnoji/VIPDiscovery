# pylint: disable=W1203, C0103, W0631, C0301, W0703, R1710
"""Citrix Function."""

import json
from helper.local_helper import log

NS_API_DATA = dict([("proxy_key", "_MPS_API_PROXY_MANAGED_INSTANCE_IP")])


def pull_sgrp_info(vs_name, adm):
    """Get ServiceGroup for given VServer.

    Args:
        vs_name (str): Virtual server name.
        adm (Class): ADM Class.

    Returns:
        dict: Return dictionary with VServer, pool and pool members.
    """
    try:
        NS_API_DATA["path"] = f"config/lbvserver_servicegroupmember_binding/{vs_name.get('name')}"
        resp = adm.adm_api_call(**NS_API_DATA)
        if resp.status_code == 200 and "lbvserver_servicegroupmember_binding" in resp.text:
            jresp = json.loads(resp.text)
            servicegrp = jresp["lbvserver_servicegroupmember_binding"][0]["servicegroupname"]
            pool_mem = list(sgrp["ipv46"] for sgrp in jresp["lbvserver_servicegroupmember_binding"])
            return dict([("name", vs_name["name"]), ("pool", servicegrp), ("pool_mem", pool_mem)])
    except Exception as err:
        log.error(f"{vs_name.get('name')}: {err}")


def pull_cert_info(vs_name, adm):
    """Get SSL Cert info for given VServer.

    Args:
        vs_name (str): Virtual server name.
        adm (Class): ADM Class.

    Returns:
        dict: Return dictionary with Cert CN, Cert serial, issuer, and expiration data.
    """
    try:
        NS_API_DATA["path"] = f"config/sslvserver_binding/{vs_name.get('name')}"
        resp = adm.adm_api_call(**NS_API_DATA)
        cert = []
        if resp.status_code == 200 and "sslvserver_sslcertkey_binding" in resp.text:
            ssl_cert = json.loads(resp.text)["sslvserver_binding"][0]["sslvserver_sslcertkey_binding"]
            for i in ssl_cert:
                # Get SSL Cert Info : serial number, issuer, expire etc
                NS_API_DATA["path"] = f"config/sslcertkey/{i.get('certkeyname')}"
                resp3 = adm.adm_api_call(**NS_API_DATA)
                if resp3.status_code == 200 and "sslcertkey" in resp.text:
                    jresp3 = json.loads(resp3.text)
                    cert.append(
                        dict(
                            [
                                ("cert_cn", jresp3["sslcertkey"][0]["subject"].split("CN=", 1)[1]),
                                (
                                    "cert_type",
                                    "CA" if i.get("ca") is True else "SNI" if i.get("snicert") is True else "",
                                ),
                                ("cert_serial", jresp3["sslcertkey"][0]["serial"]),
                                ("cert_issuer", jresp3["sslcertkey"][0]["issuer"]),
                                ("cert_exp", jresp3["sslcertkey"][0]["clientcertnotafter"]),
                            ]
                        )
                    )
            return cert
    except Exception as err:
        log.error(f"{vs_name.get('name')}: {err}")


def pull_vip_info(device, adm):
    """Get list of VS for given LB instance.

    Args:
        device (str): LB instance.
        adm (Class): ADM Class.

    Returns:
        list: Return list of VServer.
    """
    try:
        NS_API_DATA["path"] = "config/lbvserver?view=summary"
        NS_API_DATA["proxy_value"] = device["ipv4_address"]
        resp = adm.adm_api_call(**NS_API_DATA)
        if resp.status_code == 200:
            log.info(f"{device['hostname']}")
            return json.loads(resp.text)
    except Exception as err:
        log.error(f"{device['hostname']}: {err}")
        return {}
