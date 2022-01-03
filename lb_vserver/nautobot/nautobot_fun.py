# pylint: disable=W1203, C0103, W0631, W0703, R1710, R0902, W0201, C0201, R1705, R0904
"""Nautobot Function."""

import json
from datetime import datetime
from helper.script_conf import (
    log,
    VIP_FIELDS,
    NAUTOBOT_DEVICE_REGION,
    NAUTOBOT_DEVICE_ROLES,
    NAUTOBOT_DEVICE_REGION_OFS,
)


class nautobot_fun:
    """Create a Nautobot Function client."""

    def __init__(self, NB, lb_uuid=False):
        """Initialize Nautobot Function Client.

        Args:
            NB (Class): Nautobot API Client
            lb_uuid (bool, optional): Create Loadbalancer in Nautobot Device module. Defaults to False.
        """
        self.NB = NB
        self.log = log
        self.lb_uuid = lb_uuid

    def main_fun(self, vip_data):
        """Main Function.

        Main function which will be initiated from nautobot_master.
        VIP could can have more than one Cert (SNI), so cert is list.

        Args:
            vip_data (dict): Single VIP related info.
        """
        self.vip_data = vip_data
        self.dport = self.vip_data.get("dport")
        self.cert_uuid = []
        if not hasattr(self, "tag"):
            self.get_tags(self.vip_data.get("tags"))
        for cert in self.vip_data.get("cert"):
            self.cert_parser(cert)
            self.get_cert()
        self.main_worker()

    def main_worker(self):
        """Main worker.

        Validate if input vip info has all fields required to create Nautobot entry.
        Get or create partition and environment UUID, before initiating VIP function.
        """
        if all(x in list(self.vip_data) for x in VIP_FIELDS):
            self.log.debug(f"VIP create / update / validate in process : {self.vip_data.get('name')} ...")

            try:
                self.get_partition()
                self.get_environment()
                self.get_vip()
            except Exception as err:
                self.log.error(f"Unable to create VIP : {self.vip_data.get('name')} : {err}")
        else:
            self.log.error(
                f"Mandatory VIP Fields are missing : {VIP_FIELDS} : {dict((i,self.vip_data[i]) for i in self.vip_data if i!='ns_info')}"
            )
            self.log.warning("Going for Next VIP")

    ###########################################
    # IP Address related functions
    ###########################################
    def get_address(self, addr, create=False):
        """Check if Address exist in Nautobot IPAM IP Address core module.

        Args:
            addr (str): IP address.
            create (bool, optional): If address does not exist, create address. Defaults to False.

        Returns:
            str: UUID of the IP address object.
        """
        tag = "ofd" if "ofd" in self.vip_data.get("tags") else "ofs"
        obj = f"ipam/ip-addresses?address={addr}&tag={tag}"
        resp = self.get_api_call(obj)
        if resp["count"] >= 1:
            return resp["results"][0]["id"]
        elif create:
            return self.create_address(addr)

    def create_address(self, addr):
        """Create Address in Nautobot IPAM IP Address core module.

        Args:
            addr (str): IP address.

        Returns:
            str: UUID of the IP address object.
        """
        obj = "ipam/ip-addresses/"
        data = dict([("address", addr), ("status", "active"), ("tags", self.tag)])
        resp = self.post_api_call(obj, **data)
        if resp:
            return resp["id"]
        return None

    ###########################################
    # Environment functions
    ###########################################
    def get_environment(self):
        """Check if Environment object exist in VIP Plugin module."""
        obj = f"plugins/vip-tracker/environments/?name={self.vip_data.get('environment')}"
        resp = self.get_api_call(obj)
        if resp["count"] >= 1:
            self.env_uuid = resp["results"][0]["id"]
        else:
            self.create_environment()

    def create_environment(self):
        """Create Environment object in VIP Plugin module."""
        obj = "plugins/vip-tracker/environments/"
        data = dict([("name", self.vip_data.get("environment")), ("slug", self.vip_data.get("environment").lower())])
        resp = self.post_api_call(obj, **data)
        if resp:
            self.env_uuid = resp["id"]

    ###########################################
    # Cert related functions
    ###########################################
    def cert_parser(self, cert):
        """Cert Parser.

        Cert dict will have three keys: cert_cn, cert_issuer, and cert_serial.
        This function will converts cert_issuer str value into dict of OU, CN, Organization, Country.
        Few issuers are Domain Contollers (DC).
        Also concert Date and time format to Nautobot compatible format.

        Args:
            cert (dict): Cert Info
        """
        self.cert = {}
        for k, v in cert.items():
            self.cert[k] = v
        if cert.get("cert_issuer"):
            self.cert["cert_issuer"] = {}
            dc = []
            for c in cert.get("cert_issuer").split(","):
                if "=" in c and "DC=" in c:
                    dc.append(c.split("=")[1])
                elif "=" in c:
                    self.cert["cert_issuer"][c.split("=")[0]] = c.split("=")[1]
            if dc:
                self.cert["cert_issuer"]["DC"] = "-".join(dc)
        if cert.get("cert_exp"):
            dateformat = datetime.strptime(cert.get("cert_exp"), "%b %d %H:%M:%S %Y %Z")
            self.cert["cert_exp"] = dateformat.strftime("%Y-%m-%dT%H:%M:%SZ")

    def get_cert(self):
        """Check if Cert object exist in VIP Plugin module."""
        obj = f"plugins/vip-tracker/certificates/?name={self.cert.get('cert_cn')}"
        resp = self.get_api_call(obj)
        if resp.get("count") == 0:
            self.create_update_cert()
        elif resp.get("count") == 1:
            if resp["results"][0].get("serial_number") == self.cert.get("cert_serial"):
                self.cert_uuid.append(resp["results"][0].get("id"))
            else:
                self.create_update_cert(resp["results"][0].get("id"))

    def create_update_cert(self, uuid=False):
        """Create new or update existing cert object in VIP Plugin module.

        Args:
            uuid (bool, optional): Update existing cert object. Defaults to False.
        """
        org = (
            self.cert["cert_issuer"].get("DC")
            if self.cert["cert_issuer"].get("DC")
            else self.cert["cert_issuer"].get("O", "UNKNOWN")
        )
        self.get_org(org)
        self.get_issuer()
        if hasattr(self, "cert_issuer_uuid"):
            obj = "plugins/vip-tracker/certificates/"
            data = dict(
                [
                    ("name", self.cert.get("cert_cn")),
                    ("slug", self.cert.get("cert_cn").replace(" ", "-").replace(".", "_").replace("*", "").lower(),),
                    ("exp", self.cert.get("cert_exp", "2000-01-01T00:00")),
                    ("serial_number", self.cert.get("cert_serial", "")),
                    ("issuer", self.cert_issuer_uuid),
                    ("cert_type", "RSA"),
                ]
            )
            if uuid:
                obj = f"plugins/vip-tracker/certificates/{uuid}/"
                if self.patch_api_call(obj, **data) == 200:
                    self.cert_uuid.append(uuid)
                    self.log.debug("Cert Info updated on Nautobot")
            else:
                resp = self.post_api_call(obj, **data)
                if resp:
                    self.cert_uuid.append(resp.get("id"))

    def get_issuer(self):
        """Check if Issuer object exist in VIP Plugin module."""
        obj = f"plugins/vip-tracker/issuer/?name={self.cert['cert_issuer'].get('CN')}"
        resp = self.get_api_call(obj)
        if resp.get("count") == 0:
            obj = "plugins/vip-tracker/issuer/"
            data = dict(
                [
                    ("name", self.cert["cert_issuer"].get("CN")),
                    (
                        "slug",
                        self.cert["cert_issuer"].get("CN").replace(" ", "-").replace(".", "_").replace("*", "").lower(),
                    ),
                    ("country", self.cert["cert_issuer"].get("C", "")),
                    ("location", self.cert["cert_issuer"].get("L", "")),
                    ("state", self.cert["cert_issuer"].get("ST", "")),
                    ("email", self.cert["cert_issuer"].get("emailAddress", "")),
                    ("organization", self.cert_org_uuid),
                ]
            )
            resp = self.post_api_call(obj, **data)
            if resp:
                self.cert_issuer_uuid = resp.get("id")
        elif resp.get("count") == 1:
            self.cert_issuer_uuid = resp["results"][0].get("id")

    def get_org(self, org):
        """Check if Organization object exist in VIP Plugin module.

        Args:
            org (str): Organization name from cert issuer field.
        """
        obj = f"plugins/vip-tracker/organization/?name={org}"
        resp = self.get_api_call(obj)
        if resp.get("count") == 0:
            obj = "plugins/vip-tracker/organization/"
            data = dict([("name", org), ("slug", org.replace(" ", "-").replace(".", "_").replace("*", "").lower())])
            resp = self.post_api_call(obj, **data)
            if resp:
                self.cert_org_uuid = resp.get("id")
        elif resp.get("count") == 1:
            self.cert_org_uuid = resp["results"][0].get("id")

    ###########################################
    # VIP related functions
    ###########################################

    def get_vip(self):
        """Check if VIP object exist in VIP Plugin module."""
        self.vip_addr_uuid = self.get_address(self.vip_data.get("address"))
        if self.vip_addr_uuid:
            obj = (
                f"plugins/vip-tracker/vip-detail/?name={self.vip_data.get('name')}&environment={self.env_uuid}"
                f"&address={self.vip_addr_uuid}&port={self.vip_data.get('port')}"
            )
            resp = self.get_api_call(obj)
            if resp.get("count") == 1:
                self.update_vip(resp["results"][0])
            else:
                self.create_vip()
        else:
            self.create_vip()

    def create_vip(self):
        """Create VIP object in VIP Plugin module."""
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
                    ("certificates", self.cert_uuid),
                    ("loadbalancer", self.lb_uuid),
                    ("partition", self.partition_uuid),
                    ("environment", self.env_uuid),
                    ("advanced_policies", self.advp_uuid),
                    ("protocol", self.vip_data.get("protocol", "TCP").upper()),
                    ("tags", self.tag),
                ]
            )
            resp = self.post_api_call(obj, **data)
            if resp:
                self.log.debug("VIP created on Nautobot")
        else:
            self.log.error("Unable to create VIP UUID")

    def update_vip(self, n_vip):
        """Update existing VIP object in VIP Plugin module.

        Args:
            n_vip (dict): VIP info.
        """
        uuid = n_vip.get("id")
        data = {}
        self.get_pool()
        data["loadbalancer"] = self.lb_uuid
        data["pool"] = self.vip_pool_uuid
        data["environment"] = self.env_uuid
        data["advanced_policies"] = self.advp_uuid
        data["certificates"] = self.cert_uuid
        data["tags"] = self.tag

        obj = f"plugins/vip-tracker/vip/{uuid}/"
        if self.patch_api_call(obj, **data) == 200:
            self.log.debug("VIP updated on Nautobot")

    ###########################################
    # Pool related functions
    ###########################################

    def get_pool(self):
        """Check if pool object exist in VIP Plugin module."""
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
        """Create pool object in VIP Plugin module."""
        obj = "plugins/vip-tracker/pools/"
        data = dict(
            [
                ("name", self.vip_data["pool"]),
                ("slug", self.vip_data["pool"].replace(" ", "-").replace(".", "_").replace("*", "").lower()),
                ("members", self.pool_mem_uuid),
            ]
        )
        resp = self.post_api_call(obj, **data)
        if resp:
            self.vip_pool_uuid = resp["id"]

    def update_pool(self):
        """Update existing pool object in VIP Plugin module."""
        obj = f"plugins/vip-tracker/pools/{self.vip_pool_uuid}/"
        data = dict([("members", self.pool_mem_uuid)])
        if self.patch_api_call(obj, **data) == 200:
            self.log.debug("VIP Pool updated on Nautobot")

    ###########################################
    # Pool members related functions
    ###########################################

    def get_pool_mem_addr(self):
        """Check if pool member object exist in VIP Plugin module."""
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
        """Pool Member.

        Create pool member object in VIP Plugin module.
        Check if pool member is 1.1.1.1 IP address and action accordingly.

        Args:
            mem_info (dict): Pool member info from pool_mem_parser function.
        """
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
                ("tags", self.tag),
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
        """Convert pool member info into dict format to create pool."""

        def _parser(slug_name):
            """Replace special charaters for slug name.

            Args:
                slug_name (str): Slug name.

            Returns:
                str: Slug name with no special characters.
            """
            return slug_name.replace(".", "_").replace("/", "_")

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
    # Partition and Advance Policies
    ###########################################

    def get_partition(self):
        """Check if partition object exist in VIP Plugin module."""
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
        """Create partition object in VIP Plugin module."""
        data = dict([("name", self.vip_data.get("partition")), ("slug", self.vip_data.get("partition").lower())])
        obj = "plugins/vip-tracker/partitions/"
        resp = self.post_api_call(obj, **data)
        self.partition_uuid = resp["id"]

    def get_adv_policy(self):
        """Check if Advance policy object exist in VIP Plugin module."""
        for pol in self.vip_data.get("advanced_policies", []):
            obj = f"plugins/vip-tracker/policies/?name={pol}"
            resp = self.get_api_call(obj)
            if resp["count"] >= 1:
                self.advp_uuid.append(resp["results"][0]["id"])
            else:
                self.create_adv_policy(pol)

    def create_adv_policy(self, pol):
        """Create Advance policy object in VIP Plugin module.

        Args:
            pol (str): Advance policy object name.
        """
        data = dict([("name", pol), ("slug", pol.lower().replace("/", "_").replace(".", "_"))])
        obj = "plugins/vip-tracker/policies/"
        resp = self.post_api_call(obj, **data)
        if resp:
            self.advp_uuid.append(resp["id"])
        else:
            self.log.error(f"Unable to create Advance Policy : {data}")

    #################################
    # Device related functions
    #################################

    def get_loadbalancer(self, lb_data):
        """Check if loadbalancer object exist in core Device module.

        Args:
            lb_data (dict): LB related info.
        """
        self.lb_data = lb_data
        if not hasattr(self, "tag"):
            self.get_tags(self.lb_data.get("tags"))
        name = self.lb_data.get("hostname")
        obj = f"dcim/devices/?name={name}"
        resp = self.get_api_call(obj)
        if resp["count"] == 1:
            self.lb_uuid = resp["results"][0]["id"]
        else:
            self.create_loadbalancer()

    def create_loadbalancer(self):
        """Create loadbalancer object in core Device module."""
        self.get_device_type()
        if hasattr(self, "device_type_uuid"):
            self.get_device_role()
            if hasattr(self, "device_role_uuid"):
                self.get_site()
                if hasattr(self, "site_uuid"):
                    data = dict(
                        [
                            ("name", self.lb_data.get("hostname")),
                            ("device_type", self.device_type_uuid),
                            ("device_role", self.device_role_uuid),
                            ("site", self.site_uuid),
                            ("status", "active"),
                            ("tags", self.tag),
                        ]
                    )
                    resp = self.post_api_call("dcim/devices/", **data)
                    if resp:
                        self.lb_uuid = resp["id"]

    def get_device_type(self):
        """Check if device type object exist in core Device module."""
        obj = f"dcim/device-types/?model={self.lb_data.get('type','ltm')}"
        resp = self.get_api_call(obj)
        if resp["count"] == 1:
            self.device_type_uuid = resp["results"][0]["id"]
        else:
            self.create_device_type()

    def create_device_type(self):
        """Create device type object in core Device module."""
        obj = "dcim/device-types/"
        model = self.lb_data.get("type", "ltm").lower()
        data = dict([("manufacturer", self.get_manufacturers()), ("model", model), ("slug", model)])
        resp = self.post_api_call(obj, **data)
        if resp:
            self.device_type_uuid = resp["id"]

    def get_device_role(self):
        """Check if device role object exist in core Device module."""
        obj = "dcim/device-roles?name=load_balancer"
        resp = self.get_api_call(obj)
        if resp["count"] == 1:
            self.device_role_uuid = resp["results"][0]["id"]
        else:
            self.create_device_role()

    def create_device_role(self):
        """Create device role object in core Device module."""
        obj = "dcim/device-roles/"
        resp = self.post_api_call(obj, **NAUTOBOT_DEVICE_ROLES["LB"])
        if resp:
            self.device_type_uuid = resp["id"]

    def get_tags(self, tags):
        """Check if tag object exist in core Organization module.

        Args:
            tags (list): list of tag names.
        """
        for tag in tags:
            obj = f"extras/tags/?slug={tag}"
            resp = self.get_api_call(obj)
            if resp["count"] == 0:
                self.create_tags(tag)
        self.tag = [{"slug": tag.lower()} for tag in tags]

    def create_tags(self, tag):
        """Create tag object in core Organization module.

        Args:
            tag (str): tag name.
        """
        obj = "extras/tags/"
        data = dict([("name", tag.upper()), ("slug", tag.lower())])
        self.post_api_call(obj, **data)

    #################################################
    # Site, Region and Manufacturer related functions
    #################################################

    def get_manufacturers(self):
        """Check if Manufacturers object exist in core Device module.

        Returns:
            str: UUID of the Manufacturer object.
        """
        name = "f5" if "product" in self.lb_data else "citrix"
        obj = f"dcim/manufacturers/?slug={name}"
        resp = self.get_api_call(obj)
        if resp["count"] == 1:
            return resp["results"][0]["id"]
        else:
            self.log.error(f"Manufacturer Not Found On Nautobot : {obj}")

    def get_site(self):
        """Get Site.

        LB Name are not as per standards. Static config file has hostname and site mapping.
        For OFD, NAUTOBOT_DEVICE_REGION and for OFS, NAUTOBOT_DEVICE_REGION_OFS
        Lookup config file and find appropriate site name match for OFS and OFD device.
        """

        def site(name):
            """Check if Site object exist in core Organization module.

            Args:
                name (str): Site name.
            """
            obj = f"dcim/sites/?slug={name.get('site').lower()}"
            resp = self.get_api_call(obj)
            if resp["count"] == 1:
                self.site_uuid = resp["results"][0]["id"]
            else:
                self.create_site(name)

        if "ofd" in self.lb_data.get("tags"):
            lb_dkey = self.lb_data.get("hostname")[:6]
            if lb_dkey in NAUTOBOT_DEVICE_REGION.keys():
                site(NAUTOBOT_DEVICE_REGION[lb_dkey])
            else:
                site(NAUTOBOT_DEVICE_REGION.get("SANE_UNK"))
        elif "ofs" in self.lb_data.get("tags"):
            octate = ".".join(self.lb_data.get("address").split(".", 2)[:2])
            if octate in NAUTOBOT_DEVICE_REGION_OFS.keys():
                site(NAUTOBOT_DEVICE_REGION_OFS[octate])
            else:
                octate = ".".join(self.lb_data.get("mgmt_ip_address").split(".", 2)[:2])
                if octate in NAUTOBOT_DEVICE_REGION_OFS.keys():
                    site(NAUTOBOT_DEVICE_REGION_OFS[octate])
                else:
                    site(NAUTOBOT_DEVICE_REGION.get("SANE_UNK"))
        else:
            site(NAUTOBOT_DEVICE_REGION.get("SANE_UNK"))

    def create_site(self, name):
        """Create site object in core Organization module.

        Args:
            name (str): Site name.
        """
        obj = "dcim/sites/"
        self.get_region(name)
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
        """Check if Region object exist in core Organization module.

        Args:
            name (str): Region name.
        """
        obj = f"dcim/regions/?name={name.get('region')}"
        resp = self.get_api_call(obj)
        if resp["count"] == 1:
            self.region_uuid = resp["results"][0]["id"]
        else:
            self.create_region(name)

    def create_region(self, name):
        """Create region object in core Organization module.

        Args:
            name ([type]): [description]
        """
        obj = "dcim/regions/"
        data = dict([("name", name.get("region")), ("slug", name.get("region").replace(" ", "-").lower())])
        resp = self.post_api_call(obj, **data)
        if resp:
            self.region_uuid = resp["id"]

    #################################
    # GET, POST, PATCH API Function
    #################################

    def get_api_call(self, obj):
        """GET API call function.

        Args:
            obj (str): URI path.

        Returns:
            dict: Data in dict format.
        """
        try:
            self.log.info(obj)
            resp = self.NB.nb_data("GET", obj, **{})
            if resp.status_code == 200:
                self.log.debug(f"GET Data obj={obj}, resp={resp.status_code} : {json.loads(resp.text)['count']}")
                return json.loads(resp.text)
            self.log.debug(f"GET Data obj={obj}, resp={resp.status_code}")
        except Exception as err:
            self.log.error(f"Unable to GET obj={obj}, error={err}")

    def patch_api_call(self, obj, **data):
        """PATCH API call function.

        Args:
            obj (str): URI path.

        Returns:
            dict: Data in dict format.
        """
        payload = {"data": data}
        try:
            self.log.info(f"PATCH Data obj={obj}, data={data}")
            resp = self.NB.nb_data("PATCH", obj, **payload)
            self.log.debug(f"PATCH Data obj={obj}, data={data}, resp={resp.status_code}")
            if resp.status_code == 200:
                return resp.status_code
            self.log.error(f"Unable to PATCH obj={obj}, data={data}, resp={resp.status_code} : {resp.text}")
        except Exception as err:
            self.log.error(f"Unable to PATCH obj={obj}, data={data}, error={err}")

    def post_api_call(self, obj, **data):
        """POST API call function.

        Args:
            obj (str): URI path.

        Returns:
            dict: Data in dict format.
        """
        payload = {"data": data}
        try:
            self.log.info(f"POST Data obj={obj}, data={data}")
            resp = self.NB.nb_data("POST", obj, **payload)
            self.log.debug(f"POST Data obj={obj}, data={data}, resp={resp.status_code}")
            if resp.status_code == 201:
                return json.loads(resp.text)
            self.log.error(f"Unable to POST obj={obj}, data={data}, resp={resp.status_code} : {resp.text}")
        except Exception as err:
            self.log.error(f"Unable to POST obj={obj}, data={data}, error={err}")
