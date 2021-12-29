import json
from helper.script_conf import *


class F5HelperFun:
    def __init__(self, f5, item):
        self.log = LOG("f5_fun")
        self.f5 = f5
        self.apidata = True
        self.item = item
        self.dport = 10
        self.log.debug("Gathering Pool member info...")
        self.pool_info()
        self.log.debug("Gathering Cert File info...")
        self.cert_file_info()
        self.log.debug("Gathering SSL Profile info...")
        self.ssl_profile_info()

    def pool_info(self):
        resp = self.f5.bigiq_api_call(
            "GET", self.item.get("uuid"), "/rest-proxy/mgmt/tm/ltm/pool/?expandSubcollections=true"
        )
        if resp.status_code == 200 and json.loads(resp.text).get("items"):
            self.pool_lst = {}
            for pool in json.loads(resp.text)["items"]:
                if pool["membersReference"].get("items"):
                    pool_m_lst = [
                        dict(
                            [
                                ("name", pool_mem.get("name").split(":")[0]),
                                (
                                    "address",
                                    "1.1.1.1"
                                    if "any6" in pool_mem.get("address")
                                    else pool_mem.get("address").split("%")[0],
                                ),
                            ]
                        )
                        for pool_mem in pool["membersReference"].get("items")
                    ]
                    self.pool_lst.update({pool["name"]: pool_m_lst})
        else:
            self.apidata = False

    def ssl_profile_info(self):
        resp = self.f5.bigiq_api_call("GET", self.item.get("uuid"), "/rest-proxy/mgmt/tm/ltm/profile/client-ssl")
        if resp.status_code == 200 and json.loads(resp.text).get("items"):
            self.ssl_profile = {
                ssl_profile.get("name"): self.cert_file[ssl_profile.get("cert").split("/")[2]]
                for ssl_profile in json.loads(resp.text)["items"]
            }
        else:
            self.apidata = False

    def cert_file_info(self):
        resp = self.f5.bigiq_api_call("GET", self.item.get("uuid"), "/rest-proxy/mgmt/tm/sys/file/ssl-cert/")
        if resp.status_code == 200 and json.loads(resp.text).get("items"):
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
                for cert in json.loads(resp.text)["items"]
            }
        else:
            self.apidata = False

    def gather_vip_info(self):
        resp = self.f5.bigiq_api_call(
            "GET", self.item.get("uuid"), "/rest-proxy/mgmt/tm/ltm/virtual?expandSubcollections=true"
        )
        vip_lst = []
        if resp.status_code == 200 and json.loads(resp.text).get("items"):
            vs_lst = json.loads(resp.text)["items"]
            self.log.debug(f"[{len(vs_lst)}] VIPs...")
            for vip in vs_lst:
                try:
                    if vip.get("destination") not in DISREGARD_VIP and vip.get("pool"):
                        addr = vip.get("destination").split("/")[2].split(":")[0]
                        port = vip.get("destination").split("/")[2].split(":")[1]
                        if "%" in vip.get("destination"):
                            addr = vip.get("destination").split("/")[2].split("%")[0]
                            port = vip.get("destination").split("/")[2].split("%")[1].split(":")[1]
                        vip_info = dict(
                            [
                                ("name", vip.get("name")),
                                ("address", addr),
                                ("pool", vip.get("pool").split("/")[2]),
                                ("partition", vip.get("partition")),
                                ("advanced_policies", vip.get("rules", [])),
                                ("port", "1" if port == "0" else port),
                                ("loadbalancer", self.item.get("hostname")),
                                ("protocol", "UDP" if vip.get("ipProtocol") == "udp" else "TCP"),
                                ("environment", self.item.get("environment")),
                                ("tags", self.item.get("tags")),
                            ]
                        )
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

                        self.log.debug(vip_info)
                        if "1.1.1.1" in str(vip_info.get("pool_mem")):
                            self.dport += 5
                            vip_info["dport"] = self.dport
                        vip_lst.append(vip_info)
                except Exception as e:
                    self.log.error(f"[{vip.get('name')}]: {e}")
        elif resp.status_code != 200:
            self.log.error(f"[{self.item.get('hostname')}]: [{resp.status_code}] virtual")
        return vip_lst
