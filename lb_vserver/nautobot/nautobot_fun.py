# pylint: disable=W1203, C0103, W0631, W0703
"""Nautobot REST API SDK."""

import os
import requests
import pynautobot
from random import randint
from helper.variables_nautobot import NAUTOBOT_DEVICE_REGION, NAUTOBOT_DEVICE_REGION_OFS
from helper.local_helper import log
from helper.variables_lb import VIP_FIELDS
from datetime import datetime

requests.urllib3.disable_warnings()

url                     = os.environ.get("RD_OPTION_NAUTOBOT_URL")
token                   = os.environ.get("RD_OPTION_NAUTOBOT_KEY")
nb                      = pynautobot.api(url, token=token, threading=True)
nb.http_session.verify  = False
plugins_attr            = getattr(nb, "plugins")
extras_attr             = getattr(nb, "extras")
dcim_attr               = getattr(nb, "dcim")
ipam_attr               = getattr(nb, "ipam")
vip_tracker_attr        = getattr(plugins_attr, "vip-tracker")
tags_attr               = getattr(extras_attr, "tags")
ip_addresses_attr       = getattr(ipam_attr, "ip-addresses")
interfaces_attr         = getattr(dcim_attr, "interfaces")
sites_attr              = getattr(dcim_attr, "sites")
devices_attr            = getattr(dcim_attr, "devices")
device_types_attr       = getattr(dcim_attr, "device-types")
device_roles_attr       = getattr(dcim_attr, "device-roles")
manufacturers_attr      = getattr(dcim_attr, "manufacturers")
regions_attr            = getattr(dcim_attr, "regions")
platforms_attr          = getattr(dcim_attr, "platforms")
vip_attr                = getattr(vip_tracker_attr, "vip")
vip_detail_attr         = getattr(vip_tracker_attr, "vip-detail")
certificates_attr       = getattr(vip_tracker_attr, "certificates")
environments_attr       = getattr(vip_tracker_attr, "environments")
issuer_attr             = getattr(vip_tracker_attr, "issuer")
members_attr            = getattr(vip_tracker_attr, "members")
organization_attr       = getattr(vip_tracker_attr, "organization")
partitions_attr         = getattr(vip_tracker_attr, "partitions")
policies_attr           = getattr(vip_tracker_attr, "policies")
pools_attr              = getattr(vip_tracker_attr, "pools")


