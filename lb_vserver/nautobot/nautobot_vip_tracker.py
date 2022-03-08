# pylint: disable=W1203, C0103, W0631, W0703
"""Nautobot REST API SDK."""

import pynautobot
from helper import log
from helper.variables_lb import VIP_FIELDS
from datetime import datetime
from nautobot.nautobot_attr import VIPT_ATTR
from nautobot.nautobot_filters import cert_filter, vip_port_filter, cert_filter1, cert_serial


class LB_VIP(VIPT_ATTR):
    """Create a Nautobot LB VIP Function client."""

    # fmt: off
    def __init__(self, vip_data, loadbalancer_uuid, tag_uuid):
        """Initialize Nautobot Function Client.

        Args:
            vip_data (dict)         : LB VIP information in dict format.
            loadbalancer_uuid (str) : LB Device UUID.
            tag_uuid (list)          : Tag UUID in list.
        """
        self.vip_data           = vip_data
        self.loadbalancer_uuid  = loadbalancer_uuid
        self.tag_uuid           = tag_uuid
        self.policies_uuid      = []
        self.environment_uuid   = ""
        self.partition_uuid     = ""
        self.certificates_uuid  = []
        self.vip_addr_uuid      = ""
        self.create_vip         = True
        self.vip_query          = """
        query ($vip: String!) {
            vips (name: $vip) {
                address { address }
                port
                protocol
                pool { members { address { address } } }
                certificates { serial_number }
            }
        }
        """
        # fmt: on

    def main_fun(self):
        """Main function, initiated from nautobot_master.

        Validate if input vip info has all fields required to create Nautobot entry.
        Create partition and environment UUID, before initiating VIP function.
        """
        if all(x in list(self.vip_data) for x in VIP_FIELDS):
            self.vip_address()
            self.validate_update()
            if self.create_vip:
                if not self.vip_data.get("pool_mem", []):
                    self.vip_data["pool_mem"] = ["1.1.1.1"]
                # self.members()
                if not self.vip_data.get("pool"):
                    self.vip_data["pool"] = "UNKNOWN"
                self.pool()
                if self.vip_data.get("cert"):
                    self.certificates()
                if self.vip_data.get("partition"):
                    self.partition()
                if self.vip_data.get("advanced_policies"):
                    self.policies()
                self.environment()
                self.vip()
        else:
            log.warning(
                f"[Missing VIP Fields][{self.vip_data.get('loadbalancer')}] {self.vip_data.get('name')} {list(self.vip_data)}"
            )

    def validate_update(self):
        """Validate if VIP already exist in Nautobot."""
        variables = {"vip": self.vip_data.get("name")}
        self.vip_addr_uuid
        resp = VIPT_ATTR.nb.graphql.query(query=self.vip_query, variables=variables).json
        for vip in resp["data"].get("vips", []):
            if self.vip_data.get("address").split("/")[0] == vip["address"].get("address").split("/")[0]:
                if vip_port_filter(vip, self.vip_data):
                    self.create_vip = False
                    for mem in vip["pool"].get("members"):
                        if mem["address"].get("address").split("/")[0] not in str(self.vip_data.get("pool_mem")):
                            self.pool()
                    if self.vip_data.get("cert") and len(self.vip_data.get("cert")) < 5:
                        for cert in self.vip_data.get("cert"):
                            try:
                                if cert_filter(cert, vip):
                                    self.certificates()
                            except Exception as err:
                                log.error(f"{vip}{cert}:{err}")

    def vip(self):
        """Create VIP object in VIP Plugin module."""
        data = {
            "name": self.vip_data.get("name"),
            "port": self.vip_data.get("port"),
            "address": self.vip_addr_uuid,
            "pool": self.pool_uuid,
            "certificates": self.certificates_uuid,
            "loadbalancer": self.loadbalancer_uuid,
            "partition": self.partition_uuid,
            "environment": self.environment_uuid,
            "advanced_policies": self.policies_uuid,
            "protocol": self.vip_data.get("protocol", "TCP").upper(),
            "tags": self.tag_uuid,
        }
        try:
            VIPT_ATTR.vip_attr.create(data)
        except pynautobot.core.query.RequestError:
            pass
            # log.warning(
            # f"Duplicate VIP:Port [{self.vip_data.get('name')}] {self.vip_data.get('address')}:{self.vip_data.get('port')}"
            # )
        except Exception as err:
            log.error(f"[Create][{self.vip_data.get('loadbalancer')}] {self.vip_data} : {err}")

    ###########################################
    # VIP address functions
    ###########################################
    def vip_address(self):
        """Create VIP Address."""
        self.vip_addr_uuid = self.ipam_address(self.vip_data.get("address"))

    def environment(self):
        """Create Environment object in VIP Plugin module."""
        environment = VIPT_ATTR.environments_attr.get(name=self.vip_data.get("environment"))
        if not environment:
            data = {
                "name": self.vip_data.get("environment"),
                "slug": self.slug_parser(self.vip_data.get("environment")),
            }
            try:
                environment = VIPT_ATTR.environments_attr.create(data)
            except Exception as err:
                log.error(
                    f"[{self.vip_data.get('loadbalancer')}] {self.vip_data.get('name')} {self.vip_data.get('environment')} : {err}"
                )
        self.environment_uuid = environment.id

    def partition(self):
        """Create Partition object in VIP Plugin module."""
        partition = VIPT_ATTR.partitions_attr.get(slug=self.slug_parser(self.vip_data.get("partition")))
        if not partition:
            data = {"name": self.vip_data.get("partition"), "slug": self.slug_parser(self.vip_data.get("partition"))}
            try:
                partition = VIPT_ATTR.partitions_attr.create(data)
            except Exception as err:
                log.error(
                    f"[{self.vip_data.get('loadbalancer')}] {self.vip_data.get('name')} {self.vip_data.get('partition')} : {err}"
                )
        self.partition_uuid = partition.id

    def policies(self):
        """Create Policies object in VIP Plugin module."""
        adv_policies = []
        for policy in self.vip_data.get("advanced_policies"):
            policies = VIPT_ATTR.policies_attr.get(name=policy)
            if not policies:
                data = {"name": policy, "slug": self.slug_parser(policy)}
                try:
                    policies = VIPT_ATTR.policies_attr.create(data)
                except Exception as err:
                    log.error(f"[{self.vip_data.get('loadbalancer')}] {self.vip_data.get('name')} {policy} : {err}")
            adv_policies.append(policies.id)
        self.policies_uuid = adv_policies

    ###########################################
    # Cert related functions
    ###########################################

    def certificates(self):
        """Create Certificate object in VIP Plugin module."""
        cert_uuid = []
        try:
            for cert in self.vip_data.get("cert"):
                self.cert_parser(cert)
                certificate = VIPT_ATTR.certificates_attr.get(slug=self.slug_parser(self.cert_info.get("cn")))
                if not certificate and self.cert_info.get("serial") and len(self.cert_info.get("serial")) > 10:
                    certificate = VIPT_ATTR.certificates_attr.get(serial_number=self.cert_info.get("serial"))
                data = {
                    "exp": self.cert_info.get("exp", "2000-01-01T00:00"),
                    "serial_number": self.cert_info.get("serial"),
                    "cert_type": "RSA",
                }
                if certificate:
                    try:
                        if cert_filter1(data, certificate):
                            certificate.update(data)
                    except Exception as err:
                        log.error(
                            f"[{self.vip_data.get('loadbalancer')}] {self.vip_data.get('name')} {cert.get('cert_cn')} : {err}"
                        )
                else:
                    self.cert_issuer()
                    data["name"] = self.cert_info.get("cn")
                    data["slug"] = self.slug_parser(self.cert_info.get("cn"))
                    data["issuer"] = self.cert_issuer_uuid
                    try:
                        certificate = VIPT_ATTR.certificates_attr.create(data)
                    except Exception as err:
                        log.error(
                            f"[{self.vip_data.get('loadbalancer')}] {self.vip_data.get('name')} {cert.get('cert_cn')} : {err}"
                        )
                if certificate:
                    cert_uuid.append(certificate.id)
        except Exception as err:
            log.error(
                f"[{self.vip_data.get('loadbalancer')}] {self.vip_data.get('name')} Cert error : {err}"
            )
        self.certificates_uuid = cert_uuid

    def cert_parser(self, cert_data):
        """Cert Parser.

        Cert dict will have three keys: cert_cn, cert_issuer, and cert_serial.
        This function will converts cert_issuer str value into dict of OU, CN, Organization, Country.
        Few issuers are Domain Contollers (DC).
        Also concert Date and time format to Nautobot compatible format.

        Args:
            cert_data (dict): Cert Info
        """
        log.debug(f"[Cert] Before Parser : {cert_data}")
        # cert = {"serial": randint(100, 2000) if not cert_data.get("cert_serial") else cert_data.get("cert_serial")}
        cert = cert_serial(cert_data)
        cert["cn"] = cert_data.get("cert_cn", "").split("/")[0].split(",")[0]
        if cert_data.get("cert_issuer"):
            cert["issuer"] = {}
            dc = []
            for c in cert_data.get("cert_issuer").split(","):
                if "=" in c and "DC=" in c:
                    dc.append(c.split("=")[1])
                elif "=" in c:
                    cert["issuer"][c.split("=")[0].strip()] = c.split("=")[1].split("/")[0].strip()
            if dc:
                cert["issuer"]["DC"] = "-".join(dc)
        if cert_data.get("cert_exp"):
            dateformat = datetime.strptime(cert_data.get("cert_exp"), "%b %d %H:%M:%S %Y %Z")
            cert["exp"] = dateformat.strftime("%Y-%m-%dT%H:%M:%SZ")
        log.debug(f"[Cert] After Parser : {cert}")
        self.cert_info = cert

    def cert_issuer(self):
        """Create Certificate Issuer object in VIP Plugin module."""
        if self.cert_info["issuer"].get("CN"):
            name = self.cert_info["issuer"].get("CN")
        elif self.cert_info["issuer"].get("O"):
            name = self.cert_info["issuer"].get("O")
        else:
            name = "UNKNOWN"
        issuer = VIPT_ATTR.issuer_attr.get(name=name)
        if not issuer:
            self.cert_organization_uuid = ""
            self.cert_organization()
            data = {
                "name": name,
                "slug": self.slug_parser(name),
                "country": self.cert_info["issuer"].get("C", ""),
                "location": self.cert_info["issuer"].get("L", ""),
                "state": self.cert_info["issuer"].get("ST", ""),
                "email": self.cert_info["issuer"].get("emailAddress", ""),
                "organization": self.cert_organization_uuid,
            }
            try:
                issuer = VIPT_ATTR.issuer_attr.create(data)
            except Exception as err:
                log.error(
                    f"[{self.vip_data.get('loadbalancer')}] {self.vip_data.get('name')} {self.cert_info['issuer'].get('CN')} : {err}"
                )
        self.cert_issuer_uuid = issuer.id

    def cert_organization(self):
        """Create Certificate Organization object in VIP Plugin module."""
        org = self.cert_info["issuer"].get("O", "UNKNOWN")
        organization = VIPT_ATTR.organization_attr.get(name=org)
        if not organization:
            data = {"name": org, "slug": self.slug_parser(org)}
            try:
                organization = VIPT_ATTR.organization_attr.create(data)
            except Exception as err:
                log.error(f"[{self.vip_data.get('loadbalancer')}] {self.vip_data.get('name')} {org} : {err}")
        self.cert_organization_uuid = organization.id

    def pool(self):
        """Create Pool Member object in VIP Plugin module."""
        try:
            self.members()
            pools = self.pool_exist_by_addr(self.members_uuid, self.vip_data.get("pool"))
            if not pools:
                pools = self.pool_exist_by_name(self.vip_data.get("pool"))
            data = {
                "name": self.vip_data.get("pool"),
                "slug": self.slug_parser(self.vip_data.get("pool")),
                "members": self.members_uuid,
                "tags": self.tag_uuid,
            }
            if not pools:
                pools = VIPT_ATTR.pools_attr.create(data)
            else:
                try:
                    pools.update(data)
                except pynautobot.core.query.RequestError as err:
                    log.error(f"[PoolUpdateError] {self.vip_data} {self.vip_data.get('pool')} :{err}")
            self.pool_uuid = pools.id
        except Exception as err:
            log.error(f"[{self.vip_data.get('loadbalancer')}] {self.vip_data.get('name')} {self.vip_data.get('pool')} : {err}")
            self.pool_error()

    def pool_exist_by_name(self, name):
        """Check for Pool by name."""
        pools = VIPT_ATTR.pools_attr.get(slug=self.slug_parser(name))
        if pools:
            return pools

    def pool_exist_by_addr(self, addr_uuid, name=""):
        """Check for Pool by Member UUID."""
        try:
            pool_lst = VIPT_ATTR.pools_attr.filter(members=addr_uuid)
            if name:
                for pool in pool_lst:
                    if pool.name == name:
                        pools = pool
                        return pools
        except pynautobot.core.query.RequestError:
            pass

    def pool_error(self):
        """Default Pool."""
        pool_name = "pool_error"
        mem_addr_uuid = self.ipam_address("1.1.1.1")
        pools = self.pool_exist_by_addr(mem_addr_uuid)
        if not pools:
            data = {
                "name": pool_name,
                "slug": self.slug_parser(pool_name),
                "members": [mem_addr_uuid],
                "tags": self.tag_uuid,
            }
            pools = VIPT_ATTR.pools_attr.create(data)
        self.pool_uuid = pools.id

    def members(self):
        """Create Pool Member object in VIP Plugin module."""
        members = []
        # port = mem.get("port")
        self.pool_mem_parser()
        for mem in self.pool_mem_info:
            mem_uuid = self.ipam_address(mem.get("address"))
            port = "1" if mem.get("port") == "0" else mem.get("port", "1")
            name = f'{mem.get("name").replace("%", "")}_{port}'
            member = VIPT_ATTR.members_attr.get(address=mem_uuid, port=port)
            if not member:
                member = VIPT_ATTR.members_attr.get(name=name, port=port)
            if member:
                members.append(member.id)
            else:
                data = {
                    "name": name,
                    "slug": self.slug_parser(name),
                    "address": mem_uuid,
                    "port": port,
                    "tags": self.tag_uuid,
                }
                # log.info(f"creating member {data}")
                try:
                    member = VIPT_ATTR.members_attr.create(data)
                    log.debug("[Member] Created")
                except Exception as err:
                    log.error(
                        f"[{self.vip_data.get('loadbalancer')}] {self.vip_data.get('name')} {mem.get('name')} : {err}"
                    )
                members.append(member.id)
        self.members_uuid = members

    def pool_mem_parser(self):
        """Convert pool member info into dict format to create pool."""
        self.pool_mem_info = []
        if isinstance(self.vip_data.get("pool_mem"), str):
            self.pool_mem_info.append(
                {"name": self.vip_data.get("pool_mem"), "address": self.vip_data.get("pool_mem")}
            )
        elif isinstance(self.vip_data.get("pool_mem"), list):
            for addr in self.vip_data.get("pool_mem"):
                if isinstance(addr, dict):
                    self.pool_mem_info.append(addr)
                else:
                    self.pool_mem_info.append({"name": addr, "address": addr})

    ###########################################
    # IP Address and Slug Parser functions
    ###########################################

    def ipam_address(self, address):
        """Create IP Address object in core IPAM module.

        Args:
            address (str): IP Address.

        Returns:
            str: IP Address UUID.
        """
        ipam_addr = VIPT_ATTR.ip_addresses_attr.filter(address=address)
        ipam_address = False
        for addr in ipam_addr:
            tag1 = self.vip_data.get("tags")
            tag2 = [i.slug for i in addr.tags]
            tag2.sort()
            tag1.sort()
            if address == addr.address.split("/")[0] and tag1 == tag2:
                ipam_address = addr
        if not ipam_address:
            data = dict([("address", address), ("status", "active"), ("tags", self.tag_uuid)])
            try:
                ipam_address = VIPT_ATTR.ip_addresses_attr.create(data)
            except Exception as err:
                log.error(f"[{self.vip_data.get('loadbalancer')}] {self.vip_data.get('name')} {address} : {err}")
        return ipam_address.id

    def slug_parser(self, name):
        """Slug name parser.

        Replace all special characters and space with "_" and covert to lower case.

        Args:
            name (str): Object name.

        Returns:
            str: Object name.
        """
        return (
            name.replace(" ", "-")
            .replace(".", "_")
            .replace("*", "")
            .replace("/", "_")
            .replace("%", "_")
            .replace("&", "")
            .replace("(", "")
            .replace(")", "")
            .lower()
        )
