# pylint: disable=W1203, C0103, W0631, C0301, W0703, R1710
"""Citrix Function."""

import json
import sys
from helper import log


class CITIRIX_FUN:
    """Gather NetScaler VIP Info."""

    def __init__(self, adm) -> None:
        """Initialize."""
        self.adm = adm
        self.vs_name = ""
        self.device = ""
        self.cert = ""
        self.NS_API_DATA = dict([("proxy_key", "_MPS_API_PROXY_MANAGED_INSTANCE_IP")])

    def pull_sgrp_info(self, vs_name):
        """Get ServiceGroup for given VServer."""
        try:
            self.vs_name = vs_name
            self.NS_API_DATA["path"] = f"config/lbvserver_servicegroupmember_binding/{self.vs_name.get('name')}"
            resp = self.adm.adm_api_call(**self.NS_API_DATA)
            if resp.status_code == 200 and "lbvserver_servicegroupmember_binding" in resp.text:
                jresp = json.loads(resp.text)
                servicegrp = jresp["lbvserver_servicegroupmember_binding"][0]["servicegroupname"]
                pool_mem = list(sgrp["ipv46"] for sgrp in jresp["lbvserver_servicegroupmember_binding"])
                return dict([("pool", servicegrp), ("pool_mem", pool_mem)])
        except Exception as err:
            log.error(f"{sys._getframe().f_code.co_name}: {self.vs_name.get('name')}: {err}")

    def pull_cert_info(self):
        """Get SSL Cert info for given VServer."""
        try:
            self.NS_API_DATA["path"] = f"config/sslvserver_binding/{self.vs_name.get('name')}"
            # log.info(self.NS_API_DATA)
            resp = self.adm.adm_api_call(**self.NS_API_DATA)
            self.cert = []
            if resp.status_code == 200 and "sslvserver_sslcertkey_binding" in resp.text:
                ssl_cert = json.loads(resp.text)["sslvserver_binding"][0]["sslvserver_sslcertkey_binding"]
                for sslcert in ssl_cert:
                    self.pull_ssl_key(sslcert)
                return self.cert
        except Exception as err:
            log.error(f"{sys._getframe().f_code.co_name}: {self.vs_name.get('name')}: {err}")

    def pull_ssl_key(self, sslcert):
        """Get SSL Key for each Cert."""
        # Get SSL Cert Info : serial number, issuer, expire etc
        self.NS_API_DATA["path"] = f"config/sslcertkey/{sslcert.get('certkeyname')}"
        resp = self.adm.adm_api_call(**self.NS_API_DATA)
        if resp.status_code == 200 and "sslcertkey" in resp.text:
            jresp = json.loads(resp.text)
            self.cert.append(self.cert_template(jresp, sslcert))

    def cert_template(self, data, sslcert):
        """SSL Certificate Template."""
        cert = dict(
            [
                ("cert_cn", data["sslcertkey"][0]["subject"].split("CN=", 1)[1]),
                ("cert_type", "CA" if sslcert.get("ca") is True else "SNI" if sslcert.get("snicert") is True else "",),
                ("cert_serial", data["sslcertkey"][0]["serial"]),
                ("cert_issuer", data["sslcertkey"][0]["issuer"]),
                ("cert_exp", data["sslcertkey"][0]["clientcertnotafter"]),
            ]
        )
        return cert

    def pull_vip_info(self, device):
        """Get list of VS for given LB instance."""
        self.device = device
        try:
            self.NS_API_DATA["path"] = "config/lbvserver?view=summary"
            self.NS_API_DATA["proxy_value"] = self.device.get("ipv4_address")
            resp = self.adm.adm_api_call(**self.NS_API_DATA)
            if resp.status_code == 200:
                return json.loads(resp.text)
        except Exception as err:
            log.error(f"{sys._getframe().f_code.co_name}: {device['hostname']}: {err}")
            return {}
