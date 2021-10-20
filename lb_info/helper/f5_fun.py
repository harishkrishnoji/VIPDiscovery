import json
from helper.script_conf import *
from helper.nautobot_fun import nautobot_fun


class F5HelperFun:
    def __init__(self, f5, item, ENV):
        self.log = LOG("f5_fun")
        self.f5 = f5
        self.uuid = item["uuid"]
        self.item = item
        self.env = ENV
        self.log.info("Gathering Pool member info...")
        self.pool_info()
        self.log.info("Gathering Cert File info...")
        self.cert_file_info()
        self.log.info("Gathering SSL Profile info...")
        self.ssl_profile_info()

    def pool_info(self):
        resp = self.f5.bigiq_api_call("GET", self.uuid, "/rest-proxy/mgmt/tm/ltm/pool/?expandSubcollections=true")
        if resp.status_code == 200 and json.loads(resp.text).get("items"):
            self.pool_lst = {}
            for pool in json.loads(resp.text)["items"]:
                if pool["membersReference"].get("items"):
                    pool_m_lst = [
                        dict(
                            [
                                ("name", pool_mem.get("name").split(":")[0]),
                                ("address", pool_mem.get("address").split("%")[0]),
                            ]
                        )
                        for pool_mem in pool["membersReference"].get("items")
                    ]
                    self.pool_lst.update({pool["name"]: pool_m_lst})

    def ssl_profile_info(self):
        resp = self.f5.bigiq_api_call("GET", self.uuid, "/rest-proxy/mgmt/tm/ltm/profile/client-ssl")
        if resp.status_code == 200 and json.loads(resp.text).get("items"):
            self.ssl_profile = {
                ssl_profile.get("name"): self.cert_file[ssl_profile.get("cert").split("/")[2]]
                for ssl_profile in json.loads(resp.text)["items"]
            }

    def cert_file_info(self):
        resp = self.f5.bigiq_api_call("GET", self.uuid, "/rest-proxy/mgmt/tm/sys/file/ssl-cert/")
        if resp.status_code == 200 and json.loads(resp.text).get("items"):
            self.cert_file = {
                cert.get("name"): dict(
                    [
                        ("cert_exp", cert.get("expirationString")),
                        ("cert_issuer", cert.get("issuer")),
                        ("cert_serial", cert.get("serialNumber")),
                        ("cert_cn", cert.get("subject").split("CN=")[1].split(",")[0]),
                    ]
                )
                for cert in json.loads(resp.text)["items"]
            }
            self.log.debug(self.cert_file)

    def gather_vip_info(self, NB):
        self.log.info("Pulling VIP Info from Standby...")
        resp = self.f5.bigiq_api_call("GET", self.uuid, "/rest-proxy/mgmt/tm/ltm/virtual?expandSubcollections=true")
        if resp.status_code == 200 and json.loads(resp.text).get("items"):
            vs_lst = json.loads(resp.text)["items"]
            count = 0
            for vip in vs_lst:
                if vip.get("destination") not in DISREGARD_VIP and vip.get("pool"):
                    addr = vip.get("destination").split("/")[2].split(":")[0]
                    port = vip.get("destination").split("/")[2].split(":")[1]
                    if "%" in vip.get("destination"):
                        addr = vip.get("destination").split("/")[2].split("%")[0]
                        port = vip.get("destination").split("/")[2].split("%")[1].split(":")[1]
                    vip_to_nautobot = dict(
                        [
                            ("name", vip.get("name")),
                            ("address", addr),
                            ("pool_mem", self.pool_lst.get(vip.get("pool").split("/")[2])),
                            ("partition", vip.get("partition")),
                            ("advanced_policies", vip.get("rules", [])),
                            ("port", port),
                            ("pool", vip.get("pool").split("/")[2]),
                            ("loadbalancer", self.item["hostname"]),
                            ("tag", "ofd"),
                            ("environment", self.env),
                            ("ns_info", self.item),
                        ]
                    )
                    if vip.get("subPath"):
                        vip_to_nautobot["partition"] = f'{vip.get("partition")}_{vip.get("subPath")}'
                        vip_to_nautobot["pool"] = vip.get("pool").split("/")[3]
                        vip_to_nautobot["pool_mem"] = self.pool_lst.get(vip_to_nautobot["pool"])

                    if vip["profilesReference"].get("items"):
                        for i in vip["profilesReference"].get("items"):
                            vip_to_nautobot["advanced_policies"].append(i["name"])
                            if "clientside" in i["context"]:
                                vip_to_nautobot.update(self.ssl_profile[i["name"]])

                    if count % 10 == 0 or count == 0:
                        self.log.info(f"[{len(vs_lst)-count}/{len(vs_lst)}] VIPs...")

                    self.log.debug(vip_to_nautobot)
                    nbf = nautobot_fun(NB)
                    nbf.write_data(vip_to_nautobot)
                    count += 1