class LB_DEVICE:
    """Create a Nautobot LB Device Function client."""

    def __init__(self, device_data):
        """Initialize Nautobot Function Client.

        Args:
            device_data (dict): LB Device information in dict format.
        """
        self.device_data = device_data

    def device(self):
        """Check if loadbalancer object exist in core Device module."""
        device = devices_attr.get(name=self.device_data.get("hostname"))
        self.tags()
        if not device:
            self.device_role()
            self.device_type()
            self.site()
            self.device_platforms()
            data = {
                "name": self.device_data.get("hostname"),
                "device_type": self.device_type_uuid,
                "device_role": self.device_role_uuid,
                "platform": self.platform_uuid,
                "site": self.site_uuid,
                "status": "active",
                "tags": self.tag_uuid,
            }
            device = devices_attr.create(data)
        self.loadbalancer_uuid = device.id
        self.device_interface()

    def device_interface(self):
        """Create Device Interface object in core Organization module."""
        interface = interfaces_attr.filter(device=self.device_data.get("hostname"))
        if interface:
            self.interface_uuid = interface[0].id
        else:
            data = {
                "device": self.loadbalancer_uuid,
                "name": "Management",
                "type": "virtual",
                "enabled": True,
                "description": f"{self.device_data.get('hostname')} Management Interface"
            }
            interface = interfaces_attr.create(data)
            self.interface_uuid = interface[0].id
        self.device_interface_address()

    def device_interface_address(self):
        """Create Interface Address object in core Organization module."""
        self.mgmt_address_uuid = self.ipam_address(self.device_data.get("mgmt_address"))
        data = {"primary_ip4": self.mgmt_address_uuid}
        device = devices_attr.get(name=self.device_data.get("hostname"))
        device.update(data)

    def device_role(self):
        """Create Device Role object in core Organization module."""
        device_role = device_roles_attr.get(name="load_balancer")
        if not device_role:
            data = {"name": "load_balancer", "slug": "load-balancer", "description": "F5 and Citrix LB role"}
            device_role = device_roles_attr.create(data)
        self.device_role_uuid = device_role.id

    def device_platforms(self):
        """Create Device Platform object in core Organization module."""
        name = "bigip" if "F5" in self.device_data.get("environment") else "netscaler"
        platform = platforms_attr.get(name=name)
        if not platform:
            data = {"name": name, "slug": name, "manufacturer": self.manufacturer_uuid}
            platform = platforms_attr.create(data)
        self.platform_uuid = platform.id

    def device_type(self):
        """Create Device Type object in core Organization module."""
        device_type = device_types_attr.get(slug=self.device_data.get("type").lower())
        if not device_type:
            self.manufacturers()
            data = {
                "manufacturer": self.manufacturer_uuid,
                "model": self.device_data.get("type"),
                "slug": self.slug_parser(self.device_data.get("type")),
            }
            device_type = device_types_attr.create(data)
        self.device_type_uuid = device_type.id

    def manufacturers(self):
        """Create manufacturer object in core Organization module."""
        manufacturer_name = "F5" if "F5" in self.device_data.get("environment") else "Citrix"
        manufacturer = manufacturers_attr.get(name=manufacturer_name)
        if not manufacturer:
            data = {"name": manufacturer_name.upper(), "slug": self.slug_parser(manufacturer_name)}
            manufacturer = manufacturers_attr.create(data)
        self.manufacturer_uuid = manufacturer.id

    def tags(self):
        """Create tag object in core Organization module."""
        tag_uuid = []
        for tag_name in self.device_data.get("tags"):
            tag = tags_attr.get(slug=self.slug_parser(tag_name))
            if not tag:
                data = {"name": tag_name.upper(), "slug": self.slug_parser(tag_name)}
                tag = tags_attr.create(data)
            tag_uuid.append(tag.id)
        self.tag_uuid = tag_uuid

    def site(self):
        """Create Site object in core Organization module."""
        self.site_info = NAUTOBOT_DEVICE_REGION.get("SANE_UNK")
        if "ofd" in self.device_data.get("tags"):
            lb_dkey = self.device_data.get("hostname")[:6]
            if lb_dkey in NAUTOBOT_DEVICE_REGION.keys():
                self.site_info = NAUTOBOT_DEVICE_REGION[lb_dkey]
        elif "ofs" in self.device_data.get("tags"):
            octate = ".".join(self.device_data.get("address").split(".", 2)[:2])
            if octate in NAUTOBOT_DEVICE_REGION_OFS.keys():
                self.site_info = NAUTOBOT_DEVICE_REGION_OFS[octate]
        site = sites_attr.get(slug=self.slug_parser(self.site_info.get("site")))
        if not site:
            self.region()
            data = {
                "name": self.site_info.get("site"),
                "slug": self.slug_parser(self.site_info.get("site")),
                "status": "active",
                "region": self.region_uuid,
                "description": self.site_info.get("description", ""),
            }
            site = sites_attr.create(data)
        self.site_uuid = site.id

    def region(self):
        """Create Region object in core Organization module."""
        region = regions_attr.get(name=self.site_info.get("region"))
        if not region:
            data = {"name": self.site_info.get("region"), "slug": self.slug_parser(self.site_info.get("region"))}
            region = regions_attr.create(data)
        self.region_uuid = region.id

    def ipam_address(self, address):
        """Create Interface Address object in core IPAM module.

        Args:
            address (str): IP Address.

        Returns:
            str: IP Address UUID.
        """
        ipam_addr = ip_addresses_attr.filter(address=address)
        ipam_address = False
        for addr in ipam_addr:
            tag1 = self.device_data.get("tags")
            tag2 = [i.slug for i in addr.tags]
            tag2.sort()
            tag1.sort()
            if address == addr.address.split("/")[0] and tag1 == tag2:
                ipam_address = addr
        data = dict(
            [
                ("address", address),
                ("status", "active"),
                ("tags", self.tag_uuid),
                ("assigned_object_type", "dcim.interface"),
                ("assigned_object_id", self.interface_uuid)
            ]
        )
        try:
            if not ipam_address:
                ipam_address = ip_addresses_attr.create(data)
            elif ipam_address.assigned_object_id != self.interface_uuid:
                ipam_address.update(data)
        except Exception as err:
            log.error(f"[{self.device_data.get('hostname')}] {address} : {err}")
        return ipam_address.id

    def slug_parser(self, name):
        """Slug name parser.

        Replace all special characters and space with "_" and covert to lower case.

        Args:
            name (str): Object name.

        Returns:
            str: Object name.
        """
        return name.replace(" ", "-").replace(".", "_").replace("*", "").replace("/", "_").lower()


