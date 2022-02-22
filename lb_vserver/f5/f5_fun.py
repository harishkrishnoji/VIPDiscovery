# pylint: disable=W1203, C0103, W0631, C0301, W0703, R1710, R0902, E0602, R1702
"""F5 Function."""

import json
from helper.local_helper import log
from helper.variables_lb import DISREGARD_VIP, FILTER_VIP


class F5HelperFun:
    """Create a F5 Function client."""

    def __init__(self, f5, item):
        """Initialize the F5 Function client.

        Args:
            f5 (Class): F5 API Client.
            item (dict): LB related and UUID info.
        """
        self.log = log
        self.f5 = f5
        self.item = item
        self.pool_lst = dict()
        self.pool_info()
        self.ssl_profile = dict()
        self.cert_file_info()
        self.ssl_profile_info()

    def pool_info(self):
        """Get all pool info for specific device UUID."""
        uri = "/rest-proxy/mgmt/tm/ltm/pool/?expandSubcollections=true"
        resp = self.get_api_call(uri)
        if resp:
            for pool in resp:
                pool_m_lst = []
                for pool_mem in pool["membersReference"].get("items", []):
                    pool_m_lst.append(
                        {
                            "name": pool_mem.get("name").split(":")[0],
                            "address": self.pool_mem_addr(pool_mem.get("address")),
                            "port": self.pool_mem_port(pool_mem.get("name"))
                        }
                    )
                self.pool_lst.update({pool["name"]: pool_m_lst})
    
    def pool_mem_addr(self, addr):
        """Parse pool mem address. ex: "10.35.48.141%5"."""
        if "any6" in addr:
            return "1.1.1.1"
        else:
            return addr.split("%")[0]

    def pool_mem_port(self, addr):
        """Parse pool mem port. ex: "255.255.255.254:41003"."""
        return addr.split(":")[1]


    def ssl_profile_info(self):
        """Get all ssl profile info for specific device UUID."""
        uri = "/rest-proxy/mgmt/tm/ltm/profile/client-ssl"
        resp = self.get_api_call(uri)
        if resp and hasattr(self, "cert_file"):
            self.ssl_profile = {
                ssl_profile.get("name"): self.cert_file[ssl_profile.get("cert").split("/")[2]] for ssl_profile in resp
            }

    def cert_file_info(self):
        """Get all cert file info for specific device UUID."""
        uri = "/rest-proxy/mgmt/tm/sys/file/ssl-cert/"
        resp = self.get_api_call(uri)
        if resp:
            self.cert_file = {
                cert.get("name"): dict(
                    [
                        ("cert_exp", cert.get("expirationString")),
                        ("cert_issuer", cert.get("issuer")),
                        ("cert_serial", cert.get("serialNumber")),
                        (
                            "cert_cn",
                            cert.get("subject").split("CN=")[1].split(",")[0]
                            if len(cert.get("subject").split("CN=")) > 1
                            else "",
                        ),
                    ]
                )
                for cert in resp
            }

    def gather_vip_info(self):
        """Get all VIP info for specific device UUID.

        Returns:
            dict: VIP info.
        """
        log.debug("Gathering VIP Info..")
        uri = "/rest-proxy/mgmt/tm/ltm/virtual?expandSubcollections=true"
        resp = self.get_api_call(uri)
        if not resp:
            uri = "/rest-proxy/mgmt/tm/ltm/virtual"
            resp = self.get_api_call(uri)
        vip_lst = []
        if resp:
            self.log.debug(f"[{len(resp)}] VIPs...")
            for vip in resp:
                try:
                    vip_info = self.vip_info_parser(vip)
                    if vip_info:
                        vip_lst.append(vip_info)
                except Exception as e:
                    self.log.error(f"[{self.item.get('hostname')}] {vip.get('name')} : {e}")
        return vip_lst

    def vip_info_parser(self, vip):
        """VIP info parser and data constructor."""
        if vip.get("destination") != ":0":
            addr = vip.get("destination").split("/")[2].split(":")[0]
            port = vip.get("destination").split("/")[2].split(":")[1]
            if "%" in vip.get("destination"):
                addr = vip.get("destination").split("/")[2].split("%")[0]
                port = vip.get("destination").split("/")[2].split("%")[1].split(":")[1]
            # Filter for VIPs which need to be discarded (DISREGARD_VIP) ex: '1.1.1.1'.
            # For Testing and Troubleshooting, filter specific VIP (FILTER_VIP).
            if (
                addr not in DISREGARD_VIP
                and vip.get("pool")
                and ("All" in FILTER_VIP or vip.get("name") in FILTER_VIP)
            ):
                vip_info = self.vip_dict_format(vip, addr, port)
                if vip.get("subPath"):
                    vip_info["partition"] = f'{vip.get("partition")}_{vip.get("subPath")}'
                    if "/Common/" not in vip.get("pool"):
                        vip_info["pool"] = vip.get("pool").split("/")[3]
                vip_info["pool_mem"] = self.pool_lst.get(vip_info["pool"])
                if vip["profilesReference"].get("items"):
                    vip_info["cert"] = []
                    for i in vip["profilesReference"].get("items"):
                        vip_info["advanced_policies"].append(i["name"])
                        if "clientside" in i["context"] and self.ssl_profile.get(i["name"]):
                            vip_info["cert"].append(self.ssl_profile.get(i["name"]))
                if not vip_info.get("advanced_policies"):
                    vip_info.pop("advanced_policies")
                if not vip_info.get("cert"):
                    vip_info.pop("cert")  
                return vip_info

    def vip_dict_format(self, vip, addr, port):
        """VIP data dictionary format."""
        return dict(        
            [
                ("name", vip.get("name")),
                ("address", addr),
                ("pool", vip.get("pool").split("/")[2]),
                ("partition", vip.get("partition")),
                ("advanced_policies", vip.get("rules", [])),
                ("port", "1" if port == "0" else port),
                ("loadbalancer", self.item.get("hostname")),
                ("loadbalancer_address", self.item.get("mgmt_address", "")),
                ("protocol", "UDP" if vip.get("ipProtocol") == "udp" else "TCP"),
                ("environment", self.item.get("environment")),
                ("tags", self.item.get("tags")),
            ]
        )


    def get_api_call(self, uri):
        """Get API call function."""
        try:
            log.debug(f"[{self.item.get('hostname')}] GET API {self.item.get('uuid')}:{uri}")
            resp = self.f5.bigiq_api_call("GET", self.item.get("uuid"), uri)
            if resp.status_code == 200 and json.loads(resp.text).get("items"):
                return json.loads(resp.text)["items"]
        except Exception:
            log.error(f"[{self.item.get('hostname')}] GET API Server Error {uri}")
