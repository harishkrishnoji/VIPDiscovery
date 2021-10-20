import json
from helper.script_conf import *

log = LOG("citrix_fun")


def pull_sgrp_info(vs_name, adm):
    # Get ServiceGroup
    NS_API_DATA["path"] = f"config/lbvserver_servicegroupmember_binding/{vs_name.get('name')}"
    resp = adm.adm_api_call(**NS_API_DATA)
    if resp.status_code == 200 and "lbvserver_servicegroupmember_binding" in resp.text:
        # Get ServiceGroup Members
        jresp = json.loads(resp.text)
        servicegrp = jresp["lbvserver_servicegroupmember_binding"][0]["servicegroupname"]
        pool_mem = list(sgrp["ipv46"] for sgrp in jresp["lbvserver_servicegroupmember_binding"])
        return dict([("name", vs_name["name"]), ("pool", servicegrp), ("pool_mem", pool_mem)])


def pull_cert_info(vs_name, adm):
    # Get SSL Profile Info for VIP
    NS_API_DATA["path"] = f"config/sslvserver_binding/{vs_name.get('name')}"
    resp2 = adm.adm_api_call(**NS_API_DATA)
    if resp2.status_code == 200 and "sslvserver_sslcertkey_binding" in resp2.text:
        ssl_cert = json.loads(resp2.text)["sslvserver_binding"][0]["sslvserver_sslcertkey_binding"]
        cert_cn = []
        cert_issuer = []
        cert_serial = []
        for i in ssl_cert:
            # Get SSL Cert Info : serial number, issuer, expire etc
            NS_API_DATA["path"] = f"config/sslcertkey/{i.get('certkeyname')}"
            resp3 = adm.adm_api_call(**NS_API_DATA)
            jresp3 = json.loads(resp3.text)
            cert_cn.append(jresp3["sslcertkey"][0]["subject"].split("CN=", 1)[1])
            cert_issuer.append(jresp3["sslcertkey"][0]["issuer"])
            cert_serial.append(jresp3["sslcertkey"][0]["serial"])

        return dict(
            [
                ("cert_cn", ",".join(cert_cn)),
                ("cert_type", "CA" if i.get("ca") is True else "SNI" if i.get("snicert") is True else ""),
                ("cert_serial", ",".join(cert_serial)),
                ("cert_issuer", ",".join(cert_issuer)),
                ("cert_exp", jresp3["sslcertkey"][0]["clientcertnotafter"]),
            ]
        )


def pull_vip_info(device, adm):
    # Get NS VIP API Call
    NS_API_DATA["path"] = "config/lbvserver?view=summary"
    NS_API_DATA["proxy_value"] = device["ipv4_address"]
    resp = adm.adm_api_call(**NS_API_DATA)
    log.info(f"{device['hostname']}: NS VIP list Status code : {resp.status_code}")
    if resp.status_code == 200:
        return json.loads(resp.text)
    return {}