class LB_VIP:
    """Create a Nautobot LB VIP Function client."""

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

    def main_fun(self):
        """Main function, initiated from nautobot_master.

        Validate if input vip info has all fields required to create Nautobot entry.
        Create partition and environment UUID, before initiating VIP function.
        """
        self.dport = self.vip_data.get("dport", 1)
        if all(x in list(self.vip_data) for x in VIP_FIELDS):
            if not self.vip_data.get("pool"):
                self.vip_data["pool"] = "UNKNOWN"
            if not self.vip_data.get("pool_mem"):
                self.vip_data["pool_mem"] = ["1.1.1.1"]
            try:
                if self.vip_data.get("cert"):
                    self.certificates()
                self.members()
                self.pool()
                self.vip_address()
                if self.check_pool():
                    if self.vip_data.get("partition"):
                        self.partition()
                    if self.vip_data.get("advanced_policies"):
                        self.policies()
                    self.environment()
                    self.vip()
            except Exception as err:
                log.error(f"[{self.vip_data.get('loadbalancer')}] {self.vip_data} : {err}")
        else:
            log.warning(f"[Missing VIP Fields][{self.vip_data.get('loadbalancer')}] {self.vip_data.get('name')} {list(self.vip_data)}")

    def check_pool(self):
        """Check if pool and cert exist and match."""
        vips = vip_attr.filter(name=self.vip_data.get("name"))
        for vip in vips:
            if (
                (vip.address == self.vip_addr_uuid)
                and (str(vip.port) == str(self.vip_data.get("port")))
                and (vip.protocol == self.vip_data.get("protocol"))
            ):
                if vip.pool == self.pool_uuid:
                    if self.vip_data.get("cert"):
                        if vip.certificates.sort() == self.certificates_uuid.sort():
                            return False
                    else:
                        return False
        return True

    def vip(self):
        """Create VIP object in VIP Plugin module."""
        vips = vip_attr.filter(name=self.vip_data.get("name"))
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
        for vip in vips:
            if (
                (vip.address == self.vip_addr_uuid)
                and (str(vip.port) == str(self.vip_data.get("port")))
                and (vip.protocol == self.vip_data.get("protocol"))
            ):
                log.debug("[VIP] Delete")
                vip.delete()
        try:
            vip_attr.create(data)
        except pynautobot.core.query.RequestError:
            log.warning(f"Duplicate VIP:Port [{self.vip_data.get('loadbalancer')}] {self.vip_data.get('address')}:{self.vip_data.get('port')}")
        except Exception as err:
            log.error(f"[2][{self.vip_data.get('loadbalancer')}] {self.vip_data} : {err}")

    ###########################################
    # VIP address functions
    ###########################################
    def vip_address(self):
        """Create VIP Address."""
        self.vip_addr_uuid = self.ipam_address(self.vip_data.get("address"))

    def environment(self):
        """Create Environment object in VIP Plugin module."""
        environment = environments_attr.get(name=self.vip_data.get("environment"))
        if not environment:
            data = {
                "name": self.vip_data.get("environment"),
                "slug": self.slug_parser(self.vip_data.get("environment")),
            }
            try:
                environment = environments_attr.create(data)
            except Exception as err:
                log.error(
                    f"[{self.vip_data.get('loadbalancer')}] {self.vip_data.get('name')} {self.vip_data.get('environment')} : {err}"
                )
        self.environment_uuid = environment.id

    def partition(self):
        """Create Partition object in VIP Plugin module."""
        partition = partitions_attr.get(slug=self.slug_parser(self.vip_data.get("partition")))
        if not partition:
            data = {"name": self.vip_data.get("partition"), "slug": self.slug_parser(self.vip_data.get("partition"))}
            try:
                partition = partitions_attr.create(data)
            except Exception as err:
                log.error(
                    f"[{self.vip_data.get('loadbalancer')}] {self.vip_data.get('name')} {self.vip_data.get('partition')} : {err}"
                )
        self.partition_uuid = partition.id

    def policies(self):
        """Create Policies object in VIP Plugin module."""
        adv_policies = []
        for policy in self.vip_data.get("advanced_policies"):
            policies = policies_attr.get(name=policy)
            if not policies:
                data = {"name": policy, "slug": self.slug_parser(policy)}
                try:
                    policies = policies_attr.create(data)
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
        for cert in self.vip_data.get("cert"):
            self.cert_parser(cert)
            # certificate = certificates_attr.get(name=self.cert_info.get("cn"))
            certificate = certificates_attr.get(slug=self.slug_parser(self.cert_info.get("cn")))
            self.cert_info
            self.cert_issuer()
            data = {
                "name": self.cert_info.get("cn"),
                "slug": self.slug_parser(self.cert_info.get("cn")),
                "exp": self.cert_info.get("exp", "2000-01-01T00:00"),
                "serial_number": self.cert_info.get("serial"),
                "issuer": self.cert_issuer_uuid,
                "cert_type": "RSA",
            }
            if certificate:
                try:
                    if data.get("serial_number") and len(data.get("serial_number")) > 8:
                        certificate.update(data)
                except Exception as err:
                    log.error(
                        f"[{self.vip_data.get('loadbalancer')}] {self.vip_data.get('name')} {cert.get('cert_cn')} : {err}"
                    )
            else:
                try:
                    certificate = certificates_attr.create(data)
                except Exception as err:
                    log.error(
                        f"[{self.vip_data.get('loadbalancer')}] {self.vip_data.get('name')} {cert.get('cert_cn')} : {err}"
                    )
            if certificate:
                cert_uuid.append(certificate.id)
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
        cert = {"serial": randint(100, 2000) if not cert_data.get("cert_serial") else cert_data.get("cert_serial")}
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
        issuer = issuer_attr.get(name=name)
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
                issuer = issuer_attr.create(data)
            except Exception as err:
                log.error(
                    f"[{self.vip_data.get('loadbalancer')}] {self.vip_data.get('name')} {self.cert_info['issuer'].get('CN')} : {err}"
                )
        self.cert_issuer_uuid = issuer.id

    def cert_organization(self):
        """Create Certificate Organization object in VIP Plugin module."""
        org = self.cert_info["issuer"].get("O", "UNKNOWN")
        organization = organization_attr.get(name=org)
        if not organization:
            data = {"name": org, "slug": self.slug_parser(org)}
            try:
                organization = organization_attr.create(data)
            except Exception as err:
                log.error(f"[{self.vip_data.get('loadbalancer')}] {self.vip_data.get('name')} {org} : {err}")
        self.cert_organization_uuid = organization.id

    ###########################################
    # Pool related functions
    ###########################################

    def pool(self):
        """Create Pool Member object in VIP Plugin module.

        Nautobot does not accept duplicate pool name, so create exception function.
        Function will only create, if existing pool name found, it will create new pool with DUP[no].
        ex: pool-abc-DUP1, where number will be incremented if there are more than 1 duplicate pool.
        """
        log.debug(f"VIP-Info : {self.vip_data} {self.members_uuid}")

        def pool_check(name):
            """Check if pool and pool member match."""
            pools = pools_attr.get(slug=self.slug_parser(name))
            if pools:
                mem1 = pools.members
                mem1.sort()
                mem2 = self.members_uuid
                mem2.sort()
                if mem1 == mem2:
                    log.debug("Found pool and member match")
                    return pools, True
                else:
                    log.debug("Found pool, but no member match")
                    return pools, False
            else:
                log.debug("No pool or member match")
                return False, False
        name = self.vip_data.get("pool")
        n = 0
        while True:
            pools, match = pool_check(name)
            if not pools:
                break
            elif pools and match:
                break
            else:
                n = n + 1
                name = f"{self.vip_data.get('pool')}-DUP{n}"
        data = {"name": name, "slug": self.slug_parser(name), "members": self.members_uuid}
        if not pools:
            try:
                pools = pools_attr.create(data)
            except Exception as err:
                log.error(
                    f"[{self.vip_data.get('loadbalancer')}] {self.vip_data.get('name')} {self.vip_data.get('pool')} : {err}"
                )
        self.pool_uuid = pools.id

    # def pool(self):
    #     """Create Pool Member object in VIP Plugin module."""
    #     pools = pools_attr.get(slug=self.slug_parser(self.vip_data.get("pool")))
    #     data = {
    #         "name": self.vip_data.get("pool"),
    #         "slug": self.slug_parser(self.vip_data.get("pool")),
    #         "members": self.members_uuid,
    #         # "tags": self.tag_uuid
    #     }
    #     if pools:
    #         pool = pools.update(data)
    #         if pool:
    #             log.debug(f"[Pool] Updated {self.vip_data.get('pool')}")
    #     else:
    #         try:
    #             pools = pools_attr.create(data)
    #         except Exception as err:
    #             log.error(
    #                 f"[{self.vip_data.get('loadbalancer')}] {self.vip_data.get('name')} {self.vip_data.get('pool')} : {err}"
    #             )
    #     self.pool_uuid = pools.id

    def members(self):
        """Create Pool Member object in VIP Plugin module."""
        members = []
        port = 1
        self.pool_mem_parser()
        for mem in self.pool_mem_info:
            mem_uuid = self.ipam_address(mem.get("address"))
            # We cannot have member with same name and address.
            # As work around, we are also checking if member exist by name.
            member = members_attr.get(address=mem_uuid)
            if not member:
                member = members_attr.get(name=mem.get("name"))
            if member:
                members.append(member.id)
            else:
                if "1.1.1.1" in str(mem.get("address")):
                    self.dport = self.dport + 1
                    port = self.dport
                data = {
                    "name": mem.get("name").replace("%", ""),
                    "slug": self.slug_parser(mem.get("name")),
                    "address": mem_uuid,
                    "port": port,
                    "tags": self.tag_uuid,
                }
                try:
                    member = members_attr.create(data)
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
                {"name": self.vip_data.get("pool_mem"), "address": self.vip_data.get("pool_mem"), }
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
        ipam_addr = ip_addresses_attr.filter(address=address)
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
                ipam_address = ip_addresses_attr.create(data)
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
        return name.replace(" ", "-").replace(".", "_").replace("*", "").replace("/", "_").replace("%", "_").replace("&", "").replace("(", "").replace(")", "").lower()
