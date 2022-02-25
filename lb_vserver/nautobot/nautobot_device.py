# pylint: disable=W1203, C0103, W0631, W0703
"""Nautobot REST API SDK."""

from nautobot.nautobot_attr import Device_ATTR
from helper.variables_nautobot import NAUTOBOT_DEVICE_REGION, NAUTOBOT_DEVICE_REGION_OFS
from helper.local_helper import log


class NB_Device(Device_ATTR):
    """Create a Nautobot Device Function client."""

    def __init__(self, device_data):
        """Initialize Nautobot Function Client.

        Args:
            device_data (dict): Device information in dict format.
        """
        self.device_data = device_data

    def device(self):
        """Check if device object exist in core Device module."""
        device = Device_ATTR.devices_attr.get(name=self.device_data.get("hostname"))
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
            device = Device_ATTR.devices_attr.create(data)
            self.device_uuid = device.id
            self.device_interface()
        self.device_uuid = device.id

    def device_interface(self):
        """Create Device Interface object in core Organization module."""
        interface = Device_ATTR.interfaces_attr.filter(device=self.device_data.get("hostname"))
        if interface:
            self.interface_uuid = interface[0].id
        else:
            data = {
                "device": self.device_uuid,
                "name": "Management",
                "type": "virtual",
                "enabled": True,
                "description": f"{self.device_data.get('hostname')} Management Interface",
            }
            interface = Device_ATTR.interfaces_attr.create(data)
            self.interface_uuid = interface.id
        self.device_interface_address()

    def device_interface_address(self):
        """Create Interface Address object in core Organization module."""
        self.mgmt_address_uuid = self.ipam_address(self.device_data.get("mgmt_address"))
        data = {"primary_ip4": self.mgmt_address_uuid, "tags": self.tag_uuid}
        device = Device_ATTR.devices_attr.get(name=self.device_data.get("hostname"))
        device.update(data)

    def device_role(self):
        """Create Device Role object in core Organization module."""
        device_role = Device_ATTR.device_roles_attr.get(name="load_balancer")
        if not device_role:
            data = {"name": "load_balancer", "slug": "load-balancer", "description": "F5 and Citrix LB role"}
            device_role = Device_ATTR.device_roles_attr.create(data)
        self.device_role_uuid = device_role.id

    def device_platforms(self):
        """Create Device Platform object in core Organization module."""
        name = "bigip" if "F5" in self.device_data.get("environment") else "netscaler"
        platform = Device_ATTR.platforms_attr.get(name=name)
        if not platform:
            self.manufacturers()
            data = {"name": name, "slug": name, "manufacturer": self.manufacturer_uuid}
            platform = Device_ATTR.platforms_attr.create(data)
        self.platform_uuid = platform.id

    def device_type(self):
        """Create Device Type object in core Organization module."""
        device_type = Device_ATTR.device_types_attr.get(slug=self.device_data.get("type").lower())
        if not device_type:
            self.manufacturers()
            data = {
                "manufacturer": self.manufacturer_uuid,
                "model": self.device_data.get("type"),
                "slug": self.slug_parser(self.device_data.get("type")),
            }
            device_type = Device_ATTR.device_types_attr.create(data)
        self.device_type_uuid = device_type.id

    def manufacturers(self):
        """Create manufacturer object in core Organization module."""
        manufacturer_name = "F5" if "F5" in self.device_data.get("environment") else "Citrix"
        manufacturer = Device_ATTR.manufacturers_attr.get(slug=self.slug_parser(manufacturer_name))
        if not manufacturer:
            data = {"name": manufacturer_name.upper(), "slug": self.slug_parser(manufacturer_name)}
            manufacturer = Device_ATTR.manufacturers_attr.create(data)
        log.info(manufacturer)
        self.manufacturer_uuid = manufacturer.id

    def tags(self):
        """Create tag object in core Organization module."""
        tag_uuid = []
        for tag_name in self.device_data.get("tags"):
            tag = Device_ATTR.tags_attr.get(slug=self.slug_parser(tag_name))
            if not tag:
                data = {"name": tag_name.upper(), "slug": self.slug_parser(tag_name)}
                tag = Device_ATTR.tags_attr.create(data)
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
        site = Device_ATTR.sites_attr.get(slug=self.slug_parser(self.site_info.get("site")))
        if not site:
            self.region()
            data = {
                "name": self.site_info.get("site"),
                "slug": self.slug_parser(self.site_info.get("site")),
                "status": "active",
                "region": self.region_uuid,
                "description": self.site_info.get("description", ""),
            }
            site = Device_ATTR.sites_attr.create(data)
        self.site_uuid = site.id

    def region(self):
        """Create Region object in core Organization module."""
        region = Device_ATTR.regions_attr.get(name=self.site_info.get("region"))
        if not region:
            data = {"name": self.site_info.get("region"), "slug": self.slug_parser(self.site_info.get("region"))}
            region = Device_ATTR.regions_attr.create(data)
        self.region_uuid = region.id

    def ipam_address(self, address):
        """Create Interface Address object in core IPAM module.

        Args:
            address (str): IP Address.

        Returns:
            str: IP Address UUID.
        """
        ipam_addr = Device_ATTR.ip_addresses_attr.filter(address=address)
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
                ("assigned_object_id", self.interface_uuid),
            ]
        )
        try:
            if not ipam_address:
                ipam_address = Device_ATTR.ip_addresses_attr.create(data)
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
