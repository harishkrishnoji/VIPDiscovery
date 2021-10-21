import json
from datetime import datetime
from helper.script_conf import *


class nautobot_fun:
    def __init__(self, NB):
        self.NB = NB
        self.log = LOG("nautobot_fun")

    def write_data(self, vip_data):
        self.dport = vip_data.get("dport")
        self.vip_data = vip_data
        if self.vip_data.get("cert_cn") and self.vip_data.get("cert_exp"):
            dateformat = datetime.strptime(self.vip_data["cert_exp"], "%b %d %H:%M:%S %Y %Z")
            self.vip_data["cert_exp"] = dateformat.strftime("%Y-%m-%dT%H:%M:%SZ")
            self.vip_data["cert_issuer"] = self.vip_data["cert_issuer"][1:101]
        return self.main_worker()

    def main_worker(self):
        if all(x in list(self.vip_data) for x in VIP_FIELDS):
            # 1. Get or Create device (loadbalancer)
            #   1.1 Get or Create device-types
            #       1.1.1 Get - Manufacturer need to available
            #   1.2 Get or Create device_role
            #   1.3 Get or Create Site (Data dict need to be updated)
            #       1.3.1 Get or Create Region

            self.get_loadbalancer()
            if hasattr(self, "lb_uuid") is True:
                self.log.debug(f"VIP create / update / validate in process : {self.vip_data.get('name')} ...")
                self.get_tags()
                # 2. Get or Create or Update VIP
                #   2.1 Get or Create or Update pool
                #       2.1.1 Get or Create or Update pool member
                #           2.1.1.1 Get or Create IP address
                #   2.2 Get or Create partition (Optional)
                #   2.3 Get or Create Adv Policy (Optional)
                #   2.4 Get or Update Cert info (Optional)
                #   2.5 Get device UUID
                try:
                    self.get_partition()
                    self.get_environment()
                    self.get_vip()
                except:
                    self.log.error(f"Unable to create VIP : {self.vip_data.get('name')}")
                    self.log.warning("Going for Next VIP")
            else:
                self.log.error("LB UUID was not Found")
                self.log.warning("Going for Next VIP")
        else:
            self.log.error(
                f"Mandatory VIP Fields are missing : {VIP_FIELDS} : {dict((i,self.vip_data[i]) for i in self.vip_data if i!='ns_info')}"
            )
            self.log.warning("Going for Next VIP")

    ###########################################
    # IP Address related functions
    ###########################################
    def get_address(self, addr, create=False):
        obj = f"ipam/ip-addresses?address={addr}&tag={self.vip_data.get('tag')}"
        resp = self.get_api_call(obj)
        if resp["count"] >= 1:
            return resp["results"][0]["id"]
        elif create is True:
            return self.create_address(addr)

    def create_address(self, addr):
        obj = "ipam/ip-addresses/"
        data = dict([("address", addr), ("status", "active"), ("tags", [self.tagd])])
        resp = self.post_api_call(obj, **data)
        if resp:
            return resp["id"]
        return None

    ###########################################
    # Environment functions
    ###########################################
    def get_environment(self):
        obj = f"plugins/vip-tracker/environments/?name={self.vip_data.get('environment')}"
        resp = self.get_api_call(obj)
        if resp["count"] >= 1:
            self.env_uuid = resp["results"][0]["id"]
        else:
            self.create_environment()

    def create_environment(self):
        obj = "plugins/vip-tracker/environments/"
        data = dict([("name", self.vip_data.get("environment")), ("slug", self.vip_data.get("environment").lower())])
        resp = self.post_api_call(obj, **data)
        if resp:
            self.env_uuid = resp["id"]

    ###########################################
    # VIP related functions
    ###########################################

    def get_vip(self):
        self.tagd = dict([("name", self.vip_data.get("tag").upper()), ("slug", self.vip_data.get("tag").lower())])
        addr = self.get_address(self.vip_data.get("address"))
        if addr:
            obj = (
                f"plugins/vip-tracker/vip/?name={self.vip_data.get('name')}&loadbalancer={self.lb_uuid}"
                f"&address={addr}&port={self.vip_data.get('port')}"
            )
            resp = self.get_api_call(obj)
            if resp["count"] == 1:
                self.get_pool()
                self.vip_uuid = resp["results"][0]["id"]
                data = {}
                if self.vip_pool_uuid != resp["results"][0]["pool"]:
                    data["pool"] = self.vip_pool_uuid
                if self.vip_data.get("cert_cn"):
                    if self.vip_data.get("cert_cn") != resp["results"][0].get("cert_cn"):
                        data["cert_cn"] = self.vip_data.get("cert_cn")
                    if self.vip_data.get("cert_serial") != resp["results"][0].get("cert_serial"):
                        data["cert_serial"] = self.vip_data.get("cert_serial")
                    if self.vip_data.get("cert_issuer") != resp["results"][0].get("cert_issuer"):
                        data["cert_issuer"] = self.vip_data.get("cert_issuer")
                    if self.vip_data.get("cert_exp") != resp["results"][0].get("cert_exp"):
                        data["cert_exp"] = self.vip_data.get("cert_exp")
                if self.vip_data.get("environment") != resp["results"][0].get("environment"):
                    data["environment"] = self.env_uuid
                if data:
                    self.update_vip(**data)
                else:
                    self.log.debug(f"No change in VIP fields : {self.vip_data.get('name')}")
            else:
                self.create_vip()
        else:
            self.create_vip()

    def create_vip(self):
        if (vip_addr_uuid := self.get_address(self.vip_data.get("address"), True)) is not None:
            self.vip_addr_uuid = vip_addr_uuid
            self.get_pool()
            obj = "plugins/vip-tracker/vip/"
            data = dict(
                [
                    ("name", self.vip_data.get("name")),
                    ("port", self.vip_data.get("port")),
                    ("address", self.vip_addr_uuid),
                    ("pool", self.vip_pool_uuid),
                    ("cert_cn", self.vip_data.get("cert_cn", "")),
                    ("cert_serial", self.vip_data.get("cert_serial", "")),
                    ("cert_issuer", self.vip_data.get("cert_issuer", "")),
                    ("cert_exp", self.vip_data.get("cert_exp", "2000-01-01T00:00")),
                    ("loadbalancer", self.lb_uuid),
                    ("partition", self.partition_uuid),
                    ("environment", self.env_uuid),
                    ("advanced_policies", self.advp_uuid),
                ]
            )
            resp = self.post_api_call(obj, **data)
            if resp:
                self.log.debug("VIP created on Nautobot")
        else:
            self.log.error("Unable to create VIP UUID")

    def update_vip(self, **data):
        obj = f"plugins/vip-tracker/vip/{self.vip_uuid}/"
        if self.patch_api_call(obj, **data) == 200:
            self.log.debug("VIP updated on Nautobot")

    ###########################################
    # Pool related functions
    ###########################################

    def get_pool(self):
        self.get_pool_mem_addr()
        name = self.vip_data.get("pool")
        obj = f"plugins/vip-tracker/pools?name={name}"
        resp = self.get_api_call(obj)
        if resp["count"] >= 1:
            self.vip_pool_uuid = resp["results"][0]["id"]
            if resp["results"][0]["members"] != self.pool_mem_uuid:
                self.update_pool()
            else:
                self.log.debug(f"No change in Pool Members list : {name}")
        else:
            self.create_pool()

    def create_pool(self):
        obj = "plugins/vip-tracker/pools/"
        data = dict(
            [
                ("name", self.vip_data["pool"]),
                ("slug", self.vip_data["pool"].replace(".", "_").lower()),
                ("members", self.pool_mem_uuid),
            ]
        )
        resp = self.post_api_call(obj, **data)
        if resp:
            self.vip_pool_uuid = resp["id"]

    def update_pool(self):
        obj = f"plugins/vip-tracker/pools/{self.vip_pool_uuid}/"
        data = dict([("members", self.pool_mem_uuid)])
        if self.patch_api_call(obj, **data) == 200:
            self.log.debug("VIP Pool updated on Nautobot")

    ###########################################
    # Pool members related functions
    ###########################################

    def get_pool_mem_addr(self):
        self.pool_mem_parser()
        self.pool_mem_uuid = []
        for mem_info in self.pool_mem_info:
            obj = f"plugins/vip-tracker/members/?address={mem_info.get('uuid')}&name={mem_info.get('name')}"
            resp = self.get_api_call(obj)
            if resp["count"] >= 1:
                self.pool_mem_uuid.append(resp["results"][0]["id"])
            else:
                self.create_pool_mem_addr(mem_info)

    def create_pool_mem_addr(self, mem_info):
        port = 1
        if "1.1.1.1" in str(self.vip_data.get("pool_mem")):
            self.dport = self.dport + 1
            port = self.dport
            self.log.debug(self.dport)
        data = dict(
            [
                ("address", mem_info.get("uuid")),
                ("name", mem_info.get("name")),
                ("slug", mem_info.get("slug")),
                ("port", port),
                ("tags", [self.tagd]),
            ]
        )
        obj = "plugins/vip-tracker/members/"
        resp = self.post_api_call(obj, **data)
        if resp:
            self.pool_mem_uuid.append(resp["id"])
        else:
            self.log.error(f"Unable to create Pool Member : {mem_info}")

    ###########################################
    # Pool member parser from input data
    ###########################################

    def pool_mem_parser(self):
        def _parser(addr):
            return addr.replace(".", "_").replace("/", "_")

        self.pool_mem_info = []
        if isinstance(self.vip_data.get("pool_mem"), str):
            self.pool_mem_info.append(
                {
                    "uuid": self.get_address(self.vip_data.get("pool_mem"), True),
                    "slug": _parser(self.vip_data.get("pool_mem")),
                    "name": self.vip_data.get("pool_mem"),
                }
            )
        elif isinstance(self.vip_data.get("pool_mem"), list):
            for addr in self.vip_data.get("pool_mem"):
                if isinstance(addr, dict):
                    self.pool_mem_info.append(
                        {
                            "uuid": self.get_address(addr.get("address"), True),
                            "slug": _parser(addr.get("name")).lower(),
                            "name": addr.get("name"),
                        }
                    )
                else:
                    self.pool_mem_info.append(
                        {"uuid": self.get_address(addr, True), "slug": _parser(addr), "name": addr}
                    )

    ###########################################
    # Partition and Advance Policys
    ###########################################

    def get_partition(self):
        self.partition_uuid = ""
        self.advp_uuid = []
        if self.vip_data.get("partition"):
            obj = f"plugins/vip-tracker/partitions/?name={self.vip_data.get('partition')}"
            resp = self.get_api_call(obj)
            if resp["count"] >= 1:
                self.partition_uuid = resp["results"][0]["id"]
            else:
                self.create_partition()
            self.get_adv_policy()

    def create_partition(self):
        data = dict([("name", self.vip_data.get("partition")), ("slug", self.vip_data.get("partition").lower())])
        obj = "plugins/vip-tracker/partitions/"
        resp = self.post_api_call(obj, **data)
        self.partition_uuid = resp["id"]

    def get_adv_policy(self):
        for pol in self.vip_data.get("advanced_policies", []):
            obj = f"plugins/vip-tracker/policies/?name={pol}&partition={self.partition_uuid}"
            # obj = f"plugins/vip-tracker/policies/?name={pol}"
            resp = self.get_api_call(obj)
            if resp["count"] >= 1:
                self.advp_uuid.append(resp["results"][0]["id"])
            else:
                self.create_adv_policy(pol)

    def create_adv_policy(self, pol):
        data = dict(
            [
                ("name", pol),
                ("slug", pol.lower().replace("/", "_").replace(".", "_")),
                ("partition", self.partition_uuid),
            ]
        )
        obj = "plugins/vip-tracker/policies/"
        resp = self.post_api_call(obj, **data)
        if resp:
            self.advp_uuid.append(resp["id"])
        else:
            self.log.error(f"Unable to create Advance Policy : {data}")

    #################################
    # Device related functions
    #################################

    def get_loadbalancer(self):
        name = self.vip_data.get("loadbalancer")
        obj = f"dcim/devices/?name={name}" if name else "dcim/devices/"
        resp = self.get_api_call(obj)
        if resp["count"] == 1:
            self.lb_uuid = resp["results"][0]["id"]
        else:
            self.create_loadbalancer()

    def create_loadbalancer(self):
        self.get_device_type()
        if hasattr(self, "device_type_uuid") is True:
            self.get_device_role()
            if hasattr(self, "device_role_uuid") is True:
                self.get_site()
                if hasattr(self, "site_uuid") is True:
                    data = dict(
                        [
                            ("name", self.vip_data["loadbalancer"]),
                            ("device_type", self.device_type_uuid),
                            ("device_role", self.device_role_uuid),
                            ("site", self.site_uuid),
                            ("status", "active"),
                            ("custom_fields", {"internal_organization": "ofd"}),
                        ]
                    )
                    resp = self.post_api_call("dcim/devices/", **data)
                    if resp:
                        self.lb_uuid = resp["id"]

    def get_device_type(self):
        obj = f"dcim/device-types/?model={self.vip_data['ns_info'].get('type', 'netscaler')}"
        resp = self.get_api_call(obj)
        if resp["count"] == 1:
            self.device_type_uuid = resp["results"][0]["id"]
        else:
            self.create_device_type()

    def create_device_type(self):
        obj = "dcim/device-types/"
        model = self.vip_data["ns_info"].get("type").lower()
        data = dict([("manufacturer", self.get_manufacturers()), ("model", model), ("slug", model)])
        resp = self.post_api_call(obj, **data)
        if resp:
            self.device_type_uuid = resp["id"]

    def get_device_role(self):
        obj = "dcim/device-roles?name=load_balancer"
        resp = self.get_api_call(obj)
        if resp["count"] == 1:
            self.device_role_uuid = resp["results"][0]["id"]
        else:
            self.create_device_role()

    def create_device_role(self):
        obj = "dcim/device-roles/"
        resp = self.post_api_call(obj, **NAUTOBOT_DEVICE_ROLES["LB"])
        if resp:
            self.device_type_uuid = resp["id"]

    def get_tags(self):
        obj = f"extras/tags/?slug={self.vip_data.get('tag')}"
        resp = self.get_api_call(obj)
        if resp["count"] == 0:
            self.create_tags()

    def create_tags(self):
        obj = "extras/tags/"
        data = dict([("name", self.vip_data.get("tag").upper()), ("slug", self.vip_data.get("tag").lower())])
        self.post_api_call(obj, **data)

    #################################################
    # Site, Region and Manufacturer related functions
    #################################################

    def get_manufacturers(self):
        name = "f5" if "F5" in self.vip_data.get("environment") else "citrix"
        obj = f"dcim/manufacturers/?slug={name}"
        resp = self.get_api_call(obj)
        if resp["count"] == 1:
            return resp["results"][0]["id"]
        else:
            self.log.error(f"Manufacturer Not Found On Nautobot : {obj}")

    def get_site(self):
        def site(name):
            obj = f"dcim/sites/?slug={name.get('site')}"
            resp = self.get_api_call(obj)
            if resp["count"] == 1:
                self.site_uuid = resp["results"][0]["id"]
            else:
                self.create_site(name)

        self.lb_dkey = self.vip_data.get("loadbalancer")[:6]
        if self.lb_dkey in NAUTOBOT_DEVICE_REGION.keys():
            name = NAUTOBOT_DEVICE_REGION[self.lb_dkey]
            site(name)
        elif "Netscaler" in self.vip_data.get("environment"):
            octate = ".".join(self.vip_data["ns_info"].get("mgmt_ip_address").split(".", 2)[:2])
            if octate in NAUTOBOT_DEVICE_REGION_OFS.keys():
                name = NAUTOBOT_DEVICE_REGION_OFS[octate]
                site(name)
            else:
                site(NAUTOBOT_DEVICE_REGION.get("SANE_UNK"))
        elif "F5" in self.vip_data.get("environment"):
            octate = ".".join(self.vip_data["ns_info"].get("address").split(".", 2)[:2])
            if octate in NAUTOBOT_DEVICE_REGION_OFS.keys():
                name = NAUTOBOT_DEVICE_REGION_OFS[octate]
                site(name)
            else:
                site(NAUTOBOT_DEVICE_REGION.get("SANE_UNK"))

    def create_site(self, name):
        obj = "dcim/sites/"
        self.get_region(name)
        # name = NAUTOBOT_DEVICE_REGION[self.lb_dkey].get("site")
        data = dict(
            [
                ("name", name.get("site").upper()),
                ("slug", name.get("site").lower()),
                ("status", "active"),
                ("region", self.region_uuid),
                ("description", name.get("description", "")),
            ]
        )
        resp = self.post_api_call(obj, **data)
        if resp:
            self.site_uuid = resp["id"]

    def get_region(self, name):
        # name = NAUTOBOT_DEVICE_REGION[self.lb_dkey].get("region")
        obj = f"dcim/regions/?name={name.get('region')}"
        resp = self.get_api_call(obj)
        if resp["count"] == 1:
            self.region_uuid = resp["results"][0]["id"]
        else:
            self.create_region(name)

    def create_region(self, name):
        obj = "dcim/regions/"
        # name = NAUTOBOT_DEVICE_REGION[self.lb_dkey].get("region")
        data = dict([("name", name.get("region")), ("slug", name.get("region").replace(" ", "-").lower())])
        resp = self.post_api_call(obj, **data)
        if resp:
            self.region_uuid = resp["id"]

    #################################
    # GET, POST, PATCH API Function
    #################################

    def get_api_call(self, obj):
        try:
            resp = self.NB.nb_data("GET", obj, **{})
            if resp.status_code == 200:
                self.log.debug(f"GET Data obj={obj}, resp={resp.status_code} : {json.loads(resp.text)['count']}")
                return json.loads(resp.text)
            self.log.debug(f"GET Data obj={obj}, resp={resp.status_code}")
        except:
            self.log.error(f"Unable to GET obj={obj}")

    def patch_api_call(self, obj, **data):
        payload = {"data": data}
        try:
            resp = self.NB.nb_data("PATCH", obj, **payload)
            self.log.debug(f"PATCH Data obj={obj}, data={data}, resp={resp.status_code}")
            if resp.status_code == 200:
                return resp.status_code
            self.log.error(f"Unable to PATCH obj={obj}, data={data}, resp={resp.status_code} : {resp.text}")
        except:
            self.log.error(f"Unable to PATCH obj={obj}, data={data}")

    def post_api_call(self, obj, **data):
        payload = {"data": data}
        try:
            resp = self.NB.nb_data("POST", obj, **payload)
            self.log.debug(f"POST Data obj={obj}, data={data}, resp={resp.status_code}")
            if resp.status_code == 201:
                return json.loads(resp.text)
            self.log.error(f"Unable to POST obj={obj}, data={data}, resp={resp.status_code} : {resp.text}")
        except:
            self.log.error(f"Unable to POST obj={obj}, data={data}")
